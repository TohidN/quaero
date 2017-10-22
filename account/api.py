from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializer import UserSerializer, GroupSerializer, ProfileSerializer
from .models import Profile


class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all().order_by('-date_joined')
	serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer


class GroupViewSet(viewsets.ModelViewSet):
	queryset = Group.objects.all()
	serializer_class = GroupSerializer
