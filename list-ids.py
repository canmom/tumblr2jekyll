from argparse import ArgumentParser

import util

parser = ArgumentParser(description='Go through every text post on a blog and save the post ID of the reblog source')
parser.add_argument('--blog',help='name of the tumblr blog to download posts from',default='dldqdot')
args=parser.parse_args()

#determine the number of posts
bloginfo = util.get_bloginfo(args.blog,{})

n_posts = bloginfo['posts']
print(n_posts,'posts')
n_calls = 1 + (n_posts // 20)

post_ids = set()

for i in range(0,n_calls):
    offset = i * 20

    posts = util.get_posts(args.blog,{'offset' : offset})

    print(len(posts),'posts returned')

    post_ids.update(post['id'] for post in posts)

print(post_ids)