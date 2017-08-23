from util import get_posts, get
from process import save_post

def get_tag(blog, tag, fetch_images = True, subfolder = ""):
    response = get(blog, 'posts', {'tag':tag, 'limit': 0})
    total = response['total_posts']
    offsets = range(0,total,20)
    for offset in offsets:
        posts = get_posts(blog,{'tag': tag, 'offset': offset})
        for post in posts:
            save_post(post, fetch_images, subfolder)
