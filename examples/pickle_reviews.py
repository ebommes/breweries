#!/usr/bin/env python

"""Pickle reviews of 100 beers for nlp in SpaCy."""

# set path to project -> change if needed
project_path = '/Users/EB/Google Drive/Projects/breweries'

# mongodb
from pymongo import MongoClient

# pickle
import pickle
import os

# random sampling
import random

# create corpus
import textacy

# functions
def mdata(item, review):
    """Returns meta data in dictionary format."""
    meta = {'brew_id': item['brew_id'], 
            'beer_id': item['beer_id'], 
            'style_id': item['style_id'], 
            'brew_name': item['brew_name'], 
            'beer_name': item['beer_name'], 
            'style_name': item['style_name'],
            'rating': review[1] 
           }
    return meta

# load data
client = MongoClient()
db = client.breweries
cursor = db.reviews.find()

# only keep beers with reviews
data = [item for item in cursor if 'reviews' in item]

# random sample of 100 beers
data = random.sample(data, 100)

# textacy corpus format
meta = []
texts = []

for item in data:
    reviews = None
    reviews = [(i['text'], i['rating']) for i in item['reviews'][0]]
    for review in reviews:
        meta.append(mdata(item, review))
        texts.append(review[0])

# saving textacy corpus currently only works with ascii text -> pickle instead
os.chdir(project_path + '/data/')

with open('reviews_sample.p', 'wb') as f:
    pickle.dump([meta, texts], f)
