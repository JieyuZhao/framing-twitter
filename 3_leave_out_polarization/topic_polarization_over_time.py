#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import copy
import gc
import json
import sys

import pandas as pd
from joblib import Parallel, delayed
from calculate_leaveout_polarization import get_leaveout_value
sys.path.append('..')
from helpers.funcs import *

# NOTE: only use this for events where there is enough (temporal) data, otherwise it'll be very noisy

config = json.load(open('../config.json', 'r'))
INPUT_DIR = config['INPUT_DIR']
TWEET_DIR = config['TWEET_DIR']
NUM_CLUSTERS = config['NUM_CLUSTERS']
events = open(INPUT_DIR + 'event_names.txt', 'r').read().splitlines()
event_times = json.load(open(INPUT_DIR + "event_times.json","r"))
hour = 60 * 60
day = 24 * hour
split_by = 24 * hour
no_splits = int((day / split_by) * 14)  # 14 days


def get_polarization(event, cluster_method = None):
    '''

    :param event: name of the event (str)
    :param cluster_method: None, "relative" or "absolute" (see 5_assign_tweets_to_clusters.py); must have relevant files
    :return:
    '''
    data = pd.read_csv(TWEET_DIR + event + '/' + event + '.csv', sep='\t', lineterminator='\n',
                       usecols=['user_id', 'text', 'dem_follows', 'rep_follows', 'timestamp'])
    data = get_cluster_assignments(event, data, cluster_method)
    cluster_method = method_name(cluster_method)
    print(event, len(data))

    buckets, _ = get_buckets(data, event_times[event], no_splits, split_by)
    del data
    gc.collect()

    topic_polarization_overtime = {}
    for i, b in enumerate(buckets):
        print('bucket', i)
        topic_polarization = {}
        for j in range(NUM_CLUSTERS):
            print(j)
            t = b[b['topic'] == j]
            topic_polarization[j] = tuple(get_leaveout_value(event,t))
        topic_polarization_overtime[i] = topic_polarization

    with open(TWEET_DIR + event + '/' + event + '_topic_polarization_over_time' + cluster_method + '.json', 'w') as f:
        f.write(json.dumps(topic_polarization_overtime))

cluster_method = None if len(sys.argv) < 2 else sys.argv[1]

Parallel(n_jobs=2)(delayed(get_polarization)(e, cluster_method) for e in ['orlando', 'vegas'])

