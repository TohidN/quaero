from django.contrib.auth.models import UserManager
from django.contrib.auth import get_user_model
from django.utils.six import text_type
from django.utils.encoding import smart_text
from django.utils import timezone
from .modules.functions import generate_sha1
import account.settings as account_settings

import re
SHA1_RE = re.compile('^[a-f0-9]{40}$')

class AccountManager(UserManager):
	""" Account model to handle registration process. """
	def create_user(self, username, email, password, active=False, send_email=True):
		new_user = get_user_model().objects.create_user(
			username, email, password)
		new_user.is_active = active
		new_user.save()

		account = self.create_account(new_user)

		if send_email:
			account.send_activation_email()

		return new_user

	def create_account(self, user):
		"""
		Creates an :class:`AccountSignup` instance for this user.

		:param user:
			Django :class:`User` instance.

		:return: The newly created :class:`AccountSignup` instance.

		"""
		if isinstance(user.username, text_type):
			user.username = smart_text(user.username)
		salt, activation_key = generate_sha1(user.username)

		try:
			account = self.get(user=user)
		except self.model.DoesNotExist:
			account = self.create(user=user, activation_key=activation_key)
		return account

	def reissue_activation(self, activation_key):
		"""
		Creates a new ``activation_key`` resetting activation timeframe when
		users let the previous key expire.

		:param activation_key:
			String containing the secret SHA1 activation key.

		"""
		try:
			signedup_user = self.get(activation_key=activation_key)
		except self.model.DoesNotExist:
			return False
		try:
			salt, new_activation_key = generate_sha1(signedup_user.user.username)
			signedup_user.activation_key = new_activation_key
			signedup_user.save(using=self._db)
			signedup_user.user.date_joined = timezone.now()
			signedup_user.user.save(using=self._db)
			signedup_user.send_activation_email()
			return True
		except:
			return False

	def activate_user(self, activation_key):
		"""
		Activate an :class:`User` by supplying a valid ``activation_key``.
		"""
		if SHA1_RE.search(activation_key):
			try:
				signedup_user = self.get(activation_key=activation_key)
			except self.model.DoesNotExist:
				return False
			if not signedup_user.activation_key_expired():
				signedup_user.activation_key = account_settings.ACTIVATED_TEXT
				user = signedup_user.user
				user.is_active = True
				signedup_user.save(using=self._db)
				user.save(using=self._db)
				return user
		return False

	def check_expired_activation(self, activation_key):
		"""
		Check if ``activation_key`` is still valid.
		"""
		if SHA1_RE.search(activation_key):
			signedup_user = self.get(activation_key=activation_key)
			return signedup_user.activation_key_expired()
		raise self.model.DoesNotExist

	def confirm_email(self, confirmation_key):
		"""
		Confirm an email address by checking a ``confirmation_key``.
		"""
		if SHA1_RE.search(confirmation_key):
			try:
				signedup_user = self.get(email_confirmation_key=confirmation_key, email_unconfirmed__isnull=False)
			except self.model.DoesNotExist:
				return False
			else:
				user = signedup_user.user
				old_email = user.email
				user.email = signedup_user.email_unconfirmed
				signedup_user.email_unconfirmed, signedup_user.email_confirmation_key = '',''
				signedup_user.save(using=self._db)
				user.save(using=self._db)

				return user
		return False

	def delete_expired_users(self):
		"""
		Checks for expired users and delete's the ``User`` associated with
		it. Skips if the user ``is_staff``.
		"""
		deleted_users = []
		for user in get_user_model().objects.filter(is_staff=False, is_active=False):
			if user.AccountSignup.activation_key_expired():
				deleted_users.append(user)
				user.delete()
		return deleted_users
