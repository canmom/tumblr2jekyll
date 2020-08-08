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
    html = post['body']

    return (title, html)

def parse_link_post(post):
    assert post['type'] == 'link'

    html_template = "{link}\n{description}"
    link_template = "<h1 class='link'><a href='{href}'>{text}</a></h1>\n"

    link = link_template.format(href=post['url'],text=post['title'])
    html = html_template.format(link=link,description=post['description'])

    title = post['title']

    return (title, html)

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

    title = None
    
    return (title, html)

def parse_answer_post(post):
    assert post['type'] == 'answer'

    html_template = "{question}\n{answer}"
    question_template = "<p><a class='tumblr_blog' href='{url}'>{asker}</a> asked:</p>\n<blockquote class='ask'>{question}</blockquote>"

    question = question_template.format(url=post['asking_url'],asker=post['asking_name'],question=post['question'])
    html = html_template.format(question=question,answer=post['answer'])

    title = None

    return (title, html)

def parse_quote_post(post):
    assert post['type'] == 'quote'

    quote_template = "<blockquote>{quote}</blockquote>\n{source}"

    html = quote_template.format(quote = post['text'],source = post ['source'])

    title = None

    return (title, html)

def parse_chat_post(post):
    assert post['type'] == 'chat'

    line_template = '<li class="person{personindex}"><strong class="name">{name}</strong> {message}</li>'
    page_template = '<ul class="chat">{lines}</ul>'

    dialogue = post['dialogue']
    people = []
    formatted_lines = []

    for line in dialogue:
        name = line['label']
        message = line['phrase']
        if name in people:
            personindex = people.index(name) + 1
        else:
            people.append(name)
            personindex = len(people)

        formatted_lines.append(line_template.format(personindex = personindex, name = name, message = message))

    html = page_template.format(lines="\n".join(formatted_lines))

    title = post['title']

    return (title, html)

def parse_audio_post(post):
    assert post['type'] == 'audio'

    html_template = '{player}\n{caption}'

    html = html_template.format(player = post['player'], caption = post['caption'])

    title = post['track_name']

    return (title, html)

def parse_video_post(post):
    assert post['type'] == 'video'

def parse_npf_post(post):
    assert post['type'] == 'blocks'

def parse_post(post):
    date = clean_date(post['date'])
    permalink = post['post_url']

    if post['type'] == 'text':
        title, html = parse_text_post(post)
    elif post['type'] == 'photo':
        title, html = parse_photo_post(post)
    elif post['type'] == 'link':
        title, html = parse_link_post(post)
    elif post['type'] == 'answer':
        title, html = parse_answer_post(post)
    elif post['type'] == 'quote':
        title, html = parse_quote_post(post)
    elif post['type'] == 'chat':
        title, html = parse_chat_post(post)
    else:
        raise NotImplementedError('Unimplemented post type: ' + post['type'])

    return (title, date, html, permalink)

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

def fix_images(soup,images_subfolder):
    image_urls = []
    for index, tag in enumerate(soup.find_all('img')):
        tumblr_url = tag['src']
        #we don't need to worry about fancy URL parsing because Tumblr embedded image URLs are consistent
        ext = tumblr_url.rsplit('.',1)[-1]
        jekyll_path = 'img/embed/{subf}'.format(subf=images_subfolder)
        jekyll_filename = 'img-{ind:02}.{ext}'.format(ind=index,ext=ext,subf=images_subfolder)
        jekyll_url = '{{ site.url }}/' + jekyll_path + '/' + jekyll_filename
        tag['src'] = jekyll_url

        image_urls.append((tumblr_url, jekyll_path, jekyll_filename))

    return image_urls

def download_images(image_urls):
    for tumblr_url, jekyll_path, jekyll_filename in image_urls:
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
    image_urls = fix_images(soup,images_subfolder)

    return tidy(soup), image_urls

def add_jekyll_boilerplate(title,html,origin):
    jekyll_boilerplate = '---\ntitle: {title}\nlayout: article\norigin: {origin}\n---\n{html}'

    return jekyll_boilerplate.format(title=title,html=html,origin=origin)

def generate_filename(title,date,html):
    if title:
        slug = slugify(title)
    else:
        slug = slugify(re.sub('<[^<]+?>', '', html),max_length=50,word_boundary=True)

    return date + '-' + slug

def save_post(post,fetch_images=True, subfolder=""):
    title, date, html, permalink = parse_post(post)

    if subfolder[-1] != '/':
        subfolder += '/'

    if title is None:
        title = 'post-'+ str(post['id'])
    filename = generate_filename(title,date,html)
    html, image_urls = clean_html(html,filename)
    output = add_jekyll_boilerplate(title,html,permalink)

    if fetch_images:
        download_images(image_urls)

    os.makedirs('posts/'+subfolder,exist_ok=True)
    file = open('posts/' + subfolder + filename+'.html','w', encoding='utf8')
    file.write(output)
    file.close()
    print('processed',filename)