from argparse import ArgumentParser

import util

#go up the reblog history until you find the most recent instance of target_blog
def get_source_id(post,target_blog):
    for past_reblog in reversed(post['trail']):
        if past_reblog['blog']['name'] == target_blog:
            return past_reblog['post']['id']
    print('No reblog from',target_blog,'in trail!')
    return None

def get_all_source_ids(blog, original_blog):
    #determine the number of posts
    bloginfo = util.get_bloginfo(blog,dict())

    n_posts = bloginfo['posts']
    print(n_posts,'posts')
    n_calls = 1 + (n_posts // 20)

    #get IDs
    source_ids = set()

    for i in range(0,n_calls):
        offset = i * 20

        posts = util.get_posts(blog,{'offset' : offset})

        print(len(posts),'posts returned')

        for post in posts:
            source_id = get_source_id(post, original_blog)
            if source_id is not None:
                source_ids.add(source_id)

    return source_ids