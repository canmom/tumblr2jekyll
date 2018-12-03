import requests
from requests_oauthlib import OAuth1

base_url = "https://api.tumblr.com/v2/blog/"

with open('api-keys.txt') as keyfile:
    keys = [key.strip() for key in keyfile]
    keyfile.close()

auth = OAuth1(*keys)

def api_url(blog,method):
    return "{0}{1}.tumblr.com/{2}".format(base_url,blog,method)

def get(blog,method,params):
    url = api_url(blog,method)
    # params.update({'api_key': keys[0]})

    response = requests.get(url,auth=auth,params=params)
    response.raise_for_status()

    print('response received at',response.url)

    return response.json()['response']

def get_posts(blog,params):
    return get(blog,'posts',params)['posts']

def get_bloginfo(blog,params):
    return get(blog,'info',params)['blog']
    