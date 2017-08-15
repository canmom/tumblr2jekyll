import re
import os
from argparse import ArgumentParser
from slugify import slugify
from bs4 import BeautifulSoup
from tidylib import tidy_fragment
import requests

import util

def clean_date(datetime_string):
    return datetime_string.split(' ')[0]

def parse_text_post(post):
    assert post['type'] == 'text'

    title = post['title']
    date = clean_date(post['date'])
    html = post['body']

    return (title, date, html)

def parse_link_post(post):
    assert post['type'] == 'link'

    html_template = "{link}\n{description}"
    link_template = "<h1 class='link'><a href='{href}'>{text}</a></h1>\n"

    link = link_template.format(href=post['url'],text=post['title'])
    html = html_template.format(link=link,description=post['description'])

    title = post['title']
    date = clean_date(post['date'])

    return (title, date, html)

def parse_photo_post(post):
    assert post['type'] == 'photo'

    html_template = "{section}\n{caption}"
    section_template = "<section class='photoset'>\n{figures}\n</section>"
    figure_template = '<figure>\n{photo}\n{figcaption}\n</figure>\n'
    figcaption_template = '<figcaption>{caption}</figcaption>'
    img_template = "<img src='{src}'>"

    figures = []

    for photo in post['photos']:
        if photo['caption'] != '':
            figcaption = figcaption_template.format(caption=photo['caption'])
        else:
            figcaption = ''
        src = photo['alt_sizes'][0]['url']
        img = img_template.format(src=src)
        figure = figure_template.format(photo=img,figcaption=figcaption)
        figures.append(figure)

    section = section_template.format(figures='\n'.join(figures))

    html = html_template.format(section=section,caption=post['caption'])

    date = clean_date(post['date'])
    title = None
    
    return (title, date, html)

def parse_answer_post(post):
    assert post['type'] == 'answer'

    html_template = "{question}\n{answer}"
    question_template = "<p><a class='tumblr_blog' href='{url}'>{asker}</a> asked:</p>\n<blockquote class='ask'>{question}</blockquote>"

    question = question_template.format(url=post['asking_url'],asker=post['asking_name'],question=post['question'])
    html = html_template.format(question=question,answer=post['answer'])

    date = clean_date(post['date'])
    title = None

    return (title, date, html)

def get_post(blog,post_id):
    posts = util.get_posts(blog,{'id' : post_id})

    assert len(posts)==1, 'Expected only one post, received ' + str(len(posts))
    post = posts[0]

    if post['type'] == 'text':
        return parse_text_post(post)
    elif post['type'] == 'photo':
        return parse_photo_post(post)
    elif post['type'] == 'link':
        return parse_link_post(post)
    elif post['type'] == 'answer':
        return parse_answer_post(post)
    else:
        raise NotImplementedError('Unimplemented post type: ' + post['type'])

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

    return date + '-' + slug

def save_post(blog,post_id):
    try:
        title, date, html = get_post(blog,post_id)
    except AssertionError:
        print('Post is not a text post.')
        return

    if title is None:
        title = 'post-'+post_id
    filename = generate_filename(title,date,html)
    html = clean_html(html,filename)
    output = add_jekyll_boilerplate(title,html)

    file = open('posts/' + filename+'.html','w', encoding='utf8')
    file.write(output)
    file.close()
    print('processed',filename)