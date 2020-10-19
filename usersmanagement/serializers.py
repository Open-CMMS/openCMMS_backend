"""Serializers enable the link between front-end and back-end."""
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, update_last_login
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import Team, TeamType, UserProfile


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for our model UserProfile.

    Heritates from serializers.HyperlinkedModelSerializer and overrides :
        - create
        - update
    """

    class Meta:
        """Add metadata on the class."""

        model = UserProfile
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'nb_tries', 'is_active']
        # other fields available :
        # 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser'
        # 'last_login', 'date_joined', 'is_authenticated', 'is_anonymous'

    def create(self, validated_data):
        """Create and save a UserProfile into the database."""
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Update a UserProfile into the database."""
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserLoginSerializer(serializers.Serializer):
    """Serializer that implements the JWT authentication.

    Heritates from serializers.HyperlinkedModelSerializer and overrides :
        - validate
    """

    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    user_id = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """Validate the given data."""
        username = data.get("username", None)
        password = data.get("password", None)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                user.nb_tries = 0
                user.save()
                payload = JWT_PAYLOAD_HANDLER(user)
                jwt_token = JWT_ENCODE_HANDLER(payload)
                update_last_login(None, user)
                return {
                    'user': user,
                    'token': jwt_token,
                    'username': username,
                    'user_id': user.pk,
                    'is_blocked': False,
                }
        else:
            user = UserProfile.objects.get(username=username)
            if user is not None:
                if user.is_active:
                    user.nb_tries += 1
                    user.save()
                    if user.nb_tries == 3:
                        user.deactivate_user()
                        user.save()
                        raise serializers.ValidationError(
                            {
                                'is_blocked': (True),
                                'error': ("Mot de passe incorrect 3 fois de suite. Vous êtes bloqués."),
                                'user_id': (user.pk),
                            }
                        )
                    else:
                        raise serializers.ValidationError(
                            {
                                'is_blocked': (False),
                                'error': ("Mot de passe incorrect"),
                            }
                        )
                else:
                    raise serializers.ValidationError(
                        {
                            'is_blocked': (True),
                            'user_id': (user.pk),
                            'error': ("Vous vous êtes trompés trop de fois de mot de passe. Vous êtes bloqués."),
                        }
                    )

            raise serializers.ValidationError({
                'is_blocked': (False),
                'error': ("Login incorrect"),
            })


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for our Team model.

    Heritates from serializers.ModelSerializer.
    """

    class Meta:
        """Add metadata on the class."""

        model = Team
        fields = ['id', 'name', 'team_type', 'user_set']
        # other fields available :
        # 'permissions'


class TeamDetailsSerializer(serializers.ModelSerializer):
    """Serializer for our Team Details Serializer.

    Heritates from serializers.ModelSerializer
    """

    team_type_name = serializers.CharField(source='team_type.name')
    user_details = UserProfileSerializer(source='user_set', many=True)

    class Meta:
        """Add metadata on the class."""

        model = Team
        fields = ['id', 'name', 'team_type', 'user_set', 'team_type_name', 'user_details']


class ContentTypeSerializer(serializers.Serializer):
    """A little serializer used in the next one."""

    app_label = serializers.CharField(max_length=200)
    model = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)


class PermissionSerializer(serializers.Serializer):
    """A serializer to handle our permission system.

    Heritates from serializers.HyperlinkedModelSerializer and overrides :
        - create
        - update
    """

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    content_type = ContentTypeSerializer()
    codename = serializers.CharField(max_length=200)

    def create(self, validated_data):
        """Create and save a permission into the database."""
        name = validated_data.get('name')
        codename = validated_data.get('codename')
        content_type_data = validated_data.get('content_type')
        content_type = ContentType.objects.get(
            app_label=content_type_data['app_label'], model=content_type_data['model']
        )
        return Permission.objects.create(name=name, content_type=content_type, codename=codename)

    def update(self, instance, validated_data):
        """Update a permission into the database."""
        instance.name = validated_data.get('name', instance.name)
        instance.codename = validated_data.get('codename', instance.codename)
        instance.content_type.app_label = validated_data.get('content_type', instance.content_type)['app_label']
        instance.content_type.model = validated_data.get('content_type', instance.content_type)['model']
        instance.save()
        return instance


class TeamTypeSerializer(serializers.ModelSerializer):
    """A serializer to handle our TeamType model.

    Heritates from serializers.HyperlinkedModelSerializer and overrides :
        - update
    """

    class Meta:
        """Add metadata on the class."""

        model = TeamType
        fields = ['id', 'name', 'perms', 'team_set']

    def update(self, instance, validated_data):
        """Update a TeamType into the database."""
        teams = instance.team_set.all()

        for attr, value in validated_data.items():
            if attr == 'team_set':
                for t in teams:
                    if t not in value:
                        t.delete()
                instance.team_set.set(value)
            elif attr == 'perms':
                instance.perms.set(value)
                instance._apply_()
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class TeamTypeDetailsSerializer(serializers.ModelSerializer):
    """A serializer to handle our TeamType model for GET details view.

    Heritates from serializers.ModelSerializer
    """

    team_set = TeamSerializer(many=True)
    perms = PermissionSerializer(many=True)

    class Meta:
        """Add metadata on the class."""

        model = TeamType
        fields = ['id', 'name', 'perms', 'team_set']
