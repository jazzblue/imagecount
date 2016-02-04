#!/usr/bin/env python

"""
The program fetches information about movies in theaters from Rotten Tomatoes,
extracts IMDB ids from that information and determines number of images 
displayed on IMDB website for each such moviei page.

The program prints to standard output a JSON list of objects in the following as follows:

[
 {
    "url": "http://www.imdb.com/title/tt1229340",
    "count": 71,
    "imdb_id": "1229340"
  }
]
"""

import urllib2
import json
from multiprocessing.pool import ThreadPool
import re

MAX_PAGE_LIMIT = 50  # Maximum allowed movies per query.

# We assume that number of movies will be less than that to guard against infinite loops.
MAX_MOVIES = 10000

POOL_SIZE = 16

URL = 'http://api.rottentomatoes.com/api/public/v1.0/lists/movies/in_theaters.json'
API_KEY = 'put_your_key_here'

IMDB_URL_PREFIX = 'http://www.imdb.com/title/tt'

page_num = 1  # Initial value

imdb_ids = list()

while (page_num-1)*MAX_PAGE_LIMIT < MAX_MOVIES:  # Just to guard against infinite loop.

    # Query maximum movies data for the current page.
    movies_response = urllib2.urlopen(
        URL + '?' + 
        'apikey={api_key}'.format(api_key=API_KEY) + '&' + 
        'page_limit={page_limit}'.format(page_limit=MAX_PAGE_LIMIT) + '&' +
        'page={page}'.format(page=page_num)
    )

    if movies_response.code != 200:  # Response status code is not Success.
        raise Exception('Query to Rotten Tomatoes failed.')

    for m in json.loads(movies_response.read())['movies']:  # Go over movies list.
        
        if 'alternate_ids' in m and 'imdb' in m['alternate_ids']:  # Process only if IMDB id is present.

             # If a new ID has already been processed, that means that all movies have been processed
             # and Rotten Tomatoes just wrapped around. Stop processing and break out of outer while loop.
            if m['alternate_ids']['imdb'] in imdb_ids:
                break

            imdb_ids.append(m['alternate_ids']['imdb'])  # Append new IMDB id to IMDB id list. 

    else:  # If all IDs on the page were new, continue processing of the next page.
        page_num += 1  # Next page index for query.
        continue

    break

else:
    raise Exception('Too many different movies are found. Something is wrong.')
            
def get_img_count(html):
    """Counts number of <img> tags in specified html."""

    return len(re.findall('<img',html))

pool = ThreadPool(processes=POOL_SIZE)  # Create pool of worker threads.

img_info = list()

def get_imdb(imdb_id):
    """
    Issues GET request to IMDB page of the movie with specified IMDB ID. 
    Determines and stores image count of that page.
    """
    global img_info

    url = IMDB_URL_PREFIX + imdb_id

    try:
        imdb_response = urllib2.urlopen(url)

        if imdb_response.code == 200:  # If response id=s not Success, ignore.
            img_info.append(dict(url=url, imdb_id=imdb_id, count=get_img_count(imdb_response.read())))

    # If connection problem, ignore.
    except Exception as d:
        pass

pool.map(get_imdb, imdb_ids)  # Map IMDB ID list from Rotten tomatoes onto workers pool. 

print json.dumps(img_info, indent=4, separators=(',', ': '))  # Print final list to stdout.

