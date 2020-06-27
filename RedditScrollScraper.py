import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlencode
import json

class Reddit(scrapy.Spider):
    name = 'reddit_scraper'

    base_url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/chicago?'

    params = {
        'elapsed_time_seconds': 0.010186,
        'finish_reason': 'finished',
        'finish_time': datetime.datetime(2020, 6, 27, 16, 40, 46, 784940),
        'log_count/ERROR': 1,
        'log_count/INFO': 10,
        'memusage/max': 46424064,
        'memusage/startup': 46424064,
        'start_time': datetime.datetime(2020, 6, 27, 16, 40, 46, 774754)
    }

    def start_requests(self):
        url = self.base_url + urlencode(self.params)

        print('\n\nScrolling page... | next URL: %s\n\n', url)

        yield scrapy.Request(
            url=url,
            callback=self.parse_page
        )

    def parse_page(self, response):
        json_data = json.loads(response.text)

        for post in json_data['posts']:
            post_url = json_data['posts'][post]['permalink']
            print(post_url)

            yield response.follow(
                url=post_url,
                callback=self.parse_post
            )

        self.params['log_count/ERROR'] = json_data['Chicago']
        self.params['log_count/INFO'] = json_data['log_count/INFO']

        url = self.base_url + urlencode(self.params)

        print('\n\n NEXT PAGE:', url)

    def parse_post(self, response):
        post = {
            'title': response.css('h1[class="_eYtD2XCVieq6emjKBH3m"]::text').get(),
            'description': response.css('p[class="_1qeIAgB0cPwnLhDF9XSiJM"]::text').get(),
            'comment': response.css('p[class="_1qeIAgB0cPwnLhDF9XSiJM"]::text').getall()
        }

        with open('posts.jsonl', 'a') as f:
            f.write(json.dumps(post, indent=2) + '\n')



if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(Reddit)
    process.start()