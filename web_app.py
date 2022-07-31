# import os
import pandas as pd
import streamlit as st
from scraper_streamlit import glassdoor_scraper
from topic_modelling import topic_model_maker

# Setting the page layout to wide mode as that is better for the visualosations
st.set_page_config(layout = 'wide')

# Building the inputs required for data scraping from Glassdoor
st.title('Glassdoor Scraper + Topic Modelling')

# The following radio button shows the choice of either scraping the data or directly analysing the previously scraped data
choice = st.radio(label = 'Data Scrape or select', options = ['Scrape Data', 'Load Pre-scraped data'], index = 1)

if choice == 'Scrape Data':
    # chrome_driver_path = st.text_input(label = "Enter Chrome driver's path:", value = './chromedriver.exe') 
    base_url = st.text_input(label = "Enter Base page's url:")
    n_pages = st.text_input(label = "Enter number of pages to scrape: Glassdoor has 10 reviews per page")
    # st.text("Note: Glassdoor has 10 reviews per page")
    # save_loc = st.text_input(label = "Enter save location of the .csv file:")
    scrape_button = st.button('Scrape away!')

    if scrape_button:
        # scraper = glassdoor_scraper(chrome_driver_path, base_url, int(n_pages))
        scraper = glassdoor_scraper(base_url, int(n_pages))
        reviews = scraper.extract_reviews()
        # scraper.save_reviews(save_loc)
    
    # if os.path.exists(save_loc):
    # reviews = pd.read_csv(save_loc)
        st.write(reviews)

        topic = topic_model_maker(reviews)
        top_mod, con_top, con_prob, cons = topic.create_topic_model()
        st.plotly_chart(top_mod.visualize_barchart(), use_container_width = True)
        st.plotly_chart(top_mod.visualize_documents(cons), use_container_width = True)
        st.write('Topics generated by NMF algorithm:')
        st.write(topic.find_topics_sklearn())
        st.write('Downloading the .csv file will delete the topic modelling done. To do it again, load the pre-scraped data')
        st.download_button(label = 'Download data', data = reviews.to_csv(index = None, encoding = 'utf-8'), mime = 'text/csv')

else:
    load_loc = st.file_uploader('Choose location of reviews .csv file:')
    if load_loc is not None:
        reviews = pd.read_csv(load_loc)
        st.write(reviews)

        topic = topic_model_maker(reviews)
        top_mod, con_top, con_prob, cons = topic.create_topic_model()
        st.plotly_chart(top_mod.visualize_barchart(), use_container_width = True)
        st.plotly_chart(top_mod.visualize_documents(cons), use_container_width = True)
        st.write('Topics generated by NMF algorithm:')
        st.write(topic.find_topics_sklearn())