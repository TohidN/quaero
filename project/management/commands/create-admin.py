from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
	help = 'create admin'

	def handle(self, *args, **options):
		try:
			user = User.objects.get(username='admin')
			user.delete()
			print("Admin already existed. it's removed now.")
		except User.DoesNotExist:
			pass

		user = User.objects.create_user('admin', password='admin')
		user.is_superuser = True
		user.is_staff = True
		user.save()
		print("Admin is created.")
