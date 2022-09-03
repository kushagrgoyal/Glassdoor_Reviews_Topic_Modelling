from autoscraper import AutoScraper
import pandas as pd

class glassdoor_scraper():
    def __init__(self, b, n):
        '''
        b: Base page url
        n: Number of pages to scrape
        '''
        self.b = b
        self.n = n
        self.scraper = AutoScraper()
        self.scraper.load('glassdoor-scraper')
    
    def generate_paginated_url(self, page):
        '''
        This function generates the paginated urls from base url
        '''
        return f'_IP{page}.htm'.join(self.b.split('.htm'))
    
    def extract_reviews(self):
        '''
        This function will take the driver object and return the extracted data from that page
        '''
        for i in range(1, self.n + 1):
            if i == 1:
                temp = self.scraper.get_result_similar(self.b)
                temp = {'Pros':temp[::2], 'Cons':temp[1::2]}
                self.reviews = pd.DataFrame(temp)
            else:
                temp = self.scraper.get_result_similar(self.generate_paginated_url(i))
                # print(f'Page {i} scraped with total data {len(temp)}')

                temp = pd.DataFrame({'Pros':temp[::2], 'Cons':temp[1::2]})
                self.reviews = pd.concat([self.reviews, temp], axis = 0)
        self.reviews.reset_index(inplace = True, drop = True)
        return self.reviews