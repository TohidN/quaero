from django.utils.http import urlencode
from hashlib import md5


def get_gravatar(email, size=80, default='identicon'):
	""" Get's a Gravatar for a email address.
	:param email:
		used to get gravatar url
	:param size:
		The size in pixels of one side of the Gravatar's square image.
		Optional, if not supplied will default to ``80``.

	:param default:
		Defines what should be displayed if no image is found for this user.
		Optional argument which defaults to ``identicon``. The argument can be
		a URI to an image or one of the following options:

			``404``
				Do not load any image if none is associated with the email
				hash, instead return an HTTP 404 (File Not Found) response.

			``mm``
				Mystery-man, a simple, cartoon-style silhouetted outline of a
				person (does not vary by email hash).

			``identicon``
				A geometric pattern based on an email hash.

			``monsterid``
				A generated 'monster' with different colors, faces, etc.

			``wavatar``
				Generated faces with differing features and backgrounds

	:return: The URI pointing to the Gravatar.
	"""
	# base_url = 'https://secure.gravatar.com/avatar/'
	base_url = 'https://www.gravatar.com/avatar/'
	gravatar_url = '{0}{1}'.format(base_url, md5(email.lower().encode('utf-8')).hexdigest())

	gravatar_url += urlencode({
		's': str(size),
		'd': default
	})
	return gravatar_url
