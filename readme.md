A Python script to assist in trasnferring content from a Tumblr blog to a Jekyll site, using the Tumblr API.

The present version can only handle text posts, and works on one text post at a time. A post is identified by its 'id' number, which can be read from its URL. For example, with the post 
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
```
python3 downloader.py ID [--blog BLOG]
```
The script will download the specified post if it exists, and save its HTML in the `posts/` folder with Jekyll frontmatter. Any inline images will be downloaded and placed in a subfolder corresponding to the post's filename in the `img/embed/` folder.