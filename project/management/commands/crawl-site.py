from django.core.management.base import BaseCommand
from quaero.crawler import Crawler


class Command(BaseCommand):
	help = 'crawl site'

	def add_arguments(self, parser):
		parser.add_argument('url', nargs=1, type=str)
		parser.add_argument('depth', nargs=1, type=int)
		parser.add_argument('external', nargs=1, type=bool)

	def handle(self, *args, **options):
		url = options['url'][0]
		depth = options['depth'][0]
		external = options['external'][0]
		print("Crawling: {}\nWith the depth: {}".format(url, depth))
		crawler = Crawler(url=url, depth=depth, external=external)
		pass
