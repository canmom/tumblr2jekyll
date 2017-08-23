from argparse import ArgumentParser

from single import get_post
from sources import get_all_source_ids
from tag import get_tag

# read id off command line
parser = ArgumentParser(description='Download Tumblr text posts and format for Jekyll.')
parser.add_argument('--id',help='ID of the post to download',default=None)
parser.add_argument('--reblogger',help='Name of Tumblr blog containing reblogs of all posts to download')
parser.add_argument('--source',help='Name of Tumblr blog containing source posts to download',default='canmom')
parser.add_argument('--prev_source_url',help='Previous url(s) of source that may appear in reblog trails',default={'canonicalmomentum','canmom'},nargs='*')
parser.add_argument('--no_images',help='Do not download images (e.g. because you have already downloaded them and want to update HTML only).',action='store_true')
parser.add_argument('--tag',help='Download all posts with a particular tag from a blog')
parser.add_argument('--subfolder',help="subfolder of ./posts to save posts into, creating if necessary",default='')
args = parser.parse_args()

if args.id is not None:
    get_post(args.source, args.id, fetch_images = not args.no_images,subfolder = args.subfolder)
elif args.reblogger is not None:
    post_ids = get_all_source_ids(args.reblogger, set(args.prev_source_url))

    for post_id in post_ids:
        print('Identified post',post_id)
        get_post(args.source, post_id, fetch_images = not args.no_images, subfolder = args.subfolder)
elif args.tag is not None:
    get_tag(args.source, args.tag, fetch_images = not args.no_images, subfolder = args.subfolder)
else:
    parser.print_help()