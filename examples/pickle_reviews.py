#!/usr/bin/env python

"""Pickle reviews of 50 beers for nlp in SpaCy."""

# set path to project -> change if needed
project_path = '/Users/EB/Google Drive/Projects/breweries'

# mongodb
from pymongo import MongoClient

# pickle
import pickle

# random sampling
import random

# change directory
import os
os.chdir(project_path + '/modules/')

# beer
from beeradvocate.classes import Beer

# load data
client = MongoClient()
db = client.breweries
cursor = db.reviews.find()

# only keep beers with reviews
data = [item for item in cursor if 'reviews' in item]

# random sample of 50 beers
data = random.sample(data, 50)

# nicer data format
beers = []

for item in data:
    reviews = None
    reviews = [(i['text'], i['rating']) for i in item['reviews'][0]]
    beers.append(Beer(brew_id = item['brew_id'], 
                      beer_id = item['beer_id'], 
                      style_id = item['style_id'], 
                      brew_name = item['brew_name'], 
                      beer_name = item['beer_name'], 
                      style_name = item['style_name'], 
                      reviews = reviews))

# pickle results to data/reviews_sample.p
os.chdir(project_path + '/data/')
pickle.dump(beers, open('reviews_sample.p', 'wb'))
