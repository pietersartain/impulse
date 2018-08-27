import json
import requests
import yaml
from optparse import OptionParser
from jinja2 import Template, Environment, PackageLoader, select_autoescape

f = open('defaults.yaml', 'r')
defaults = yaml.load(f)
f.close()

# Transform the quotes.txt file into JSON
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
def parse_quotes_as_json():
    quotes = []

    print("Writing out quotes.js file ... ")

    f = open("quotes.txt", "r")
    for line in f:
        [q, a] = line.replace('“','',1).replace('\n','').split('”',1)
        quotes.append({'quote': q, 'author': a})
    f.close()
    quotes = json.dumps(quotes)

    f = open("static/quotes.js", "w")
    f.write(quotes)
    f.close()

    print(" done.")

    return quotes

# Scrape a list of image URLs (+ credits) from specific galleries on flickr, convert into more JSON.
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
def get_image_info_as_json(api_key, gallery_id):
    images = []

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
        print(f"Image {image_idx} of {image_count}")

        info = requests.get("https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key="+api_key+"&photo_id="+image['id']+"&format=json&nojsoncallback=1")

        size_list = (info.json())['sizes']['size']
        largest_image_url = size_list[len(size_list)-2]['source'] # Second to last is the biggest that's not an original

        images.append({'url': largest_image_url, 'title': image['title'], 'owner': image['ownername'], 'link': "https://www.flickr.com/photos/"+image['owner']})

        image_idx += 1

    print(" done.")

    print(f"Writing images-{gallery_id}.js ...")

    images = json.dumps(images)

    f = open(f"static/images-{gallery_id}.js", "w")
    f.write(images)
    f.close()

    print(" done.")

    return images


def get_all_galleries(api_key, gallery_ids):

    gallery_count = len(gallery_ids)

    images = []

    print(f"Found {gallery_count} galleries.")
    print("Gathering gallery information ...")

    gallery_idx = 1

    for gallery_id in gallery_ids:
        print(f"Looking through {gallery_idx} of {gallery_count}")
        images += json.loads(get_image_info_as_json(api_key, gallery_id))
        gallery_idx += 1

    print("Writing images.js ...")

    images = json.dumps(images)

    f = open("static/images.js", "w")
    f.write(images)
    f.close()

    print(" done.")

    return images

#
#
#
#
def parse_template(quotes, images, greetingname):
    print("Writing impulse.html ...")

    env = Environment(
        loader=PackageLoader('__main__', '.'),
        autoescape=select_autoescape(enabled_extensions=[], disabled_extensions=['html','xml'], default_for_string=False, default=False)
    )

    template = env.get_template('impulse.tmpl.html')
    page = template.render(quotes=quotes, images=images, greetingname=greetingname)
    f = open("static/impulse.html", "w")
    for line in page:
        f.write(line)
    f.close()

    print(" done.")


parser = OptionParser()
# Defaults: action="store", type="string", 
parser.add_option("-a", "--all",    action="store_true", dest="RUN_ALL",      default=False, help="Actually run everything. Without this, it's just a dry run.")
parser.add_option("-i",             action="store_true", dest="RUN_IMAGES",   default=False, help="Run the image gallery scraper, to create a intermediary images.js file.")
parser.add_option("-g",             action="store",      dest="RUN_GALLERY",  default=False, help="Run the image gallery scraper, to create an intermediary images-GALLERY.js file.")
parser.add_option("-q",             action="store_true", dest="RUN_QUOTES",   default=False, help="Run the quote parser, to create a intermediary quotes.js file.")
parser.add_option("-t",             action="store_true", dest="RUN_TEMPLATE", default=False, help="Run the templating engine, to make an impulse.html file from the intermediary files.")
(options, args) = parser.parse_args()

if (options.RUN_ALL):
    quotes = parse_quotes_as_json()
    images = get_all_galleries(defaults['flickrkey'], defaults['gallery_ids'])
    parse_template(quotes, images, defaults['greetingname'])

if (options.RUN_QUOTES):
    parse_quotes_as_json()

if (options.RUN_IMAGES):
    get_all_galleries(defaults['flickrkey'], defaults['gallery_ids'])

if (options.RUN_GALLERY):
    get_image_info_as_json(defaults['flickrkey'], options.RUN_GALLERY)

if (options.RUN_TEMPLATE):
    f = open("static/images.js", "r")
    images = f.read()

    f = open("static/quotes.js", "r")
    quotes = f.read()

    parse_template(quotes, images, defaults['greetingname'])
