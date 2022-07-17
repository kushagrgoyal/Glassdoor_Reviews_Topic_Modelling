import os
import pandas as pd
import streamlit as st
from scraper_streamlit import glassdoor_scraper
from topic_modelling import 

# Building the inputs required for data scraping from Glassdoor
st.title('Glassdoor Scraper + Topic Modelling')

# The following radio button shows the choice of either scraping the data or directly analysing the previously scraped data
choice = st.radio(label = 'Data Scrape or select', options = ['Scrape', 'Load Pre-scraped data'], index = 1)

if choice == 'Scrape':
    chrome_driver_path = st.text_input(label = "Enter Chrome driver's path:", value = './chromedriver.exe')    
    base_url = st.text_input(label = "Enter Base page's url:")
    n_pages = st.text_input(label = "Enter number of pages to scrape:")
    save_loc = st.text_input(label = "Enter save location of the .csv file:")
    scrape_button = st.button('Scrape away!')

    if scrape_button:
        scraper = glassdoor_scraper(chrome_driver_path, base_url, int(n_pages))
        reviews = scraper.extract_reviews()
        scraper.save_reviews(save_loc)
    
    if os.path.exists(save_loc):
        reviews = pd.read_csv(save_loc)
        st.write(reviews)

else:
    load_loc = st.file_uploader('Choose location of reviews .csv file:')
    if load_loc is not None:
        reviews = pd.read_csv(load_loc)
        st.write(reviews)