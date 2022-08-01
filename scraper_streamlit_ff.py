import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# from selenium.webdriver.chrome.service import Service as ChromiumService
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.utils import ChromeType

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

options = Options()
options.add_argument('--headless')

class glassdoor_scraper():
    '''
    This is a Glassdoor scraper class that can scrape reviews for any company from Glassdoor
    '''
    def __init__(self, b, n):
        '''
        dr_path: Chrome driver path
        b: Base page url
        n: Number of pages to scrape
        s_path: Save location of path
        '''
        # self.dr = webdriver.Chrome(self.dr_path, chrome_options = options)
        # self.dr_path = dr_path
        self.b = b
        self.n = n
    
    def generate_paginated_url(self, page):
        '''
        This function generates the paginated urls from base url
        '''
        return f'_IP{page}.htm'.join(self.b.split('.htm'))

    def extract_data(self):
        '''
        This function will take the driver object and return the extracted data from that page
        '''
        # reviews = driver.find_elements_by_tag_name('li')
        reviews = self.dr.find_elements(By.TAG_NAME, 'li')
        self.ratings = []
        self.employee_st = []
        self.dates = []
        self.titles = []
        self.pros = []
        self.cons = []

        # The ids are extracted for 'li' tags as they are needed to be used in xpaths later to extract the actual reviews etc.
        ids = [i.get_attribute('id') for i in reviews if 'empReview' in i.get_attribute('id')]
        for i in ids:            
            self.ratings.append(self.dr.find_element(By.XPATH, f'//*[@id="{i}"]/div/div/div[1]/div/div/div/span[1]').text)
            self.employee_st.append(self.dr.find_element(By.XPATH, f'//*[@id="{i}"]/div/div/div[1]/div/span').text)
            self.dates.append(self.dr.find_element(By.XPATH, f'//*[@id="{i}"]/div/div/div[2]/div/div[1]/span/span/span[1]').text)
            self.titles.append(self.dr.find_element(By.XPATH, f'//*[@id="{i}"]/div/div/div[2]/div/div[1]/h2/a').text)
            self.pros.append(self.dr.find_element(By.XPATH, f'//*[@id="{i}"]/div/div/div[2]/div/div[2]/div[1]/p[2]/span').text)
            self.cons.append(self.dr.find_element(By.XPATH, f'//*[@id="{i}"]/div/div/div[2]/div/div[2]/div[2]/p[2]/span').text)
        
        self.df = pd.DataFrame({
            'Rating':self.ratings,
            'Employee_status':self.employee_st,
            'Review_date':self.dates,
            'Title':self.titles,
            'Pros':self.pros,
            'Cons':self.cons
        })
        return self.df

    def extract_reviews(self):
        '''
        This function takes in the base url, paginated url and number of pages
        '''
        self.r = pd.DataFrame()
        for i in range(1, self.n + 1):
            # self.dr = webdriver.Chrome(self.dr_path, chrome_options = options)
            # self.dr = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()), chrome_options = options)
            # self.dr = webdriver.Chrome(service = ChromiumService(ChromeDriverManager(chrome_type = ChromeType.CHROMIUM).install()))
            service = Service(GeckoDriverManager().install())
            self.dr =  webdriver.Firefox(options = options, service = service)
            if i == 1:
                self.dr.get(self.b)
                self.dr.implicitly_wait(2)
                self.r = self.extract_data()
                print('Page 1 scraped')
            else:
                # We open a new window to open the paginated urls
                # After scraping the page 2 data, window is closed
                self.dr.execute_script("window.open('');")
                self.dr.switch_to.window(self.dr.window_handles[1])
                
                # if i > 2:
                    # self.p = self.p.replace(f'_IP{i-1}', f'_IP{i}')
                self.p = self.generate_paginated_url(i)
                self.dr.get(self.p)
                self.dr.implicitly_wait(2)
                self.r = pd.concat([self.r, self.extract_data()], axis = 0)
                
                # Close the paginated new window
                self.dr.close()
                self.dr.switch_to.window(self.dr.window_handles[0])
                print(f'Page {i} scraped')
            self.dr.implicitly_wait(2)
        
        # Final quit method to close the webdriver and exit completely after ending the loop
        self.dr.quit()
        print('\nAll pages scraped!!!')
        return self.r

    def save_reviews(self, s_path):
        '''
        This function saves the .csv file for the reviews at the selected location
        s_path: Save location for the .csv
        '''
        self.r.to_csv(s_path, index = None)