from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission, update_last_login
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import Team, TeamType, UserProfile

"""
Serializers enable the link between front-end and back-end
"""


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "nb_tries",
            "is_active",
        ]
        # other fields available :
        # 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'is_authenticated', 'is_anonymous'

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    user_id = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)
        user = authenticate(username=username, password=password)
        # user = UserProfile.objects.get(username=username)
        if user != None:
            if user.is_active:
                user.nb_tries = 0
                user.save()
                payload = JWT_PAYLOAD_HANDLER(user)
                jwt_token = JWT_ENCODE_HANDLER(payload)
                update_last_login(None, user)
                return {
                    "user": user,
                    "token": jwt_token,
                    "username": username,
                    "user_id": user.pk,
                    "is_blocked": False,
                }
        else:
            user = UserProfile.objects.get(username=username)
            if user != None:
                if user.is_active:
                    user.nb_tries += 1
                    user.save()
                    if user.nb_tries == 3:
                        user.deactivate_user()
                        user.save()
                        raise serializers.ValidationError(
                            {
                                "is_blocked": (True),
                                "error": (
                                    "Mot de passe incorrect 3 fois de suite. Vous êtes bloqués."
                                ),
                                "user_id": (user.pk),
                            }
                        )
                    else:
                        raise serializers.ValidationError(
                            {"is_blocked": (False), "error": ("Mot de passe incorrect")}
                        )
                else:
                    raise serializers.ValidationError(
                        {
                            "is_blocked": (True),
                            "user_id": (user.pk),
                            "error": (
                                "Vous vous êtes trompés trop de fois de mot de passe. Vous êtes bloqués."
                            ),
                        }
                    )

            raise serializers.ValidationError(
                {"is_blocked": (False), "error": ("Login incorrect")}
            )


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "team_type", "user_set"]
        # other fields available :
        # 'permissions'


class ContentTypeSerializer(serializers.Serializer):
    app_label = serializers.CharField(max_length=200)
    model = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    content_type = ContentTypeSerializer()
    codename = serializers.CharField(max_length=200)

    def create(self, validated_data):
        name = validated_data.get("name")
        codename = validated_data.get("codename")
        content_type_data = validated_data.get("content_type")
        content_type = ContentType.objects.get(
            app_label=content_type_data["app_label"], model=content_type_data["model"]
        )
        return Permission.objects.create(
            name=name, content_type=content_type, codename=codename
        )

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.codename = validated_data.get("codename", instance.codename)
        instance.content_type.app_label = validated_data.get(
            "content_type", instance.content_type
        )["app_label"]
        instance.content_type.model = validated_data.get(
            "content_type", instance.content_type
        )["model"]
        instance.save()
        return instance


class TeamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamType
        fields = ["id", "name", "perms", "team_set"]

    def update(self, instance, validated_data):
        teams = instance.team_set.all()

        for attr, value in validated_data.items():
            if attr == "team_set":
                for t in teams:
                    if t not in value:
                        t.delete()
                instance.team_set.set(value)
            elif attr == "perms":
                instance.perms.set(value)
                instance._apply_()
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
