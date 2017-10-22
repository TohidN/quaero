from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import AccountSignup, Profile


class AccountSignupInline(admin.StackedInline):
	model = AccountSignup
	max_num = 1

class ProfileInline(admin.StackedInline):
	model = Profile
	max_num = 1


class AccountAdmin(UserAdmin):
	inlines = [AccountSignupInline, ProfileInline, ]


# Register your models here.
try:
	admin.site.unregister(get_user_model())
except admin.sites.NotRegistered:
	pass
admin.site.register(get_user_model(), AccountAdmin)
