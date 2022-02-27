import os
import datetime
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException


class NewsAPI(object):
    def __init__(self):
        # ATTENTION! DEVELOPER PLAN permits you to request 100 articles per day as far back as one month ago.
        #            Obviously, the 'NEWSAPI_KEY' env variable must be setted first.
        self.newsapi = NewsApiClient(api_key=os.environ['NEWSAPI_KEY'])
        self.sources = 'bbc-news,vice-news,google-news,mtv-news'
        self.domains = 'billboard.com,corriere.it,mediaset.it,gqitalia.it,amp.theguardian.com'
        self.from_param = datetime.datetime.now() - datetime.timedelta(30)
        self.to = datetime.datetime.now().strftime('%Y-%m-%d')
        self.sort_by = 'relevancy'
        self.page_size = 20

    def get_news(self, q):
        # ATTENTION! Before calling this function you should write query q taking care of:
        #            Surrounding phrases with quotes (") for exact match;
        #            Prepending words or phrases that must appear with a + symbol;
        #            Prepending words that must not appear with a - symbol;
        #            Alternatively, using the AND / OR / NOT keywords, and optionally group these with parenthesis;

        print(f"Getting from NewsAPI news by QUERY: {q} ...")
        try:
            results = self.newsapi.get_everything(q=q, from_param=self.from_param, to=self.to,
                                                  sources=self.sources, domains=self.domains,
                                                  sort_by=self.sort_by, page_size=self.page_size)
            return results['articles']
        except (KeyError, ValueError, NewsAPIException, ConnectionError, TimeoutError) as e:
            print(e)
            return None
