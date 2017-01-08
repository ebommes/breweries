#!/usr/bin/env python

"""Check basic SpaCy functionality."""

# set path to project -> change if needed
project_path = '/Users/EB/Google Drive/Projects/breweries'

# modules
import pickle
import spacy
import os

# change directory and load Beer class
os.chdir(project_path + '/modules/')

from beeradvocate.classes import Beer

# create "custom" spacy pipeline (would also be standard)
def spacy_pipe(nlp):
    return(nlp.tagger, nlp.parser, nlp.entity)

# Load custom pipeline for English
nlp = spacy.load('en', create_pipeline = spacy_pipe)

# load pickled beer reviews
os.chdir(project_path + '/data/')
beers = pickle.load(open('reviews_sample.p', 'rb'))

# start with one review to check functionality
review = beers[0].reviews[0][0]
review = nlp(review)

# Lemmatize the review and keep only (proper) nouns and adjectives
# This might be "enough" pre-processing for e.g. cluster analysis
lemmas = []
for word in review:
    if word.pos_ in ('NOUN', 'PROPN', 'ADJ'):
        lemmas.append(word.lemma_)

print(lemmas)

# Parser
# Extract noun chunks in the text (with length > 1)
# Note: if dependency parsing is not needed, use:
#       spacy.load('en', parser = False) to increase speed
for np in review.noun_chunks:
    if len(np) > 1:
        print(np.lemma_)

# some of these dependencies (e.g. "creamy head", "earthy spice") 
# are more interesting than others (e.g. "this one")
# we can use a rule based system to extract them

for np in review.noun_chunks:
    toks = [token.pos_ for token in np]
    tok_count = toks.count('PROPN') + toks.count('NOUN') + toks.count('ADJ')

    if  tok_count == len(toks) & len(toks) > 1:
        print(np.lemma_)
