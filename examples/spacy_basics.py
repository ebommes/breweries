#!/usr/bin/env python

"""Check basic SpaCy functionality."""

# set path to project -> change if needed
project_path = '/Users/EB/Google Drive/Projects/breweries'

# modules
import pickle
import spacy
import os

# create "custom" spacy pipeline (would also be standard)
def spacy_pipe(nlp):
    return(nlp.tagger, nlp.parser, nlp.entity)

# Load custom pipeline for English
nlp = spacy.load('en', create_pipeline = spacy_pipe)

# load pickled beer reviews
os.chdir(project_path + '/data/')
data = pickle.load(open('reviews_sample.p', 'rb'))

# start with one review to check functionality
review = data[1][10]
review = nlp(review)

# Lemmatize the review and keep only (proper) nouns and adjectives
# This might be "enough" pre-processing for e.g. cluster analysis
interesting_pos = ('NOUN', 'PROPN', 'ADJ')
print([word.lemma_ for word in review if word.pos_ in interesting_pos])

# Parser
# Extract noun chunks in the text (with length > 1)
# Note: if dependency parsing is not needed, use:
#       spacy.load('en', parser = False) to increase speed
print([np.lemma_ for np in review.noun_chunks if len(np) > 1])

# some of these dependencies (e.g. "dark fruit") 
# are more interesting than others (e.g. "the chance")
# we can use a rule based system to extract them

for np in review.noun_chunks:
    toks = [token.pos_ for token in np]
    tok_count = toks.count('PROPN') + toks.count('NOUN') + toks.count('ADJ')

    if  tok_count == len(toks) & len(toks) > 1:
        print(np.lemma_)


# Entity recognition
# Currently not interesting, might be interesting for other projects
print([(entity, entity.label_) for entity in review.ents])
