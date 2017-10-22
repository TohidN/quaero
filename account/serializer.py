from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		exclude = ('password',)


class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = Profile
		fields = '__all__'
