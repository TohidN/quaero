import itertools
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_bytes
from hashlib import sha1
import random


def get_slug(obj, title, group):
	"""
	used to get unique slugs
	:param obj: Model Object
	:param title: Title to create slug from
	:param group: Model Class
	:return: Model object with unique slug
	"""
	if obj.pk is None:
		obj.slug = slug_orig = slugify(title)
		for x in itertools.count(1):
			if not group.objects.filter(slug=obj.slug).exists() and obj.slug is not None:
				break
			obj.slug = '%s-%d' % (slug_orig, x)
	return obj


def generate_sha1(string, salt=None):
	"""
	:param string: The string that needs to be encrypted.
	:param salt: Optionally define your own salt. If none is supplied, will use a random string of 5 characters.
	:return: Tuple containing the salt and hash.
	"""

	string = str(string)
	if not salt:
		salt = sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]

	salted_bytes = (smart_bytes(salt) + smart_bytes(string))
	hash_ = sha1(salted_bytes).hexdigest()

	return salt, hash_
