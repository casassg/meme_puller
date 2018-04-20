# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:36:19 2018

@author: NSing and @casassg
"""

import datetime
import json
import logging
import time
import urllib.request
from multiprocessing.dummy import Pool as ThreadPool

import praw

'''
******************************
***** USER INPUT SECTION *****
******************************
'''
# initialization variables
IMAGES_TO_PULL = 2000  # int, number of images to pull

REDDIT_PAGE = 'memes'  # str, subreddit to pull from, ex.: 'memes' for r/memes
# REDDIT_PAGE = 'MemeEconomy'  # str, subreddit to pull from, ex.: 'memes' for r/memes
# REDDIT_PAGE = 'dankmemes'  # str, subreddit to pull from, ex.: 'memes' for r/memes
# REDDIT_PAGE = 'ComedyCemetery'  # str, subreddit to pull from, ex.: 'memes' for r/memes
# REDDIT_PAGE = 'wholesomememes'  # str, subreddit to pull from, ex.: 'memes' for r/memes
COMMENTS_TO_PULL = 5  # int, amount of comments to get from each post
SAVE_JSON = True  # bool, save json file?
FILE_NAME = 'memes'  # str, output file name
DOWNLOAD_IMAGES = False  # bool, download images? need to have 'image_data' folder in dir
PULL_FROM = 'top_year'  # str, can be: hot, top_month, top_week, top_day, top_year

logging.basicConfig(
    format='%(thread)d:%(levelname)s:%(message)s',
    level=logging.INFO
)

'''
******************************
******* END USER INPUT *******
******************************
'''

# login to reddit API
REDDIT_CLIENT = praw.Reddit(check_for_updates=True,
                            client_id='hd39fRl0joML-A',
                            client_secret='7S6YELQknSlch7xckf7KX0mZD8Q',
                            user_agent='data pulling script by /u/NickColorado',
                            username='NickColorado', password='MachinesRul3theWorld')

# confirm that reddit is opened in editor mode
assert not REDDIT_CLIENT.read_only, 'Opened in read mode'
logging.info('Grabbing data from r/' + REDDIT_PAGE + ' (' + PULL_FROM + ')...')


# get location to pull from

def get_submissions():
    if PULL_FROM == 'hot':
        return REDDIT_CLIENT.subreddit(REDDIT_PAGE).hot(limit=IMAGES_TO_PULL)
    elif PULL_FROM == 'top_month':
        return REDDIT_CLIENT.subreddit(REDDIT_PAGE).top(time_filter='month', limit=IMAGES_TO_PULL)
    elif PULL_FROM == 'top_day':
        return REDDIT_CLIENT.subreddit(REDDIT_PAGE).top(time_filter='day', limit=IMAGES_TO_PULL)
    elif PULL_FROM == 'top_week':
        return REDDIT_CLIENT.subreddit(REDDIT_PAGE).top(time_filter='week', limit=IMAGES_TO_PULL)
    elif PULL_FROM == 'top_year':
        return REDDIT_CLIENT.subreddit(REDDIT_PAGE).top(time_filter='year', limit=IMAGES_TO_PULL)
    else:
        assert False, 'invalid input option for variable "pull_from" (can be: hot, top_month, top_week, top_day)'


def pull_submission(x):
    i,submission = x
    if (i%50)==0: 
        logging.info('Downloaded %d submissions' % i)
    date = datetime.datetime.fromtimestamp(submission.created)
    # get image url to deconstruct later
    url = submission.url
    if '.jpg' not in url and not '.png' in url:
        logging.error('not an image: %s' % url)
        return None

    # download image file
    file_name = url.split('/')[-1]
    image_path = 'image_data/' + file_name
    if DOWNLOAD_IMAGES:
        try:
            # try to download
            logging.info('%s downloaded' % file_name)
            urllib.request.urlretrieve(url, image_path)
        except Exception as e:
            # skip download if unavailable
            logging.error(e)
            return None

    return {'title': submission.title,
            'top_comments': [c.body for c in submission.comments[:COMMENTS_TO_PULL]],
            'image_url': url,
            'image_file_name': file_name,
            'image_loc': image_path,
            'image_type': (url.split('.')[-1]),
            'score': submission.score,
            'ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'gold_score': submission.gilded,
            'nsfw_tag': submission.over_18,
            'subreddit': (str(submission.subreddit)),
            'year': date.year,
            'month': date.month,
            'day': date.day}


if __name__ == '__main__':
    pool = ThreadPool()
    logging.info('Pulling with %s processes' % pool._processes)
    start = time.time()
    # Multi-threaded version
    infos = pool.map(pull_submission, enumerate(get_submissions()))
    # Single threaded version
    # infos = [pull_submission(s) for s in get_submissions()]
    end = time.time()
    logging.info('Time taken: %s seconds ' % (end - start))
    infos = list(filter(bool, infos))
    if SAVE_JSON == True:
        with open(FILE_NAME + '.json', 'w') as fp:
            json.dump(infos, fp)
            logging.info('JSON file saved.')
    logging.info('total grabbed: %s ' % len(infos))
