import re
import string
import os
from pytumblr import TumblrRestClient
from argparse import ArgumentParser
from slugify import slugify
from bs4 import BeautifulSoup
from tidylib import tidy_fragment
import requests

# read id off command line
parser = ArgumentParser(description='Download Tumblr text post specified by id, and format for Jekyll')
parser.add_argument('id',help='id of the post to download')
args=parser.parse_args()

with k as open('api_keys.txt'):
    api_keys = k.readlines()
    k.close()

#init tumblr API client
client = TumblrRestClient(*api_keys)

def get_post(client,args):
    posts = client.posts('canmom',id=args.id)['posts']
    assert len(posts)==1, 'Expected only one post, received ' + len(posts)
    post = posts[0]

    title = post['title']
    date = post['date'].split(' ')[0]
    html = post['body']

    return (title, date, html)

def clean_figures(soup):
    for tag in soup.find_all(attrs={'class':'tmblr-full'}):
        tag['class'].remove('tmblr-full')
        if 'tmblr-embed' in tag['class']:
            tag['class'].remove('tmblr-embed')

        if len(tag['class']) == 0:
            del tag['class']

        del tag['data-orig-height']
        del tag['data-orig-width']
        del tag['data-url']
        del tag['data-provider']
        del tag['data-orig-src']

    #clean embedded youtube videos
    for tag in soup.find_all('iframe'):
        del tag['id']
        tag['src'] = tag['src'].split('?')[0]

    #clean embedded images
    for tag in soup.find_all('img'):
        del tag['data-orig-height']
        del tag['data-orig-width']
        del tag['data-orig-src']
        if 'alt' not in tag:
            tag['alt']='ALT TEXT NEEDED!'

def fix_nested_lists(soup):
    for tag in soup.find_all('ul'):
        if tag.parent.name == 'ul':
            if tag.previous_sibling.name == 'li':
                sib = tag.previous_sibling
                floating_tag = tag.extract()
                sib.append(floating_tag)

def tidy(soup):
    #put it through HTMLTidy to get nice output
    tidy_output = tidy_fragment(str(soup),options={'indent':'auto','logical-emphasis':'yes','vertical-space':'yes','fix-uri':'no'})

    #hacks to get spacing the way I want it, since Tidy puts in too much
    html = tidy_output[0].replace('\n\n\n','\n\n')
    html = re.sub(r'\n\n(\s*)<ul>',r'\n\1<ul>',html)

    #print Tidy error messages
    print(tidy_output[1])
    return html

def download_images(soup,images_subfolder):
    for index, tag in enumerate(soup.find_all('img')):
        tumblr_url = tag['src']
        #we don't need to worry about fancy URL parsing because Tumblr embedded image URLs are consistent
        ext = tumblr_url.rsplit('.',1)[-1]
        jekyll_path = 'img/embed/{subf}'.format(subf=images_subfolder)
        jekyll_filename = 'img-{ind:02}.{ext}'.format(ind=index,ext=ext,subf=images_subfolder)
        jekyll_url = '{{ site.url }}/' + jekyll_path + '/' + jekyll_filename
        tag['src'] = jekyll_url

        print('downloading '+tumblr_url)
        os.makedirs(jekyll_path,exist_ok=True)
        image_file = open(jekyll_path + '/' + jekyll_filename,'wb')
        req = requests.get(tumblr_url)
        image_file.write(req.content)
        image_file.close()

def clean_html(html,images_subfolder):
    #reformat Tumblr's returned HTML to make it consistent and pretty

    #clean those weird <br> tags tumblr inserts at the ends of paragraphs
    html = re.sub(r'<br/></([^<]+?)>',r'</\1>',html)

    #now let's get our HTML as a tree so we can format it nicely
    soup = BeautifulSoup(html, 'html.parser')

    #clean up in soup form
    clean_figures(soup)
    fix_nested_lists(soup)
    download_images(soup,images_subfolder)

    return tidy(soup)

def add_jekyll_boilerplate(title,html):
    jekyll_boilerplate = '---\ntitle: ' + title + '\nlayout: article\n---\n'

    return jekyll_boilerplate + html

def generate_filename(title,date,html):
    if title:
        slug = slugify(title)
    else:
        slug = slugify(re.sub('<[^<]+?>', '', html),max_length=50,word_boundary=True)

    return 'posts/' + date + '-' + slug

title, date, html = get_post(client,args)
filename = generate_filename(title,date,html)
html = clean_html(html,filename)
output = add_jekyll_boilerplate(title,html)

file = open(filename+'.html','w', encoding='utf8')
file.write(output)
file.close()
print('processed',filename)