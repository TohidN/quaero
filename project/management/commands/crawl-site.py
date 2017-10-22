from django.core.management.base import BaseCommand
from quaero.crawler import Crawler


class Command(BaseCommand):
	help = 'create admin'

	def add_arguments(self, parser):
		parser.add_argument('url', nargs=1, type=str)
		parser.add_argument('depth', nargs=1, type=int)

	def handle(self, *args, **options):
		url = options['url'][0]
		depth =options['depth'][0]
		print("Crawling: {}\nWith the depth: {}".format(url, depth))
		crawler = Crawler(url=url, depth=depth)
		pass
