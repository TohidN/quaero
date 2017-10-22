from django import template
from account.models import Profile
from sorl.thumbnail import get_thumbnail

register = template.Library()


@register.simple_tag(takes_context=True)
def logged_in_user_avatar(context, size="200x200",):
	"""
	:return user's profile avatar
	"""
	if context['request'].user.is_authenticated:
		profile = Profile.objects.get(user=context['request'].user)
		avatar = profile.get_avatar_url(size=128)
		im = get_thumbnail(avatar, "128x128", crop='center', quality=99)
		return "/files/{}".format(im.name)
		return avatar
	else:
		return False


@register.filter(name='field_type')
def field_type(field):
	"""
	Get form field's type, usage:
	{{form.field_name|field_type}}
	:return: charfield, urlfield, typedchoicefield, imagefield, emailfield ...
	"""
	return field.field.widget.__class__.__name__

