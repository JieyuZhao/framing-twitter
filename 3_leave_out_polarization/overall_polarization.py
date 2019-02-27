#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import pandas as pd
import json
import sys
from calculate_leaveout_polarization import get_leaveout_value

DATA_DIR = '../data/'
TWEET_DIR = '../data/tweets/'


events = open(DATA_DIR + 'event_names.txt', 'r').read().splitlines()
print(events)

def get_polarization(event, method = "nofilter", cluster_method = None):
    '''

    :param event: name of the event (str)
    :param method: "nofilter" (default): use all tweets
                    "noRT": ignore retweets only
                    "cleaned": keep only tweets that are in "cleaned tweets" (i.e. they have words from the vocab);
                                note that this is a subset of tweets in "noRT"
                    "clustered": keep only tweets that were assigned to clusters; this is a subset of "cleaned
    :param cluster_method: None, "relative" or "absolute" (see 5_assign_tweets_to_clusters.py); must have relevant files
    :return: tuple: (true value, random value)
    '''
    data = pd.read_csv(TWEET_DIR + event + '/' + event + '.csv', sep='\t', lineterminator='\n', usecols=['text', 'timestamp', 'user_id', 'dem_follows', 'rep_follows', 'remove', 'isRT'])
    if method == "noRT":
        data = data[~data['remove'] & ~data['isRT']]
    elif method in ["cleaned", 'clustered']:
        indices = np.load(TWEET_DIR + event + '/' + event + '_cleaned_and_partisan_indices.npy')  # tweets with embeddings
        data = data.iloc[indices]
        if method == "clustered":
            data.reset_index(drop=True, inplace=True)
        if cluster_method:
            cluster_method = '_' + cluster_method
        else:
            cluster_method = ''
        assigned_indices = np.load(
            TWEET_DIR + event + '/' + event + '_cluster_assigned_embed_indices' + cluster_method + '.npy')
        data = data.iloc[assigned_indices]
    elif method != "nofilter":
        print("invalid method.")
        return None

    print(event, len(data))
    return get_leaveout_value(event, data)

if __name__ == "__main__":
    event_polarization = {}
    method = sys.argv[1]
    cluster_method = None if len(sys.argv) < 3 else sys.argv[2]
    for e in events:
        event_polarization[e] = tuple(get_polarization(e, method))

    if cluster_method:
        cluster_method = '_' + cluster_method
    else:
        cluster_method = ''
    with open(DATA_DIR + 'polarization_' + method + cluster_method + '.json', 'w') as f:
        f.write(json.dumps(event_polarization))