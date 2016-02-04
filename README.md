# imagecount

The program fetches information about movies in theaters from Rotten Tomatoes,
extracts IMDB ids from that information and determines number of images
displayed on IMDB website for each such movie page.

The script uses APIs extensively and takes advantage of multithreading.

You will have to use your own API key for Rotten Tomatoes: change the variable API_KEY assignment to your key.

The program prints to standard output a JSON list of objects in the following as follows:

[
 {
    "url": "http://www.imdb.com/title/tt1229340",
    "count": 71,
    "imdb_id": "1229340"
  }
]

