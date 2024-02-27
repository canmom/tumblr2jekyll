import util
from process import save_post

def get_post(blog,post_id,options):
    posts = util.get_posts(blog,{'id' : post_id})

    assert len(posts)==1, 'Expected only one post, received ' + str(len(posts))
    post = posts[0]

    try:
        save_post(post,options)
    except NotImplementedError as err:
        print(err)
        print('Response has fields:' + ', '.join(post.keys()))
