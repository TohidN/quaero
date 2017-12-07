from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField, HStoreField, JSONField

import io
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from newspaper import Article

from project import settings
import requests
from bs4 import BeautifulSoup


class Site(models.Model):
	site_url = models.CharField(_('Site Url'), max_length=1024, db_index=True, unique=True, blank=False)
	robots = models.CharField(max_length=4096, blank=True, null=True)  # content of robots.txt read by update_robot()
	robots_status = models.PositiveSmallIntegerField(blank=True, null=True)  # content of robots.txt read by update_robot()
	created = models.DateTimeField(_('first searched'), auto_now_add=True, blank=True, null=True)
	last_crawled = models.DateTimeField(_('last crawled'), auto_now=True, blank=True, null=True)
	status = models.CharField(max_length=1, default='A', choices=(
		('A', "Active"),
		('B', "Temporarily Blocked"),
		('S', "Spam site"),
	))

	meta = JSONField(blank=True, null=True)

	def __str__(self):
		return self.site_url

	def update_robot(self):
		url = "{}/robots.txt".format( self.get_url() )
		try:
			response = requests.get(url, headers={'User-Agent': settings.USER_AGENT})
		except (requests.ConnectTimeout, requests.HTTPError, requests.ReadTimeout, requests.Timeout, requests.ConnectionError):
			return
		if response.status_code == 200:
			self.robots = response.text
		self.robots_status = response.status_code
		self.save()

	def get_url(self):
		parse = urlparse(self.site_url)
		if parse.scheme is "":
			parse = urlparse("http://{}".format(self.site_url))

		return parse.scheme + "://" + parse.netloc


class Page(models.Model):
	site = models.ForeignKey("Site", on_delete=models.CASCADE)
	scheme = models.CharField(_('URL Scheme'), max_length=6, default="http", blank=False)
	path = models.TextField(_('URL Path'), blank=True, null=True)

	status = models.PositiveSmallIntegerField(blank=True, null=True)
	created = models.DateTimeField(_('first searched'), auto_now_add=True, blank=True, null=True)
	last_crawled = models.DateTimeField(_('last crawled'), auto_now=True, blank=True, null=True)
	backlinks = models.BigIntegerField(blank=True, null=True, default=0)

	raw_content = models.TextField(blank=True, null=True)
	page_title = models.CharField(max_length=2048, blank=True, null=True)
	article_title = models.CharField(max_length=2048, blank=True, null=True)
	article_content = models.TextField(blank=True, null=True)
	article_excerpt = models.CharField(max_length=4096, blank=True, null=True)
	article_top_image = models.CharField(max_length=4096, blank=True, null=True)
	article_keywords = ArrayField(models.CharField(max_length=512), blank=True, null=True)
	content_type = models.CharField(max_length=1024, blank=True, null=True)
	# links = ArrayField(models.BigIntegerField(), blank=True, null=True) # it's stored in Links model

	rank = models.FloatField(blank=True, null=True)
	meta = JSONField(blank=True, null=True)

	def __str__(self):
		return self.get_url()

	def get_url(self):
		if self.scheme:
			return "{}://{}{}".format(self.scheme, self.site.site_url, self.path)
		else:
			return "http://{}{}".format(self.site, self.path)

	def get_url_address(self):
		return "{}{}".format(self.site.site_url, self.path)

	def is_allowed(self):
		if self.site.robots_status==200:
			parser = RobotFileParser()
			lines = io.StringIO(self.site.robots).readlines()
			parser.parse(lines)
			return parser.can_fetch(settings.USER_AGENT, self.get_url())
		return True

	def scrap(self):
		url = self.get_url()
		print("retrieve page: {}".format(url))
		# check if we are allowed to crawl this page
		if not self.is_allowed():
			print("Retrieval is not allowed by robots.txt")
			return False

		# Get page content and headers
		try:
			response = requests.get(url, headers={'User-Agent': settings.USER_AGENT})
		except (requests.ConnectTimeout, requests.HTTPError, requests.ReadTimeout, requests.Timeout, requests.ConnectionError):
			return

		self.content_type = response.headers['content-type'] if 'content-type' in response.headers else ""  # usually "text/html"

		# don't store page content if it's not html
		self.raw_content = response.text
		if self.content_type.find("text/html") == -1:
			print("we don't process none html pages yet.")
			return False

		# store article title and content
		article = Article(url)
		article.set_html(self.raw_content)
		article.parse()
		self.article_title = article.title
		self.article_content = article.text
		self.article_top_image = article.top_image
		article.nlp()
		self.article_excerpt = article.summary
		self.article_keywords = article.keywords

		# parse html page
		soup = BeautifulSoup(self.raw_content, "html5lib")
		self.page_title = soup.title.string
		self.save()

		return soup  # for crawling


class SiteCrawlStats(models.Model):
	site = models.ForeignKey("Site")
	last_crawled = models.DateTimeField(_('last crawled'), auto_now=True, blank=True, null=True)


# class Keyword:
# 	keyword = models.CharField(max_length=1024, blank=True, null=True)
#
#
# class PageKeyword:
# 	page_id = models.ForeignKey("Page", on_delete=models.CASCADE)
# 	keyword_id = models.ForeignKey("Keyword")
# 	meta = JSONField(blank=True, null=True)


class Image(models.Model):
	page = models.ForeignKey("Page", related_name="image_page")
	title = models.CharField(max_length=1024, blank=True, null=True)
	link = models.TextField(_('ABSOLUTE URL'), blank=True, null=True)


class Link(models.Model):
	from_url = models.ForeignKey("Page", related_name="from_url")
	to_url = models.ForeignKey("Page", related_name="to_url")
	title = models.CharField(max_length=1024, blank=True, null=True)
	text = models.CharField(max_length=1024, blank=True, null=True)
	rel = models.CharField(max_length=1024, blank=True, null=True)

	def __str__(self):
		return "{} ~ {}".format(self.from_url, self.to_url)

	def add(self, from_url, to_url, title, rel):
		pass
		# add link
		# add 1 to Page.backlinks

	def remove(self):
		pass
		# remove override
		# remove 1 from Page.backlinks if it's bigger than 0
