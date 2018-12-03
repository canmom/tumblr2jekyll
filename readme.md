A Python script to assist in trasnferring content from a Tumblr blog to a Jekyll site, using the Tumblr API.

The present version can only handle text posts, photo posts, link posts and answer posts. To identify a specific post, you need to use its ID; e.g. in
```
https://canmom.tumblr.com/post/86342049687/how-to-write-your-name-on-the-moon
```
the ID is the number `86342049687`.

## Requirements

- [slugify](https://github.com/un33k/python-slugify)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [pytidylib](http://countergram.com/open-source/pytidylib/)
- the HTML5 version of [HTML-tidy](http://www.html-tidy.org/) - currently this is not available in many package repositories, so you'll probably need to compile it from source and make sure it's on your PATH.

All but the last may be installed with PIP.

Additionally, you must generate a key and secret for the [Tumblr REST API](https://www.tumblr.com/docs/en/api/v2) and a corresponding OAuth token and secret. These should be placed in a file api_keys.txt at the root of the project, one key per line.

## Usage
Call with 

```
python3 tumblr2jekyll.py [-h] [--id ID] [--reblogger REBLOGGER]
                        [--source SOURCE]
                        [--prev_source_url [PREV_SOURCE_URL [PREV_SOURCE_URL ...]]]
                        [--no_images] [--tag TAG] [--subfolder SUBFOLDER]

```
with either...

 - `--id`: give a post ID to download (the number after `/post/` in the permalink URL)

or else, to download some or all posts from a specific blog...

 - `--source`: blog to download posts from
 - `--reblogger`: go to a second blog, and for each post originally from `--source`, navigate to the source blog and download (useful if you have a secondary blog where you reblog posts to archive them)
 - `--prev_source_url`: other URLs to treat as a reblog by `--source` when using `--reblogger`
 - `--tag`: only download posts if they have this tag

With both approaches, the following flags can be used:

 - `--subfolder`: posts will be saved in `./posts/[subfolder]`, creating if necessary
 - `--no_images`: default behaviour is to download every image in a text post, photo or photoset and save them in an associated folder. With this flag, images will not be downloaded.