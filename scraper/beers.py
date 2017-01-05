print('Extract 50 beers with highest amount of votes for each style')

# modules
# scraping
import requests
from lxml import html

# mongodb
from pymongo import MongoClient


# functions
def add_beer(beer_id, beer_name, brewery_id, brew_name):
    db.breweries.update_one({"_id": ident}, {"$push": 
        {"beers": 
            {"id": beer_id,
             'name': beer_name,
             'brewery': {'brewery_id': brewery_id, 'name': brew_name}
            }
        }
    })

def grab_infos(link):
    # constants to select range in table
    min_tr = 4
    max_tr = 54
    page = requests.get(link)
    tree = html.fromstring(page.content)

    brew_name, ids, beer_name = [], [], []

    for i in range(min_tr, max_tr):
        p = '//*[@id="ba-content"]/table/tr[' + str(i) + ']'

        brew_name.append(tree.xpath(p + '//text()')[1])
        beer_name.append(tree.xpath(p + '//text()')[0])
        ids.append(tree.xpath(p + '//a/@href')[0])

    brewery_id = [i.split('/')[3] for i in ids]
    beer_id = [i.split('/')[4] for i in ids]

    return(beer_id, beer_name, brewery_id, brew_name)


# load beer styles
client = MongoClient()
db = client.breweries
cursor = db.breweries.find()

style_ids = [d['_id'] for d in cursor]

# get beer ids
for style in style_ids:
    print(style)
    ident = style
    link = 'https://www.beeradvocate.com/beer/style/' + str(ident)
    link = link + '/?sort=revsD'
    try:
        beer_id, beer_name, brewery_id, brew_name = grab_infos(link)
        
        db.breweries.update({"_id": ident}, {"$set": {"beers": []}})
        
        for j in range(0, len(beer_id)):
            add_beer(beer_id[j], beer_name[j], brewery_id[j], brew_name[j])

    except:
        print("Some problem here!")
