# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:36:19 2018

@author: NSing
"""


'''
******************************
***** USER INPUT SECTION *****
******************************
'''
# initialization variables 
amount_to_pull = 10               # int, number of images to pull
indefinite = True                 #bool, if true: pulls images until amount_to_pull is reached

reddit_page = 'memes'              # str, subreddit to pull from, ex.: 'memes' for r/memes
number_of_comments_to_pull = 5     # int, amount of comments to get from each post
save = True                        # bool, save json file? 
save_name = 'reddit_memes_data_top_month_5_4_2'    # str, output file name
download = False                    # bool, download images? need to have 'image_data' folder in dir
pull_from = 'top_year'            # str, can be: hot, top_month, top_week, top_day, top_year
verbose = True                     # bool, verbosity of run 
verbose_acc = 1                    # int, how often to update image grabbing verbosity

specify_month = True          # bool, pull_from must be = 'top_year', whether to screen by month
choose_month = 2              # int, if specify_month == True, this is the month to pull from. [1-12]

'''
******************************
******* END USER INPUT *******
******************************
'''



import praw # need to install using: conda install -c conda-forge praw 
import json
import urllib.request
import datetime

# error handling for using specify_month
if specify_month: assert pull_from == 'top_year', 'Cannot specify a month unless pulling from top_year'

# login to reddit API
reddit = praw.Reddit(check_for_updates = True,
                     client_id='hd39fRl0joML-A',
                     client_secret='7S6YELQknSlch7xckf7KX0mZD8Q',
                     user_agent='data pulling script by /u/NickColorado',
                     username='NickColorado', password='MachinesRul3theWorld')

# confirm that reddit is opened in editor mode
print('page accessed? '+str(reddit.read_only == False)) 

# initialize dictionary
json_file = {}

if verbose: print('Grabbing data from r/'+reddit_page+' ('+pull_from+')...'); 
itt = 0
add_zeros = len(str(amount_to_pull))

# get location to pull from
if indefinite:
    if pull_from == 'hot': loc = reddit.subreddit(reddit_page).hot()
    elif pull_from == 'top_month': loc = reddit.subreddit(reddit_page).top(time_filter = 'month')
    elif pull_from == 'top_day': loc = reddit.subreddit(reddit_page).top(time_filter = 'day')
    elif pull_from == 'top_week': loc = reddit.subreddit(reddit_page).top(time_filter = 'week')
    elif pull_from == 'top_year': loc = reddit.subreddit(reddit_page).top(time_filter = 'year')
    else: assert False, 'invalid input option for variable "pull_from" (can be: hot, top_month, top_week, top_day)'
else:
    if pull_from == 'hot': loc = reddit.subreddit(reddit_page).hot(limit = amount_to_pull)
    elif pull_from == 'top_month': loc = reddit.subreddit(reddit_page).top(time_filter = 'month', limit = amount_to_pull)
    elif pull_from == 'top_day': loc = reddit.subreddit(reddit_page).top(time_filter = 'day', limit = amount_to_pull)
    elif pull_from == 'top_week': loc = reddit.subreddit(reddit_page).top(time_filter = 'week', limit = amount_to_pull)
    elif pull_from == 'top_year': loc = reddit.subreddit(reddit_page).top(time_filter = 'year', limit = amount_to_pull)
    else: assert False, 'invalid input option for variable "pull_from" (can be: hot, top_month, top_week, top_day)'

# parse submission data to json file
for submission in loc:
    # loop initialization
    image_exists = False; month_skip = False
    itt += 1
    if itt % verbose_acc == 0 and verbose and indefinite: print('Grabbing: '+str(itt))
    elif itt % verbose_acc == 0 and verbose: print('Grabbing: '+str(itt)+' of '+str(amount_to_pull))
    
    # get title of post
    title = submission.title
    
    # get top comments
    comment_list = []
    comments = submission.comments
    if len(comments) >= number_of_comments_to_pull:
        for top_comments in comments[:number_of_comments_to_pull]:
            comment = top_comments.body
            comment_list.append(comment)
    else:
        for top_comments in comments:
            comment = top_comments.body
            comment_list.append(comment)
    
    # get upvotes, ratio, comment number, gilded, NSFW, subreddit, time info
    score = submission.score
    ratio = submission.upvote_ratio
    num_comments = submission.num_comments
    gold = submission.gilded
    nsfw = submission.over_18
    subreddit = str(submission.subreddit)
    date = datetime.datetime.fromtimestamp(submission.created)
    year = date.year
    month = date.month
    day = date.day   
    
    # screen based on month
    if specify_month and month != choose_month:
        month_skip = True; itt -= 1
        if verbose: print('Skip due to wrong month.')
    
    # get image url to deconstruct later
    url = submission.url
    if '.jpg' in url: image_url = url; image_exists = True;  image_type = 'jpg'
    elif '.png' in url: image_url = url; image_exists = True; image_type = 'png'
    else: 
        if verbose: print('not an image: '+url); 
        itt -= 1
    
    # save info in dictionary
    if image_exists and month_skip == False:
        # download image file
        if download == True:
            image_file_name = image_url.split('/')[-1]
            try:
                # try to download
                urllib.request.urlretrieve(image_url, 'image_data/'+image_file_name)
                info = {'title': title, 'top_comments': comment_list, 
                        'image_url': image_url, 'image_file_name': image_file_name,
                        'image_loc': 'image_data/'+image_file_name, 'image_type': image_type,
                        'score': score, 'ratio': ratio, 'num_comments': num_comments,
                        'gold_score': gold, 'nsfw_tag': nsfw,
                        'subreddit': subreddit, 'year': year,
                        'month': month, 'day': day}
                skip = False
            except:
                # skip download if unavailable
                if verbose: print('image access restricted'); 
                skip = True; itt -= 1
        else:
            info = {'title': title, 'top_comments': comment_list, 'image_url': image_url,
                    'score': score, 'ratio': ratio, 'num_comments': num_comments,
                    'gold_score': gold, 'nsfw_tag': nsfw,
                    'subreddit': subreddit, 'year': year,
                    'month': month, 'day': day}
            skip = False
        
        
        # save to json file
        if skip == False:
            itt_len = len(str(itt))
            zeros = '0'*(add_zeros-itt_len)
            name_tag = 'meme_'+zeros+str(itt)
            json_file[name_tag] = info
    
    # break once proper number pulled
    if indefinite and itt == amount_to_pull:
        print('Finishing. (limit reached)')
        break
    
if save == True:
    with open(save_name+'.json', 'w') as fp:
        json.dump(json_file, fp)
    if verbose: print('JSON file saved.')

if verbose:
    print('total grabbed: '+str(itt))

        
'''   to open json file   '''
#with open(save_name + '.json', 'r') as fp:
#    data = json.load(fp)