from rest_framework import serializers
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from .models import UserProfile, TeamType, Team

"""
Serializers enable the link between front-end and back-end
"""


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'nb_tries', 'is_active']
        #other fields available :
        # 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'is_authenticated', 'is_anonymous'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance




class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'team_type']
        #other fields available :
        # 'permissions'


class ContentTypeSerializer(serializers.Serializer):
    app_label = serializers.CharField(max_length=200)
    model = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)




class PermissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    content_type = ContentTypeSerializer()
    codename = serializers.CharField(max_length=200)

    def create(self,validated_data):
        name = validated_data.get('name')
        codename = validated_data.get('codename')
        content_type_data = validated_data.get('content_type')
        content_type = ContentType.objects.get(app_label=content_type_data['app_label'],
                                               model = content_type_data['model'])
        return Permission.objects.create(name=name,content_type=content_type,codename=codename)

    def update(self,instance,validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.codename = validated_data.get('codename', instance.codename)
        instance.content_type.app_label=validated_data.get('content_type',instance.content_type)['app_label']
        instance.content_type.model=validated_data.get('content_type', instance.content_type)['model']
        instance.save()
        return instance




class TeamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamType
        fields = ['id','name','perms','team_set']
