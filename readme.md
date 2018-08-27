# Impulse

I love [Momentum Dash](https://momentumdash.com/). I love how serene I feel just staring at the gorgeous backgrounds and how inspired I get from the quotes, but it's only available as a plugin for Chrome or Firefox. I wanted to be able to get some serenity and inspiration for those times when I'm not using either of those (eg on mobile) as well.

This is a Momentum Dash-inspired home page, that's restricted to displaying a background (with credits), a quote and a greeting/time. If you want all the other great features, I highly recommend going for the original and the best.

## Configuration and Installation

In order to use the configuration process, you will need to have lots of python3 stuff installed and a flickr API key.

Python dependencies:

 * Python3
   * Flask
   * json
   * Request
   * PyYAML
   * Jinja2

To create the static site:

1. Copy `defaults.tmpl.yaml` to `defaults.yaml` and edit as appropriate. 
2. Run `python3 make.py` to generate the static file `impulse.html`.
3. Copy `impulse.html` somewhere online and set your browser's home page to it.

In order to get gallery IDs from Flickr, paste the gallery link into [lookupGallery API explorer](https://www.flickr.com/services/api/explore/flickr.urls.lookupGallery) and look for the "id" part of the gallery tag.

References:
https://idratherbewriting.com/learnapidoc/docapis_flickr_example.html