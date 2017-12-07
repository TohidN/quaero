from urllib.parse import urlparse, urljoin
from quaero.models import Site, Page, Link


class Crawler(object):
	def __init__(self, url, depth, external=False):
		parse = urlparse(url)
		self.url = url
		self.depth = depth
		self.external = external

		self.site = parse.netloc
		# remove "/" at the end of site's url
		if self.site[-1:] == "/":
			self.site = self.site[:-1]

		self.sites = {}
		self.urls = []
		self.links = 0
		self.followed = 0
		self.crawl(url, self.depth)

	def enqueue(self, url):
		pass

	def crawl(self, link_url, depth=1):
		parse = urlparse(link_url)
		site_url = parse.netloc
		path = parse.path
		# remove "/" at the end of site's url
		if site_url[-1:] == "/":
			site_url = site_url[:-1]
		# if path starts with "./" remove it from beginning of the path
		if path[0:2] == "./":
			path = path[1:]
		# Create or find site
		if site_url in self.sites:
			site = self.sites[site_url]
		else:
			try:
				site = Site.objects.get(site_url=site_url)
			except Site.DoesNotExist:
				site = Site(site_url=site_url)
				# Site already exists, so just update it's robots.txt file
				site.update_robot()
				site.save()
			self.sites[site_url] = site
		# Create or find page
		try:
			page = Page.objects.get(site=site, path=path)
		except Page.DoesNotExist:
			page = Page(site=site, path=path)
			page.save()
		# Scrap for content and links
		soup = page.scrap()
		# Quit if we reached maximum depth, and we are allowed to scrap the page
		if depth > 1 and soup is not False:
			# list all links's pk in this page, so we can remove the ones that are removed in page edits
			existing_links = []
			# find and store all links
			for link in soup.find_all('a'):
				link_url = link.get('href')
				link_title = link.get("title")
				link_rel = link.get('rel')
				link_content = link.contents[0]

				# try to get site url and path
				link_parse = urlparse(link_url)
				link_path = link_parse.path
				link_scheme = "http" if link_parse.scheme is None or link_parse.scheme is "" else link_parse.scheme
				link_site = page.site.site_url if link_parse.netloc is None or link_parse.netloc is "" else link_parse.netloc
				link_site_url = "{}://{}".format(link_scheme, link_site)
				# if site url didn't exist, then it's a relative link. so generate absolute link
				if link_site_url == "":
					link_site_url = page.get_url()
				# now that we have an absolute link, separate site's home url and path
				link_url = urljoin(link_site_url, link_path)
				link_parse = urlparse(link_url)
				link_path = link_parse.path
				link_site_url = link_parse.netloc

				# Improve link's site and path values
				#  if link_site_url[-1:] == "/":
				#  	link_site_url = link_site_url[:-1]
				#  if link_site_url == "":
				#  	link_site_url = site.site_url
				#  if link_path[0:2] == "./":
				#  	link_path = link_path[1:]
				#  if link_path == "":
				#  	link_path = "/"
				#  if link_path[0:1] is not "/":
				#  	link_path = "/{}".format(link_path)

				# if it's not an external link or externals can be crawled,
				# and it's not already crawled using this crawl task then crawl them
				if (link_site_url == self.site or self.external is True) and link_url not in self.urls:
					self.links += 1
					self.urls.append(link_url)
					# create ore find a link between this page and link's reference page
					try:
						link = Link.objects.get(to_url__site__site_url=link_site_url, to_url__page__path=link_path, from_url=page)
					except:
						target_site = Site.objects.get_or_create(site_url=link_site_url)[0]
						target_page = Page.objects.get_or_create(path=link_path, site=target_site)[0]
						link = Link.objects.get_or_create(from_url=page, to_url=target_page)[0]
					# update link's rel and title
					if link.title is not link_title or link.rel is not link_rel:
						link.title = link_title
						link.rel = link_rel
						link.text = link_content
						link.save()
					# creating a list of existing links on page, later links which are removed during page edit will be removed
					existing_links.append(link.pk)
					# crawl if link's relationship is is not marked as "no follow"
					nofollow = False
					if link_rel is not None and isinstance(link_rel, list):
						for rel in link_rel:
							if rel.lower().find("nofollow") != -1:
								nofollow = True
					if nofollow is False:
						crawl_url = link.to_url.get_url()
						print("Crawling: {}\ndepth: {}\nrel: {}".format(crawl_url, depth, link_rel))
						self.crawl(crawl_url, depth-1)
				else:
					print("didn't proceed with scrapping: {}", link.get('href'))
			# delete * from Link if from_url!=url
			Link.objects.exclude(pk__in=existing_links).delete()
		pass
