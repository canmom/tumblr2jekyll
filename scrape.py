from util import get_posts, get
from process import save_post

def get_blog(blog, options):
    response = get(blog, 'posts', {'limit': 0})
    total = response['total_posts']
    offsets = range(0,total,20)
    for offset in offsets:
        posts = get_posts(blog,{'offset': offset})
        for post in posts:
            save_post(post, options)
