import requests

base_url = "https://api.tumblr.com/v2/blog/"

with open('api-keys.txt') as keyfile:
    keys = [key.strip() for key in keyfile]
    keyfile.close()

def posts_url(blog):
    return "{0}{1}.tumblr.com/posts".format(base_url,blog,keys[0])

def get_posts(blog,params):
    url = posts_url(blog)
    params.update({'api_key': keys[0]})

    response = requests.get(url,params=params)
    response.raise_for_status()

    posts = response.json()['response']['posts']
    return posts
