import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')

###########################################################################
# User Inputs
chrome_driver = 'chromedriver.exe'

# Depending upon the company, the base url and paginated url will be different
# Update them accordingly
# Here, it is for Fractal Analytics, already sorted by 'Most Recent', page format is _P2, _P3 etc.
base_url = 'https://www.glassdoor.co.in/Reviews/Fractal-India-Reviews-EI_IE270403.0,7_IL.8,13_IN115.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng'
paginated_url = 'https://www.glassdoor.co.in/Reviews/Fractal-India-Reviews-EI_IE270403.0,7_IL.8,13_IN115_IP2.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng'

number_of_pages = 30
save_path = 'reviews.csv'
###########################################################################

def extract_data(driver):
    '''
    This function will take the driver object and return the extracted data from that page
    '''
    reviews = driver.find_elements_by_tag_name('li')
    ratings = []
    employee_st = []
    dates = []
    titles = []
    pros = []
    cons = []

    # The ids are extracted for 'li' tags as they are needed to be used in xpaths later to extract the actual reviews etc.
    ids = [i.get_attribute('id') for i in reviews if 'empReview' in i.get_attribute('id')]
    for i in ids:
        ratings.append(driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div/div[1]/div/div/div/span[1]').text)
        employee_st.append(driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div/div[1]/div/span').text)
        dates.append(driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div/div[2]/div/div[1]/span/span/span[1]').text)
        titles.append(driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div/div[2]/div/div[1]/h2/a').text)
        pros.append(driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div/div[2]/div/div[2]/div[1]/p[2]/span').text)
        cons.append(driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div/div[2]/div/div[2]/div[2]/p[2]/span').text)
    
    df = pd.DataFrame({
        'Rating':ratings,
        'Employee_status':employee_st,
        'Review_date':dates,
        'Title':titles,
        'Pros':pros,
        'Cons':cons
    })
    return df


def extract_reviews(b_url, p_url, n_pages):
    '''
    This function takes in the base url, paginated url and number of pages
    b_url: base page url
    p_url: paginated url
    n_pages: int, number of pages to scrape reviews from
    '''
    reviews = pd.DataFrame()
    for i in range(1, n_pages + 1):
        driver = webdriver.Chrome(chrome_driver, chrome_options = options)
        if i == 1:
            driver.get(b_url)
            driver.implicitly_wait(2)
            reviews = extract_data(driver)
            print('Page 1 scraped')
        else:
            # We open a new window to open the paginated urls
            # After scraping the page 2 data, window is closed
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            
            if i > 2:
                p_url = p_url.replace(f'_IP{i-1}', f'_IP{i}')
            driver.get(p_url)
            driver.implicitly_wait(2)
            reviews = pd.concat([reviews, extract_data(driver)], axis = 0)
            
            # Close the paginated new window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print(f'Page {i} scraped')
        driver.implicitly_wait(2)
    # Final quit method to close the webdriver and exit completely after ending the loop
    driver.quit()
    print('\nAll pages scraped!!!')
    return reviews

# Main Loop
reviews = extract_reviews(base_url, paginated_url, number_of_pages)
reviews.to_csv(save_path, index = None)