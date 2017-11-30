"""DjangoBoilerplate URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.flatpages import views

from account.views import signup, signin, signout, activate, profile, profile_edit, account_edit, settings_edit, profile_list
from quaero.views import site_list, site_pages_list, site_page

urlpatterns = [
	# home
	url(r'^$', site_list, name="home"),
	# Quaero
	url(r'^sites$', site_list, name="site-list"),
	url(r'^pages/(?P<site_url>.*?)$', site_pages_list, name="site-pages-list"),
	url(r'^page/(?P<url>.*?)$', site_page, name="page"),
	# admin
	url(r'^admin/', admin.site.urls, name='admin'),
	# User Accounts
	url(r'^signup/$', signup, name='signup'),
	url(r'^login/$', signin, name='signin'),
	url(r'^logout/$', signout, {'next_page': '/'}, name='signout'),
	url(r'^activate/(?P<activation_key>\w+)/$', activate, name='activate'),
	url(r'^activate/retry/(?P<activation_key>\w+)/$', activate, name='activate_retry'),
	url(r'^activate_success/$', activate, name='activate_success'),
	url(r'^profile/(?P<username>[-\w]+)$', profile, name="profile"),
	url(r'^profile/(?P<username>[-\w]+)/edit-account$', account_edit, name="account_edit"),
	url(r'^profile/(?P<username>[-\w]+)/edit-profile$', profile_edit, name="profile_edit"),
	url(r'^profile/(?P<username>[-\w]+)/edit-settings$', settings_edit, name="user_settings_edit"),
	url(r'^profiles/$', profile_list, name="profile_list"),
	# all the pages
	url(r'^(?P<slug>[-\w]+)$', views.flatpage),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)