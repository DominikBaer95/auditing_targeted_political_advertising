# Importing libraries
import pandas as pd
import git
import os
import ast
from collections import defaultdict
from germansentiment import SentimentModel
import sys
sys.path.append('../analysis/')
from age_gender_distribution_distances import *

# Getting the Data folder name ---> we might want a config file
repo = git.Repo('.', search_parent_directories=True).working_tree_dir
path_data = os.path.join(repo, "Data")

'''
Custom functions
'''


# extract targeting categories
def get_unique_categories_include(data):
    unique_categories = defaultdict(set)
    for vals in data['include'].astype(str).unique():
        vals = eval(bytes(vals, "utf-8").decode("unicode_escape"))
        if not vals:
            continue
        for group in vals:
            for val in group:
                key = group[val]
                unique_categories[key].add(val)
    return unique_categories


def get_unique_categories_exclude(data):
    unique_categories = defaultdict(set)
    for vals in data['exclude'].astype(str).unique():
        vals = eval(bytes(vals, "utf-8").decode("unicode_escape"))
        if not vals:
            continue
        if isinstance(vals, list):  # to handle one exception in DE data
            for group in vals:
                for val in group:
                    key = group[val]
                    unique_categories[key].add(val)
        else:
            group = vals
            for val in group:
                key = group[val]
                unique_categories[key].add(val)
    return unique_categories


# extract targeting criteria
def extract_targeting_criteria(ad, var):
    vals = ad[var]
    vals_conv = eval(bytes(vals, "utf-8").decode("unicode_escape"))

    cat_vals = defaultdict(list)

    if isinstance(vals_conv, list):  # to handle one exception in DE data
        for group in vals_conv:
            for val in group:
                cat = group[val]
                cat_vals[cat].append(val)
    else:
        group = vals_conv
        for val in group:
            cat = group[val]
            cat_vals[cat].append(val)

    for category in cat_vals:
        colname = category.replace(" ", "_").lower() + "_" + var
        ad[colname] = cat_vals[category]
    return ad


'''
 Read and join data
'''

# Ad library data
ad_lib = pd.read_csv(os.path.join(path_data, 'Germany/fb_ad_library_mapped_party_DE.csv'), encoding='utf-8', dtype={'id': str})


# Create country indicator
ad_lib["country_id"] = "DE"

# Targeting data
targeting = pd.read_csv(os.path.join(path_data, 'Germany/fb_targeting_DE.csv'), encoding='utf-8', dtype={'archive_id': str})
targeting_location = pd.read_csv(os.path.join(path_data, 'Germany/fb_targeting_DE_location.csv'), encoding='utf-8', dtype={'archive_id': str})
targeting = targeting.merge(targeting_location, how='left', left_on='archive_id', right_on='archive_id')

# Join ad library and targeting data
df = ad_lib.merge(targeting, how='inner', left_on='id', right_on='archive_id')

# Filter ads published before 01/07/2021
df = df[df["ad_delivery_start_time"] >= "2021-07-01"]

'''
 Create additional variables
'''

# Impressions per spending
df["impressions_per_spending"] = df["impressions"] / df["spend"]

# Ad duration
df["ad_duration"] = pd.to_datetime(df["ad_delivery_stop_time"]).dt.date - pd.to_datetime(df["ad_delivery_start_time"]).dt.date + pd.Timedelta(days=1)

# Weekday of ad start (Monday = 0, Sunday = 6)
df["weekday_start"] = pd.to_datetime(df["ad_delivery_start_time"]).dt.weekday

# Weekday of ad end (Monday = 0, Sunday = 6)
df["weekday_end"] = pd.to_datetime(df["ad_delivery_stop_time"]).dt.weekday


'''
 Preprocess targeting data
'''

# The columns include and exclude contain different targeting categories (e.g., interests, behaviors, employers, etc.)
# We want to create a column for each category and populate it with the corresponding targeting criteria

# # Create a set containing all targeting categories
unique_categories_include = get_unique_categories_include(df)
unique_categories_exclude = get_unique_categories_exclude(df)

# Create column for each targeting category with indicator whether the category was used for targeting
# Extract targeting criteria for each category
df = df.apply(lambda x: extract_targeting_criteria(x, "include"), axis=1)
df = df.apply(lambda x: extract_targeting_criteria(x, "exclude"), axis=1)

# df = df.rename(columns={'include':'include_raw', 'exclude':'exclude_raw'})

# filling NaN with False and dropping two weird rows
df = df[df["spend"].notna()]
df = df.fillna(False)

#df = df.drop("include_location", axis=1)

# Create list of targeting columns
# targeting_include_columns = [c for c in df.columns if "include" in c and "raw" not in c and "location" not in c]
# targeting_exclude_columns = [c for c in df.columns if "exclude" in c and "raw" not in c]
targeting_include_columns = [x.replace(" ", "_").lower() + "_include" for x in list(unique_categories_include.keys())]
targeting_exclude_columns = [x.replace(" ", "_").lower() + "_exclude" for x in list(unique_categories_exclude.keys())]
targeting_columns = targeting_include_columns + targeting_exclude_columns


# Create variables indicating whether targeting criteria have been used and count of criteria used
for colname in targeting_columns:
    # Create dummy indicating whether targeting category has been used
    use = df[colname].apply(lambda x: 1 if x else 0)
    # Count number of criteria for each ad (only for categories)
    count = df[colname].apply(lambda x: len(x) if isinstance(x, list) is True else 0)
    # Create name for use dummy
    col_use = colname + "_use"
    # Create name for count column
    col_count = colname + "_count"
    # Add columns to dataframe
    df = pd.concat([df, use.rename(col_use), count.rename(col_count)], axis=1)

# # Reformat other targeting criteria
include_other = [c for c in df.columns if c.startswith("include_") and "raw" not in c and "location" not in c]
exclude_other = [c for c in df.columns if c.startswith("exclude_") and "raw" not in c and "location" not in c]

for col in include_other:
    df[col] = df[col].apply(lambda x: 1 if x is True else 0)

for col in exclude_other:
    df[col] = df[col].apply(lambda x: 1 if x is True else 0)

df["exclude_location"] = [1 if v == 1 else 0 for v in df["exclude_location"]]

exclude_other.append("exclude_location")

# Compute total number of targeting criteria used
targeting_include_count = [x + "_count" for x in targeting_include_columns]
targeting_exclude_count = [x + "_count" for x in targeting_exclude_columns]
df["include_count"] = df[targeting_include_count].sum(axis=1)
df["exclude_count"] = df[targeting_exclude_count].sum(axis=1)
df["total_count"] = df["include_count"] + df["exclude_count"] + df[include_other].sum(axis=1) + df[exclude_other].sum(axis=1)

# Dropping useless columns
df = df.drop(["ds", "archive_id"], axis=1)

# Renaming some columns
df = df.rename(columns={'age': 'targeting_age', 'gender': 'targeting_gender', 'include': 'include_raw', 'exclude': 'exclude_raw'})

# Age/Gender distribution variables
df['targeting_gender_distribution'] = [get_targeting_gender_distribution(row) for _, row in df.iterrows()]
df['actual_age_distribution'] = [get_actual_age_distribution(row) for _, row in df.iterrows()]
df['targeting_age_distribution'] = [get_targeting_age_distribution(row) for _, row in df.iterrows()]
df['actual_gender_distribution'] = [get_actual_gender_distribution(row) for _, row in df.iterrows()]
df['gender_distribution_distance'] = df.apply(gender_distribution_distance, axis=1)
df['age_distribution_distance'] = df.apply(age_distribution_distance, axis=1)

''' 
 Sentiment analysis
'''

# Remove ads with no text
ads_text = df[df["ad_creative_bodies"].notnull()]

# Check non-German ads
ads_text_non_german = ads_text[ads_text["languages"] != "de"]  # 1601 ads => 1.6 % of ads with text
# Most ads are still German but classified as nan; Some are in Russian, Turkish English, etc. but very few

model = SentimentModel()

# Initialize empty lists to store results
results = []

# Loop over each input text
for i in range(len(ads_text)):
    # Get the input text
    text = ads_text.iloc[i]["ad_creative_bodies"]

    # Predict sentiment
    classes, probabilities = model.predict_sentiment([text], output_probabilities=True)

    # Extract the values
    sentiment_class = classes[0]
    positive_prob = probabilities[0][0][1]
    negative_prob = probabilities[0][1][1]
    neutral_prob = probabilities[0][2][1]

    # Append the results to the list
    results.append([ads_text.iloc[i]["id"], sentiment_class, positive_prob, negative_prob, neutral_prob])

# Create a DataFrame from the list of results
sentiment = pd.DataFrame(results, columns=['id', 'sentiment_class', 'sentiment_positive', 'sentiment_negative', 'sentiment_neutral'])

# Merge sentiment analysis results with main dataframe
df = df.merge(sentiment, how='left', left_on='id', right_on='id')

# Save final dataframe
df.to_csv(os.path.join(path_data, "DE_merged_data.csv"), encoding='utf-8', index=False)
df.to_pickle(os.path.join(path_data, "DE_merged_data.pkl"))
