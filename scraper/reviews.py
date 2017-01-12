#!/usr/bin/env python

"""Scrape beer reviews from beeradvocate.com."""

# scraping
import requests
from lxml import html

# mongodb
from pymongo import MongoClient

# functions


def get_html(link):
    """Load HTML page and parse it."""
    page = requests.get(link)
    tree = html.fromstring(page.content)
    return tree


def beer_link(page_id, brew_id, beer_id):
    """Create link to beer page including pagination and complete path."""
    start_page = (page_id * 25) - 25

    link = 'https://www.beeradvocate.com/beer/profile/'
    link = link + '%(brewery)s/%(beer)s/?view=beer&sort=&start=%(page)d' % {
        'brewery': brew_id, "beer": beer_id, 'page': start_page}

    return link


def beer_slink(brew_id, beer_id):
    """Create shortened link to beer page."""
    link = '/beer/profile/'
    link = link + '%(brewery)s/%(beer)s/?view=beer&sort=&start=' % {
        'brewery': brew_id, "beer": beer_id}

    return link


def get_max_page(max_page, tree, brew_id, beer_id):
    """Scrape maximum review page of beer."""
    link_s = beer_slink(brew_id, beer_id)
    links_a = tree.xpath('//a/@href')
    links_a = [s.replace(link_s, "") for s in links_a if link_s in s]

    try:
        maxmax = round(max([int(i) for i in links_a if i != '0#XenForo']) / 25)
    except:
        maxmax = 1

    if maxmax < max_page:
        return maxmax
    else:
        return max_page


def extr_reviews(tree):
    """Extract beer reviews (text) from HTML tree."""
    res = tree.xpath('//div[@id="rating_fullview_content_2"][1]/text()')

    # identify individual reviews
    res = ' '.join(res)
    res = res.split('\xa0\xa0rDev')

    # clean
    res = [r for r in res if r]
    res = [r.replace("\xa0", "") for r in res]
    res = [r.replace("\n", "") for r in res]

    return res


def extr_ratings(tree):
    """Extract beer ratings from HTML tree."""
    ratings = tree.xpath('//*[@id="rating_fullview_content_2"]/span[1]/text()')
    ratings = [float(r) for r in ratings]

    return ratings


def load_reviews(max_page, brew_id, beer_id):
    """Load reviews for beer."""
    reviews, ratings = [], []

    for i in range(1, max_page + 1):
        link = beer_link(i, brew_id, beer_id)
        tree = get_html(link)

        reviews.extend(extr_reviews(tree))
        ratings.extend(extr_ratings(tree))

        if len(reviews) != len(set(reviews)):
            print('Some duplicates.')

    return(reviews, ratings)


# load data
client = MongoClient()
db = client.breweries
cursor = db.styles.find()

data = [item for item in cursor]
beer_ids = [item['beer_id'] for item in data if 'reviews' not in item]
brew_ids = [item['brew_id'] for item in data if 'reviews' not in item]

# max number of pages to load for each beer
max_page = 10

for i in range(0, len(beer_ids)):
    print(i)
    beer_id = beer_ids[i]
    brew_id = brew_ids[i]

    try:
        link = beer_link(1, brew_id, beer_id)
        tree = get_html(link)

        # check maxpage
        current_max_page = get_max_page(max_page, tree, brew_id, beer_id)

        # get reviews
        reviews, ratings = load_reviews(current_max_page, brew_id, beer_id)

        # reviews in mongodb format
        ratings = [{'text': review,
                    'rating': rating}
                   for review, rating in zip(reviews, ratings)]

        # write in mongodb
        db.styles.update({"beer_id": beer_id, "brew_id": brew_id},
                         {"$set": {"reviews": []}})

        db.styles.update({"beer_id": beer_id, "brew_id": brew_id}, {"$push":
                         {"reviews": ratings}})

    except:
        print("Some error here")

    link, tree, current_max_page = None, None, None
    reviews, ratings, beer_id, brew_id = None, None, None, None
