"""
This model is used to handle registration related features such as email confirmation
"""
import datetime, os
from django.utils import timezone
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.signals import post_save
from django.utils import timezone, translation, six
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import get_thumbnail
from .modules.functions import generate_sha1


import account.settings as profile_settings
from .modules.language_country import COUNTRIES, LANGUAGES
from .modules.mail import send_mail
from .managers import AccountManager
from .utils import get_gravatar

# used to get dynamic directory based on user's id
def get_avatar_photo_path(instance, filename):
	name, ext = os.path.splitext(filename)
	filename = 'avatar{}'.format(ext)
	salt, hash = generate_sha1(instance.user.username, instance.user.pk)
	return "avatar/{0}/{1}".format(hash, filename)


class AccountSignup(models.Model):
	user = models.OneToOneField('auth.user', verbose_name=_('user'))
	last_active = models.DateTimeField(_('last active'), blank=True, null=True)
	activation_key = models.CharField(_('activation key'), max_length=40, blank=True)
	activation_notification_send = models.BooleanField(_('notification send'), default=False)
	email_unconfirmed = models.EmailField(_('unconfirmed email address'), blank=True)
	email_confirmation_key = models.CharField(_('unconfirmed email verification key'), max_length=40, blank=True)
	email_confirmation_key_created = models.DateTimeField(_('creation date of email confirmation key'), blank=True, null=True)
	objects = AccountManager()

	class Meta:
		verbose_name = _('registration')
		verbose_name_plural = _('registrations')

	def __str__(self):
		return '%s' % self.user.username

	def change_email(self, email):
		"""
		Changes the email address for a user.
		A user needs to verify this new email address before it becomes
		active. By storing the new email address in a temporary field --
		``temporary_email`` -- we are able to set this email address after the
		user has verified it by clicking on the verification URI in the email.
		This email gets send out by ``send_verification_email``.
		
		:param email: The new email address that the user wants to use.
		"""
		from .modules.functions import generate_sha1
		self.email_unconfirmed = email
		salt, hash = generate_sha1(self.user.username)
		self.email_confirmation_key = hash
		self.email_confirmation_key_created = timezone.now()
		self.save()
		# Send email for activation
		self.send_confirmation_email()

	def send_confirmation_email(self):
		"""
		Sends an email to confirm the new email address.
		"""
		context = {'user': self.user,
					'new_email': self.email_unconfirmed,
					'protocol': settings.DEFAULT_PROTOCOL,
					'confirmation_key': self.email_confirmation_key,
					'site': Site.objects.get_current()}

		mailer = ConfirmationMail(context=context)
		mailer.generate_mail("confirmation", "_old")

		if self.user.email:
			mailer.send_mail(self.user.email)

		mailer.generate_mail("confirmation", "_new")
		mailer.send_mail(self.email_unconfirmed)

	def activation_key_expired(self):
		"""
		Checks if activation key is expired.
		Returns ``True`` when the ``activation_key`` of the user is expired and
		``False`` if the key is still valid.
		"""
		expiration_days = datetime.timedelta(profile_settings.ACTIVATION_DAYS)
		expiration_date = self.user.date_joined + expiration_days
		if self.activation_key == profile_settings.ACTIVATED_TEXT:
			return True
		if timezone.now() >= expiration_date:
			return True
		return False

	def send_activation_email(self):
		"""
		Sends a activation email to the user.
		This email is send when the user wants to activate their newly created
		user.
		"""
		context = {'user': self.user,
					'protocol': settings.DEFAULT_PROTOCOL,
					'activation_days': profile_settings.ACTIVATION_DAYS,
					'activation_key': self.activation_key,
					'site': Site.objects.get_current()}

		mailer = ConfirmationMail(context=context)
		mailer.generate_mail("activation")
		mailer.send_mail(self.user.email)


class ConfirmationMail(object):
	_message_txt = 'emails/{0}_email_message{1}.txt'
	_message_html = 'emails/{0}_email_message{1}.html'
	_subject_txt = 'emails/{0}_email_subject{1}.txt'

	def __init__(self, context):
		self.context = context

	def generate_mail(self, type_mail, version=""):
		self.type_mail = type_mail
		self.message_txt = self._message_txt.format(type_mail, version)
		self.message_html = self._message_html.format(type_mail, version)
		self.subject_txt = self._subject_txt.format(type_mail, version)
		self.subject = self._subject()
		self.message_html = self._message_in_html()
		self.message = self._message_in_txt()

	def send_mail(self, email):
		send_mail(self.subject, self.message,
				  self.message_html, settings.DEFAULT_FROM_EMAIL,
				  [email])

	def _message_in_html(self):
		if settings.EMAIL_FORMAT_HTML:
			return render_to_string(self.message_html, self.context)
		return None

	def _message_in_txt(self):
		if not settings.EMAIL_FORMAT_HTML or not self.message_html:
			return render_to_string(self.message_txt, self.context)
		return None

	def _subject(self):
		subject = render_to_string(self.subject_txt, self.context)
		subject = ''.join(subject.splitlines())
		return subject


class Profile(models.Model):
	GENDER_CHOICES = (
		('n', 'None'),
		('m', 'Male'),
		('f', 'Female'),
	)
	PRIVACY_CHOICES = (
		('o', 'Everyone'),
		('f', 'Friends'),
		('p', 'Private'),
	)
	AVATAR_CHOICES = (
		('g', 'Gravatar'),
		('n', 'None'),
		('u', 'Upload Image'),
	)
	NOTIFICATION_SETTINGS = (
		('n', 'Don\'t send notifications'),
		('d', 'Daily notifications'),
		('m', 'Monthly notifications'),
	)

	user = models.OneToOneField(User, related_name='user')
	avatar_option = models.CharField(_('Avatar Option'), max_length=1, choices=AVATAR_CHOICES, default='g')
	avatar = models.ImageField(_('If you chose "Upload Image" as avatar option this image will be used.'), upload_to=get_avatar_photo_path, blank=True, null=True)
	website = models.URLField(_('Website'), default='', blank=True, null=True)
	bio = models.TextField(_('Bio'), default='', blank=True, null=True)
	language = models.CharField(_('Choose Language'), max_length=3, choices=LANGUAGES, blank=True, null=True)
	country = models.CharField(_('Choose Country'), max_length=2, choices=COUNTRIES, blank=True, null=True)
	location = models.CharField(_('Location'), max_length=140, blank=True, null=True)
	gender = models.CharField(_('Gender'), max_length=1, default='n', choices=GENDER_CHOICES)

	public_mail = models.EmailField(blank=True, null=True, verbose_name=_('Public Mail: You can add a public email to your profile!'))
	privacy = models.CharField(max_length=1, choices=PRIVACY_CHOICES, verbose_name=_('Choose who can see your profile and favorites.'))
	notification_setting = models.CharField(_('Email Notifications'), max_length=1, choices=NOTIFICATION_SETTINGS, default='g')

	def get_full_name(self):
		"""
		Returns the full name of the user, or if none is supplied will return the username.
		"""
		user = self.user
		if user.first_name or user.last_name:
			name = "{0} {1}".format(user.first_name, user.last_name)
		else:
			name = user.username
		return name.strip()

	def get_avatar_url(self, size=256, crop='center', quality=100):
		"""
		Returns the avatar image based on user's settings
		"""
		if self.avatar_option == 'n':
			return False
		elif self.avatar_option == 'g':
			return get_gravatar(self.user.email, size)
		elif self.avatar_option == 'u':
			im = get_thumbnail(self.avatar, "{0}x{0}".format(size), crop=crop, quality=quality)
			current_site = Site.objects.get_current()
			return "{0}files/{1}".format(Site.objects.get_current(), im.name)
		return profile_settings.DEFAULT_AVATAR_URL

	def __str__(self):
		return self.user.username


def create_profile(sender, **kwargs):
	"""
	Create a user profile for each User
	Set permissions to edit and view profile
	"""
	user = kwargs["instance"]
	if kwargs["created"]:
		user_profile = Profile(user=user)
		user_profile.save()
post_save.connect(create_profile, sender=User)


class AnonymousAccount(object):
	def __init__(self, request=None):
		self.user = AnonymousUser()
		self.timezone = settings.TIME_ZONE
		if request is None:
			self.language = settings.LANGUAGE_CODE
		else:
			self.language = translation.get_language_from_request(request, check_path=True)

	def __str__(self):
		return "AnonymousAccount"
