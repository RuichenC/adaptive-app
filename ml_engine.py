import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

def create_model(model_name):
    return SentenceTransformer(model_name)


def open_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def save_pickle(file_path, data):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

def generate_embeddings(model, data):
    embeddings = model.encode(data) 
    save_pickle('embeddings.pkl', embeddings)
    return embeddings

def get_embeddings(model, data):
    try:
        embeddings = open_pickle('embeddings.pkl')
    except:
        embeddings = generate_embeddings(model, data)
    return embeddings
