from argparse import ArgumentParser

from downloader import save_post
from list_ids import get_all_source_ids

# read id off command line
parser = ArgumentParser(description='Download Tumblr text posts and format for Jekyll.')
parser.add_argument('--id',help='ID of the post to download',default=None)
parser.add_argument('--reblogger',help='Name of Tumblr blog containing reblogs of all posts to download',default='dldqdot')
parser.add_argument('--source',help='Name of Tumblr blog containing source posts to download',default='canmom')
parser.add_argument('--prev_source_url',help='Previous url of source that may appear in reblog trails',default='canonicalmomentum')
args=parser.parse_args()

if args.id is not None:
    save_post(args.source, args.id)
else:
    post_ids = get_all_source_ids(args.reblogger, args.prev_source_url)

    for post_id in post_ids:
        print('Identified post',post_id)
        save_post(args.source, post_id)