import json
import requests
from string import Template
import yaml

f = file('defaults.yaml', 'r')
defaults = yaml.load(f)

# 1. Transform the quotes.txt file into JSON
# 
# The quotes text file is in the format:
# 
# "My great quote"BySomeone
# "My great quote"BySomeone
# ...
# "My great quote"BySomeone
#
# And need to be rendered into json which looks like:
#
# json = [
#   ["My great quote", "BySomeone"],
#   ["My great quote", "BySomeone"],
#   ... ,
#   ["My great quote", "BySomeone"]
# ];
# 
# Note: the " marks here are actually “ (\u200) and ” (\u201), not normal quote marks.
# This is from copy/pasting quote history.

print("Writing out quotes.js file ... ")

quotes = []

f = open("quotes.txt", "r")
for line in f:
    [q, a] = line.replace('“','',1).replace('\n','').split('”',1)
    quotes.append({'quote': q, 'author': a})

f = open("static/quotes.js", "w")
f.write("var quotes = "+json.dumps(quotes)+";")

print(" done.")

# 2. Scrape a list of image URLs (+ credits) from specific galleries on flickr, convert into more JSON.
#
# We're looking to take a list of gallery names, convert them into gallery_ids to then get a list of 
# images.
#
# For each gallery_id we get a list of images, and we want to store:
#
# images = [
#   [url, title, owner, owner_url,
#   [...]
# ];
#
# URL is constructed as per https://www.flickr.com/services/api/misc.urls.html:
# 
# https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg
#    or
# https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}_[mstzb].jpg
#    or
# https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)
#
# We want a nice big image, so aiming for a "k" (2048 on biggest side) size image. 

print("Gathering gallery information ...")

gallery_names = []
images = []

api_key = defaults['flickrkey']
momentum_feed_4 = "152954026-72157680317429891"
gallery_id = momentum_feed_4

url = "https://api.flickr.com/services/rest/?method=flickr.galleries.getPhotos&api_key="+api_key+"&gallery_id="+gallery_id+"&format=json&nojsoncallback=1&extras=owner_name"
r = requests.get(url)

if (r.status_code != requests.codes.ok):
    print(" failed.")
    sys.exit()

image_list = (r.json())['photos']['photo']
image_count = len(image_list)

print(f"Found {image_count} images in the gallery.")
print("Getting image information ... ")

image_idx = 1

for image in image_list:
    print(f"{image_idx} of {image_count}")

    info = requests.get("https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key="+api_key+"&photo_id="+image['id']+"&format=json&nojsoncallback=1")

    size_list = (info.json())['sizes']['size']
    largest_image_url = size_list[len(size_list)-2]['source'] # Second to last is the biggest that's not an original

    images.append({'url': largest_image_url, 'title': image['title'], 'owner': image['ownername'], 'link': "https://www.flickr.com/photos/"+image['owner']})

    image_idx += 1

print(" done.")
print("Writing images.js ...")

f = open("static/images.js", "w")
f.write("var images = "+json.dumps(images)+";")

print(" done.")
