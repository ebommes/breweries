#!/usr/bin/env python

"""Simple text classification task with spacy, textacy and sklearn."""

# modules
import os
import pickle

# visualization
import matplotlib.pyplot as plt

# pandas
import pandas as pd

# sklearnlinter
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

# nlp
import spacy
import textacy

# import pylab  # show plots

# set path to project -> change if needed
project_path = '/Users/EB/Google Drive/Projects/breweries'

# configure matplotlib
plt.style.use('seaborn-white')

# functions


def get_lem(doc):
    """Returns lemma of spacy doc if lemma is noun / adjective."""

    interesting_pos = ('NOUN', 'PROPN', 'ADJ')
    lems = [word.lemma_ for word in doc if word.pos_ in interesting_pos]

    return lems


def get_chunk(noun_chunk):
    """Returns interesting parts of noun chunks."""

    interesting_pos = ('NOUN', 'PROPN', 'ADJ', 'ADV', 'VERB')
    chunk = [tok.lemma_ for tok in noun_chunk if tok.pos_ in interesting_pos]

    if len(chunk) > 1:
        return ' '.join(chunk)
    else:
        return ''


def term_list(doc):
    """Returns term list item which is used to create term document matrix"""

    tl = []

    # lemmata of nouns and adjectives
    tl.extend(get_lem(doc))

    # noun chunks
    chunks = [get_chunk(chunk) for chunk in doc.noun_chunks if chunk]
    tl.extend(chunks)

    return tl


def get_top_topic(model, doc_topic_matrix):
    """Returns top topic of estimated topic model."""
    top_topics = model.top_doc_topics(doc_topic_matrix, top_n=1)
    top_topics = [topics[0] for doc_idx, topics in top_topics]
    return top_topics


def accuracy(pred, actual):
    """Calculate accuracy of predictions."""
    return sum(pred == actual) / len(pred)

# load pickled beer reviews
os.chdir(project_path + '/data/')
data = pickle.load(open('2styles_sample.p', 'rb'))

# Load spacy pipeline for English
nlp = spacy.load('en')

# parse reviews
texts = [nlp(review) for review in data[1]]

# create term list
tl = [term_list(doc) for doc in texts]

# document term matrix
dtm_specs = {'terms_lists': (tl),
             'weighting': 'tfidf',
             'normalize': 'True',
             'smooth_idf': 'True',
             'min_df': 5,
             'max_df': 0.95}

dtm, id2t = textacy.vsm.doc_term_matrix(**dtm_specs)

# create topic model with 5 topics
model = textacy.tm.TopicModel('lda', n_topics=5)
model.fit(dtm)

# show top 6 terms for topics
for topic_idx, top_terms in model.top_topic_terms(id2t, top_n=6):
    print('Topic', topic_idx, ':', ', '.join(top_terms))

# assign topics to dtm
doc_topic_matrix = model.transform(dtm)
doc_topic_matrix.shape

# topic modeling data frame
df = pd.DataFrame(doc_topic_matrix)
df['style_name'] = [i['style_name'] for i in data[0]]
df['top_topic'] = get_top_topic(model, doc_topic_matrix)

# compute frequency table (absolute)
print(pd.crosstab(df['style_name'], df['top_topic']))

# compute frequency table (%)
ct = pd.crosstab(df['top_topic'], df['style_name'])
ct = ct.apply(lambda r: r / r.sum(), axis=1)

# visualize frequency table (%)
beer_plot = ct.plot.bar(stacked=True, color=['#ead61c', '#845422'],
                        edgecolor='none', lw=2, rot=0)
beer_plot.set_xlabel('Topic')
beer_plot.set_ylabel('Frequency (%)')
beer_plot.legend(bbox_to_anchor=(1.12, 1.12))

plt.show()

# results seem already quite usable for classification
# topic 0 -> Porter, topic 2 -> Lager

# Option A: Estimate SVM model with doc_topic_matrix as X variable
#           -> Nice because less variables as with DTM as input -> fast

X = pd.DataFrame(doc_topic_matrix)

# numeric encoding for y variable (beer style)
bin_encode = {'American Pale Lager': 0,
              'American Porter': 1}
y = df['style_name'].map(bin_encode)

# split in train and test set
X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                    test_size=0.1,
                                                    random_state=123)

# setup
seed = 123
folds = 5

# hyperparameters -> usually more tunings, just for illustration
parameters = {'clf__kernel': ('rbf', 'poly', 'linear', 'sigmoid'),
              'clf__gamma': ('auto', 1),
              'clf__C': (10, 1.0, 0.1)}

piper = Pipeline([('clf', SVC(random_state=seed))])

grid_search = GridSearchCV(piper, parameters, n_jobs=3, verbose=1,
                           refit=True, cv=folds)

grid_search.fit(X_train, y_train)

print('Best score: %0.3f' % grid_search.best_score_)
print(grid_search.best_estimator_)
y_pred = grid_search.predict(X_test)

res = pd.DataFrame({'y_test': pd.Series(y_test)})
res['y_pred'] = y_pred

print(pd.crosstab(res['y_test'], res['y_pred'], rownames=['True'],
                  colnames=['Predicted']))

print('Accuracy in test set: %0.3f' % accuracy(res['y_pred'], res['y_test']))


# Option B: Estimate SVM model with doc_term_matrix as X variable
#           -> slower but might be more accurate

X = dtm

# split in train and test set
X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                    test_size=0.1,
                                                    random_state=123)

parameters = {'clf__kernel': ('rbf', 'linear')}

piper = Pipeline([('clf', SVC(C=1.0, gamma='auto', random_state=seed))])

grid_search = GridSearchCV(piper, parameters, n_jobs=3, verbose=1,
                           refit=True, cv=folds)

grid_search.fit(X_train, y_train)

print('Best score: %0.3f' % grid_search.best_score_)
print(grid_search.best_estimator_)
y_pred = grid_search.predict(X_test)

res = pd.DataFrame({'y_test': pd.Series(y_test)})
res['y_pred'] = y_pred

print(pd.crosstab(res['y_test'], res['y_pred'], rownames=['True'],
                  colnames=['Predicted']))

print('Accuracy in test set: %0.3f' % accuracy(res['y_pred'], res['y_test']))
