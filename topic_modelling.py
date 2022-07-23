import nltk
from nltk.corpus import stopwords
from bertopic import BERTopic
from bertopic.backend import WordDocEmbedder
from flair.embeddings import TransformerDocumentEmbeddings
import numpy as np
import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.pipeline import make_pipeline

class topic_model_maker():
    def __init__(self, rev):
        '''
        rev_path: Pandas DataFrame of reviews
        '''
        self.rev = rev
    
    def preprocess_reviews(self):
        '''
        This function performs basic text processing of Pros and Cons in the reviews
        '''
        self.rev[['Employee_status', 'Duration']] = self.rev['Employee_status'].str.split(', ', expand = True)
        self.rev[['Review_date', 'Position']] = self.rev['Review_date'].str.split(' - ', n = 1, expand = True)

        self.rev['Review_date'] = pd.to_datetime(self.rev['Review_date'])
        self.rev['Cons'] = self.rev['Cons'].str.lower()
        self.rev['Pros'] = self.rev['Pros'].str.lower()
        self.rev['Cons'] = self.rev['Cons'].apply(lambda x: re.sub("\.{1,5}|-{1,5}|>|<|\d\.|,", '', x)).apply(lambda x: re.sub("/", ' ', x)).apply(lambda x: re.sub(" {2,5}", ' ', x))
        self.rev['Pros'] = self.rev['Pros'].apply(lambda x: re.sub("\.{1,5}|-{1,5}|>|<|\d\.|,", '', x)).apply(lambda x: re.sub("/", ' ', x)).apply(lambda x: re.sub(" {2,5}", ' ', x))
        
        sent_list = ['nothing not bad at all really good',
               'everything is good as of now',
               'no cons observed till date',
               "nothing as of now it's the best company",
               'nothing that i can think of',
               "i couldn't find any significant con",
               'none really i love it here',
               ]
        self.rev = self.remove_reviews_with_no_cons(sent_list)
        return self.rev
    
    def remove_reviews_with_no_cons(self, sentences_list, threshold = 0.25):
        '''
        The function takes in the preprocessed reviews dataframe and then removes the reviews that say there are "no Cons"
        This is done based on Sentence similarity score
        sentences_list: Input list of sentences as a sample to evaluate against
        '''
        model = SentenceTransformer('all-MiniLM-L6-v2')
        sent_remove_embed = model.encode(sentences_list, convert_to_tensor = True)
        cons_embed = model.encode(self.rev['Cons'].values, convert_to_tensor = True)

        cos_scores = util.cos_sim(sent_remove_embed, cons_embed)
        e = cos_scores.mean(axis = 0)

        self.rev['Cons_cos_score'] = np.array(e.cpu()).reshape(-1, 1)
        self.rev = self.rev[self.rev['Cons_cos_score'] <= threshold]
        self.rev.drop('Cons_cos_score', axis = 1, inplace = True)
        self.rev.reset_index(drop = True, inplace = True)
        return self.rev
    
    def create_topic_model(self):
        '''
        This function creates the embeddings for the Cons and performs Topic modelling with them
        '''
        # We do the preprocessing of all the reviews here directly using the preprocess_reviews function
        self.rev = self.preprocess_reviews()

        # Word embedding model
        bert = TransformerDocumentEmbeddings('bert-base-uncased')

        # Document embedding model
        sent_former = SentenceTransformer("all-mpnet-base-v2")

        # Create a model that uses both language models and pass it through BERTopic
        word_doc_embedder = WordDocEmbedder(embedding_model = sent_former, word_embedding_model = bert)
        self.topic_model = BERTopic(n_gram_range = (3, 7), embedding_model = word_doc_embedder, verbose=True).fit(self.rev['Cons'])
        self.con_topics, self.con_probs = self.topic_model.transform(self.rev['Cons'])

        return self.topic_model, self.con_topics, self.con_probs
    
    def find_topics_sklearn(self, nmf_comp = 5, n_top_words = 5):
        '''
        This function performs the topic extraction and provides the topics and their highest occurring words
        nmf_comp: Number of topics to extract
        n_top_words: Number of words in each topic
        '''
        stoplist = stopwords.words('english')

        tfidf_vectorizer = TfidfVectorizer(stop_words = stoplist, ngram_range = (3, 7))
        nmf = NMF(n_components = nmf_comp)
        self.pipe = make_pipeline(tfidf_vectorizer, nmf)
        self.pipe.fit(self.rev['Cons'])
        
        feature_names = tfidf_vectorizer.get_feature_names()

        self.output = {}
        for topic_idx, topic in enumerate(nmf.components_):
            self.output[f'Topic_{topic_idx}'] = ", ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
        
        self.output = pd.DataFrame(self.output).T        
        return self.output