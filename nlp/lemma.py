# -*- coding: utf-8 -*-

# modules
import pymysql # mysql support
import types   # simple namespace
import os      # change folder

from textblob          import TextBlob
from textblob.taggers  import PatternTagger
from textblob          import Word
from nltk.stem.wordnet import WordNetLemmatizer as lemma

# set path to Project to import paths
direct = '/Users/EB/breweries'
os.chdir(direct)

exec(open('sql-credentials.py').read())

# cred = {"host"    : "",
#         "user"    : "",
#         "pwd"     : "",
#         "charset" : ""}

# functions
def read(sql, cred, db):
    db  = pymysql.connect(host    = cred["host"],
                          user    = cred["user"], 
                          passwd  = cred["pwd"], 
                          db      = db)
    cursor = db.cursor() ; cursor.execute(sql)
    data   = cursor.fetchall()
    db.commit()
    cursor.close() ; db.close()

    return data

def createdb(cred):
    db  = pymysql.connect(host    = cred["host"],
                          user    = cred["user"], 
                          passwd  = cred["pwd"],
                          db      = "breweries")
    cur = db.cursor()
    sql = "CREATE TABLE `reviewsnlp` ("
    sql = sql + "`review` int(11) NOT NULL,"
    sql = sql + "`brewery` bigint(20) NOT NULL,"
    sql = sql + "`beer` bigint(20) NOT NULL,"
    sql = sql + "`lemma` text,"
    sql = sql + "PRIMARY KEY (`review`,`brewery`,`beer`)"
    sql = sql + ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"

    cur.execute(sql)
    db.commit()
    cur.close()
    db.close()


def clean(text):
    text = str(text.encode('ascii', 'ignore'))
    text = text.replace("\\n", " ")
    text = text.replace("\n", " ")
    text = text.replace('b"', ' ')
    text = text.replace(',', ' , ')
    text = text.replace('.', ' . ')
    text = text.replace('\\', '')
    return(str(text))

def posWN(posTB):
    if posTB.startswith('J'):
        return 'a'
    elif posTB.startswith('V'):
        return 'v'
    elif posTB.startswith('N'):
        return 'n'
    elif posTB.startswith('R'):
        return 'r'
    elif posTB.startswith('A'):
        return 's'
    else:
        return ''


def pos(blob):
    tok = [token[0] for token in blob.pos_tags]
    tokW = [Word(token) for token in tok]
    tokn = len(tok)
    posTB = [pos[1] for pos in blob.pos_tags]
    posW = [posWN(TB) for TB in posTB]
    res = [tok, posW]
    return res


def lem(words, pos):
    from nltk.stem.wordnet import WordNetLemmatizer as lemma
    tokn = len(words)
    posn = len(pos)

    lems = []
    for j in range(0, tokn):

        if pos[j] == '':
            verb = words[j].lemmatize('v')
            noun = words[j].lemmatize('n')

            if len(verb) == len(noun):
                lems.append(words[j])
            elif len(verb) < len(noun):
                lems.append(verb)
            else:
                lems.append(noun)
            
        else:
            lems.append(words[j].lemmatize(pos[j]))

    lems        = [token.lower() for token in lems]
    return lems


# try to create db table
try:
    createdb(cred)
except:
    print("Error while trying to create db, may already exist")

# import
reviews = read("SELECT * FROM reviews;", cred, "breweries")

i = 0
for i in range(0, len(reviews)):

    # structure
    review         = types.SimpleNamespace()
    review.id      = reviews[i][0]
    review.beer    = reviews[i][1]
    review.brewery = reviews[i][2]
    review.txt     = reviews[i][8]
    review.raw     = str(reviews[i][8])

    # clean text
    review.txt = clean(review.txt)    

    # create a textblob (for POS tagging)
    pt = PatternTagger()
    review.blob = TextBlob(review.txt, pos_tagger = pt)

    # extract POS tags
    review.pos = pos(review.blob)

    # extract lemmas
    review.lem = lem(review.pos[0], review.pos[1])
    review.lem = ' '.join(review.lem)
    review.lem = review.lem.replace("'", "\\'")

    # store results in sql table
    db  = pymysql.connect(host    = cred["host"],
                          user    = cred["user"], 
                          passwd  = cred["pwd"], 
                          db      = "breweries")
                       
    cur = db.cursor()

    sql = "INSERT INTO reviewsnlp(review, brewery, beer, lemma) VALUES ("
    sql = sql + "'" + str(review.id) + "'" + ", "
    sql = sql + "'" + str(review.brewery) + "'"+ ", "
    sql = sql + "'" + str(review.beer) + "'"+ ", "
    sql = sql + "'" + review.lem + "'" +");"

    try:
        cur.execute(sql)
        db.commit()
        cur.close() 
        db.close()
    except:
        print("OOPS")

