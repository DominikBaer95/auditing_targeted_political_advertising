'''
A function to compute gender and age distribution distances between Ad Targeting to the Ad Library data
Written by (30/06/2023)
'''

from map_targeting_age import *
from collections import defaultdict, Counter
import scipy.stats as ss
import numpy as np

def get_targeting_gender_distribution(ad):
    if ad['targeting_gender'] == 'All':
        target_gender_distribution = {'male':0.5, 'female':0.5}
    if ad['targeting_gender'] == "Women":
        target_gender_distribution = {'male':0, 'female':1}
    if ad['targeting_gender'] == "Men":
        target_gender_distribution = {'male':1, 'female':0}
    return target_gender_distribution

def get_actual_age_distribution(ad):
    actual_age_distribution = Counter()
    for age in ['13-17',
       '18-24', '25-34', '35-44', '45-54', '55-64', '65+']:
        p = float(ad[age])
        actual_age_distribution[age] += p
    return actual_age_distribution

def get_targeting_age_distribution(ad):
    mapping = map_age_interval(ad['targeting_age'])
    total = np.sum([mapping[k] for k in mapping])
    new_distribution = Counter()
    for k in mapping:
        new_distribution[k] = mapping[k]/total
    return new_distribution

def gender_distribution_distance(row):
    x = [row['male'], row['female']]
    y = [row['targeting_gender_distribution']['male'], row['targeting_gender_distribution']['female']]
    return ss.wasserstein_distance(x, y)

def get_actual_gender_distribution(ad):
    actual_gender_distribution = Counter()
    for gender in ['male','female']:
        p = float(ad[gender])
        actual_gender_distribution[gender] = p
    return actual_gender_distribution

def age_distribution_distance(row):
    target = row['targeting_age_distribution']
    actual = row['actual_age_distribution']
    age_bins = ['13-17',
           '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    y = [target[k] for k in age_bins]
    x = [actual[k] for k in age_bins]
    return ss.wasserstein_distance(x, y)

