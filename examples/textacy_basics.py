#!/usr/bin/env python

"""Check basic textacy functionality."""

# set path to project -> change if needed
project_path = '/Users/EB/Google Drive/Projects/breweries'

# modules
import pickle
import os
import textacy
import pylab # show plots

# load pickled beer reviews
os.chdir(project_path + '/data/')
data = pickle.load(open('reviews_sample.p', 'rb'))

# create beer reviews corpus
corpus = textacy.Corpus('en', texts = data[1], metadatas = data[0])

# specifications for terms list and document term matrix

tl_specs = {'ngrams': 1,
            'named_entities': False,
            'as_strings': True}

tl = (doc.to_terms_list(**tl_specs) for doc in corpus)

dtm_specs = {'terms_lists': tl, 
             'weighting': 'tfidf',
             'normalize': 'True',
             'smooth_idf': 'True',
             'min_df': 2,
             'max_df': 0.95}

# create document term matrix
dtm, id2t = textacy.vsm.doc_term_matrix(**dtm_specs)

# create topic model with 5 topics
model = textacy.tm.TopicModel('nmf', n_topics = 5)
model.fit(dtm)

# show top 6 terms for topics
for topic_idx, top_terms in model.top_topic_terms(id2t, top_n = 6):
    print('Topic', topic_idx + 1, ':', ", ".join(top_terms))

# termite plot
model.termite_plot(doc_term_matrix = dtm, id2term = id2t, n_terms = 15)
pylab.show()
