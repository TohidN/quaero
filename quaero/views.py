from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .models import Site


def site_list(request):
	sites = Site.objects.order_by('-site_url').all()

	page = request.GET.get('page', 1)
	paginator = Paginator(sites, 10)
	adjacent_pages = 5
	page = int(page)
	start_page = max(page - adjacent_pages, 1)
	if start_page <= 3: start_page = 1
	end_page = page + adjacent_pages + 1
	if end_page >= paginator.num_pages - 1: end_page = paginator.num_pages + 1
	try:
		sites = paginator.page(page)
	except PageNotAnInteger:
		sites = paginator.page(1)
	except EmptyPage:
		sites = paginator.page(paginator.num_pages)

	context = {
		'sites': sites,
		'paginator_range': range(start_page, end_page),
	}
	return render(request, "site-list.html", context)


