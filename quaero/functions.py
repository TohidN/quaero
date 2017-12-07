from urllib.parse import urlparse, urljoin


def get_site_path(link_url):
	parse = urlparse(link_url)
	site_url = parse.netloc
	path = parse.path
	# remove "/" at the end of site's url
	if site_url[-1:] == "/":
		site_url = site_url[:-1]
	# if path starts with "./" remove it from beginning of the path
	if path[0:2] == "./":
		path = path[1:]
	return site_url, path