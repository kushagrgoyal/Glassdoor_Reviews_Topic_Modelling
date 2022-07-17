from bertopic import BERTopic
from bertopic.backend import WordDocEmbedder
from flair.embeddings import TransformerDocumentEmbeddings
import numpy as np
import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util

class topic_model_maker():
    def __init__(self, rev_path):
        '''
        rev_path: Path of .csv file of self.rev
        '''
        self.rev_path = rev_path
    
    def preprocess_reviews(self):
        '''
        This function performs basic text processing of Pros and Cons in the reviews
        '''
        self.rev = pd.read_csv(self.rev_path)
        self.rev[['Employee_status', 'Duration']] = self.rev['Employee_status'].str.split(', ', expand = True)
        self.rev[['Review_date', 'Position']] = self.rev['Review_date'].str.split(' - ', expand = True)

        self.rev['Review_date'] = pd.to_datetime(self.rev['Review_date'])
        self.rev['Cons'] = self.rev['Cons'].str.lower()
        self.rev['Pros'] = self.rev['Pros'].str.lower()
        self.rev['Cons'] = self.rev['Cons'].apply(lambda x: re.sub("\.{1,5}|-{1,5}|>|<|\d\.|,", '', x)).apply(lambda x: re.sub("/", ' ', x)).apply(lambda x: re.sub(" {2,5}", ' ', x))
        self.rev['Pros'] = self.rev['Pros'].apply(lambda x: re.sub("\.{1,5}|-{1,5}|>|<|\d\.|,", '', x)).apply(lambda x: re.sub("/", ' ', x)).apply(lambda x: re.sub(" {2,5}", ' ', x))
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
        # Word embedding model
        bert = TransformerDocumentEmbeddings('bert-base-uncased')

        # Document embedding model
        sent_former = SentenceTransformer("all-mpnet-base-v2")

        # Create a model that uses both language models and pass it through BERTopic
        word_doc_embedder = WordDocEmbedder(embedding_model = sent_former, word_embedding_model = bert)
        self.topic_model = BERTopic(n_gram_range = (3, 7), embedding_model = word_doc_embedder, verbose=True).fit(self.rev['Cons'])
        self.con_topics, self.con_probs = self.topic_model.transform(self.rev['Cons'])

        return self.topic_model, self.con_topics, self.con_probs
    
    def create_visualisations(self):
        '''
        This function creates the visualizations for understanding the different topics in the Cons of the reviews
        '''
        return self.topic_model.visualize_documents(self.rev['Cons'])