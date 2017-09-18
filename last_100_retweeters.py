# -*- coding: UTF-8 -*-

#=========================================================================================#
# Retrieves metadata of last 100 retweeters for given tweet using /statuses/retweets/     #
#                           Lawrence Alexander @LawrenceA_UK                              #
#=========================================================================================#

import requests, json, time, codecs, sys
import requests_cache
import math
import argparse
from requests_oauthlib import OAuth1

# Parse command line arguments
ap = argparse.ArgumentParser()
ap.add_argument ("-i","--tweetid",required=True,help="ID of tweet from which to collect account data")
arguments = vars(ap.parse_args())

# Initialize http cache
requests_cache.install_cache(cache_name='tweet-amp-cache', backend='sqlite', expire_after=None)

# Set tokens and keys for API

client_key = ''
client_secret =''
token = ''
token_secret =''

# Base for Twitter API calls

base_twitter_url = "https://api.twitter.com/1.1/"

# Auth setup

oauth = OAuth1(client_key,client_secret,token,token_secret)

# Function to get last 100 accouunts retweeting a given tweet

def last_100_retweets(tweet_id):    
    api_url = "%s/statuses/retweets/%s.json?" % (base_twitter_url,tweet_id)
    api_url += "count=100"  
    # Send request
    response = requests.get(api_url,auth=oauth)    
    if response.status_code == 200:
        tweet = json.loads(response.content)
        return tweet
    else:
        print "[!] Error accessing Twitter API. Failed with code %d." % response.status_code
    return None

# This function calculates username Shannon entropy

def calc_entropy(in_string):
    count = 0
    letter_probabilities = []
    entropy = []  
    # Count letter frequencies
    for the_letter in in_string:       
        for countletters in in_string:
            if countletters == the_letter:
                count = count + 1 
        letter_probabilities.append(float(count) / len (in_string)) 
        count =0        
    # Calculate entropy 
    for probability in letter_probabilities:    
        entropy.append(probability * math.log(probability,2))
    entropy = -sum(entropy)
    return entropy

# Get last 100 accounts retweeting given status

tweet_id=arguments['tweetid']
print "[*] Getting retweeters for tweet ID: %s..." % tweet_id
retweeters = last_100_retweets(tweet_id)

# Iteratively write account data to CSV

outputfile = "last-100-retweeters-%s.csv" % tweet_id
outfile = codecs.open(outputfile, 'wb', 'utf-8')
outfile.write('User ID' + ',' + 'Username' + ',' + 'Source' + ',' + 'Creation Date' + ',' + 'Language' + ',' + 'Time Zone' + ',' 'UTC Offset' + ',' + 'Withheld In' + ',' + 'Username Entropy' + u"\n")
for account in retweeters:
    creation_date = account['user']['created_at']
    user_id = account['user']['id_str']
    try:
        screen_name = account['user']['screen_name']
    except:
        screen_name=""
        pass
    language = account['user']['lang']
    try:
        time_zone = account['user']['time_zone']
    except:
        time_zone = ""
        pass
    try:    
        utc = account['user']['utc_offset']
    except:
        utc = ""
        pass
    try:
        withheld = account['user']['withheld_in_countries']
    except:
        withheld = ""
    try:
        source = account['user']['status']['source']
    except:
        source = ""
    entropy = calc_entropy(screen_name)    
    outfile.write(user_id + ',' + screen_name + ',' + source + ',' + creation_date + ',' + language + ',' + str(time_zone) + ',' + str(utc) + ',' + withheld + ',' + str(entropy) + u"\n") 
   
outfile.close()
print "[*] File successfully written as: %s." % outputfile