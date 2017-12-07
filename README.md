## Description
Search Engine is still in development.

## Installation:
1. install requirement packages.
2. download "punkt" dataset in nltk.
```
$ python3
>>> import nltk
>>> nltk.download('punkt')
```

## Task List
- [x] User Management(login, signup, profile page, ...) powered by [Django Boilerplate](https://github.com/Towhidn/django-boilerplate "Django App Boilerplate")
- [x] Offline Data Storage Models(Sites, Pages, Links)
- [x] Simple HTML page scraper(powered by `BeautifulSoup`)
- [x] Crawler with depth as an endpoint(Simple page crawler powered by `requests`)
- [ ] Crawling Tasks
- [ ] Queues for Crawling Tasks(Powered by celery)
- [ ] Template to list active and queues tasks
- [ ] Backlink Counter
- [x] Templates(Search page, List sites and it's pages)
- [x] Extract Article content and title(remove extra HTML data such as sidebar, header, ...)
- [ ] Indexed Search(Powered by Solr, haystack)
## Tasks For Academic Research
- [ ] Sentiment Analysis
- [ ] Factoid Extraction and comparison
