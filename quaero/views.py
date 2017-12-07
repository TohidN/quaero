from itertools import chain

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from urllib.parse import urlparse

from .models import Site, Page, ImageDetail, Image


def search_home(request):
	return render(request, "search-home.html")


def search_result(request):
	query = request.GET.get('q')
	search_type = request.GET.get('t')

	if search_type == "images":
		# Search Image Tags
		results1 = ImageDetail.objects.filter(
			Q(title__icontains=query) | Q(alt__icontains=[query])
		)
		# Get images located in related pages
		results2 = ImageDetail.objects.filter(
			Q(page__page_title__icontains=query) | Q(page__article_keywords__icontains=[query]) |
			Q(page__article_title__icontains=query) | Q(page__article_content__icontains=query)
		)
		# sort and add more popular images at top
		images = {}
		results = []
		#top_results = button_results = set()
		for item in chain(results1, results2):
			item_url = item.image.get_url()
			if item_url in images:
				if item in results1:
					images[item_url]['rank'] += 10
				if item in results2:
					images[item_url]['rank'] += 1
			else:
				rank = 1
				if item in results1:
					rank += 10
				if item in results2:
					rank += 1
				images[item_url] = {'image': item, 'rank': rank}
		sorted_images = sorted(images, key=lambda x: x[rank])
		for item in sorted_images:
			results.append(images[item]['image'])
		# Merge two results
		#results = list(chain(top_results, button_results))
		count = len(results)

		page = request.GET.get('page', 1)
		paginator = Paginator(results, 20)
		adjacent_pages = 5
		page = int(page)
		start_page = max(page - adjacent_pages, 1)
		if start_page <= 3: start_page = 1
		end_page = page + adjacent_pages + 1
		if end_page >= paginator.num_pages - 1: end_page = paginator.num_pages + 1
		try:
			results = paginator.page(page)
		except PageNotAnInteger:
			results = paginator.page(1)
		except EmptyPage:
			results = paginator.page(paginator.num_pages)

		context = {
			'query': query,
			'results': results,
			'count': count,
			'paginator_range': range(start_page, end_page),
		}
		return render(request, "search-image-result.html", context)
	else:
		results = Page.objects.filter(
			Q(page_title__icontains=query) | Q(article_keywords__icontains=[query]) |
			Q(article_title__icontains=query) | Q(article_content__icontains=query)
		)
		count = results.count()

		page = request.GET.get('page', 1)
		paginator = Paginator(results, 20)
		adjacent_pages = 5
		page = int(page)
		start_page = max(page - adjacent_pages, 1)
		if start_page <= 3: start_page = 1
		end_page = page + adjacent_pages + 1
		if end_page >= paginator.num_pages - 1: end_page = paginator.num_pages + 1
		try:
			results = paginator.page(page)
		except PageNotAnInteger:
			results = paginator.page(1)
		except EmptyPage:
			results = paginator.page(paginator.num_pages)

		context = {
			'query': query,
			'results': results,
			'count': count,
			'paginator_range': range(start_page, end_page),
		}
		return render(request, "search-result.html", context)

def site_list(request):
	sites = Site.objects.order_by('-site_url').all()

	page = request.GET.get('page', 1)
	paginator = Paginator(sites, 20)
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


def site_pages_list(request, site_url):
	site_pages = Page.objects.filter(site__site_url=site_url).order_by('-path')

	page = request.GET.get('page', 1)
	paginator = Paginator(site_pages, 20)
	adjacent_pages = 5
	page = int(page)
	start_page = max(page - adjacent_pages, 1)
	if start_page <= 3: start_page = 1
	end_page = page + adjacent_pages + 1
	if end_page >= paginator.num_pages - 1: end_page = paginator.num_pages + 1
	try:
		site_pages = paginator.page(page)
	except PageNotAnInteger:
		site_pages = paginator.page(1)
	except EmptyPage:
		site_pages = paginator.page(paginator.num_pages)

	context = {
		'site_url': site_url,
		'site_pages': site_pages,
		'paginator_range': range(start_page, end_page),
	}
	return render(request, "site-pages-list.html", context)


def site_page(request, url):
	parse = urlparse("//{}".format(url))
	site_url = parse.netloc
	path = parse.path
	# remove "/" at the end of site's url
	if site_url[-1:] == "/":
		site_url = site_url[:-1]
	# if path starts with "./" remove it from beginning of the path
	if path[0:2] == "./":
		path = path[1:]

	page = get_object_or_404(Page, site__site_url=site_url, path=path)
	page_images = ImageDetail.objects.filter(page=page)
	context = {
		'page': page,
		'page_images': page_images,
	}
	return render(request, "page.html", context)

