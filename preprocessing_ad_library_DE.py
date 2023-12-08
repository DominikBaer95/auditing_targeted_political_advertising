"""
A script to preprocess raw ad library data. Written by Dominik Bar and modified by Francesco Pierri (07/2023)
"""

import pandas as pd
import numpy as np
from functools import reduce
import git
import os


# Create data frame which shows demographic distribution of each ad
def expand_demographic_distribution(row):
    df = pd.DataFrame()
    # Check if demographic distribution is available
    if type(row["demographic_distribution"]) == str:
        # Split values by age, gender
        demo_dta = row["demographic_distribution"].split("},")
        df = pd.DataFrame(demo_dta, columns=["dta"])
        df["dta"] = df["dta"].str.replace(r"\{|\}", "", regex=True)
        # Create percentage, age, and gender variables
        df[["percentage", "age", "gender"]] = df["dta"].str.split(",", expand=True)
        # Extract percentage floats
        df["percentage"] = df["percentage"].str.replace("percentage: ", "", regex=True).astype(float)
        # Extract age categories
        df["age"] = df["age"].str.replace("age: ", "", regex=True)
        # Extract gender categories
        df["gender"] = df["gender"].str.replace("gender: ", "", regex=True)
        # Remove leading and trailing whitespace from age and gender
        df[["age", "gender"]] = df[["age", "gender"]].apply(lambda x: x.str.rstrip(), axis=1)
        # Add ad id
        df["id"] = row["id"]
        # Compute impressions for each line
        df["impressions_lb"] = df["percentage"] * row["impressions_lb"]
        df["impressions_ub"] = df["percentage"] * row["impressions_ub"]
        # Drop unnecessary columns
        df = df.drop(columns="dta")
    return df


# Preprocess ad library data
def preprocessing_ad_library(country):

    repo = git.Repo('.', search_parent_directories=True).working_tree_dir
    data_folder = os.path.join(repo, "Data", country) 
    
    ###############################################
    # Load raw library data and preprocess
    ###############################################
    
    print("Reading raw ad library data.")
    # Clean data
    ads_df = pd.read_csv(os.path.join(data_folder, "fb_ad_library_data_DE"+".csv"))
    # Drop index
    if "Unnamed: 0" in ads_df:                      
        ads_df = ads_df.drop(columns="Unnamed: 0")
        
    # Text fields
    # Text fields are framed like this [' text '] but just one ad per content => remove frames
    # Affected columns
    cols = ["ad_creative_bodies", "ad_creative_link_captions", "ad_creative_link_titles", "languages", "publisher_platforms", "ad_creative_link_descriptions"]
    ads_df[cols] = ads_df[cols].replace(r"\[\'|\']|\[\"|\"\]", "", regex=True)

    # Remove line breaks
    ads_df[cols] = ads_df[cols].replace("\\\\n", " ", regex=True)
    # Replace empty lines with nan as in rest of dataset
    ads_df[cols] = ads_df[cols].replace(" ", np.NaN)

    # Create platform indicators
    ads_df["facebook"] = 0
    ads_df["instagram"] = 0

    ads_df.loc[ads_df["publisher_platforms"].str.contains("facebook") == True, "facebook"] = 1
    ads_df.loc[ads_df["publisher_platforms"].str.contains("instagram") == True, "instagram"] = 1

    # Clean spending
    spend = ads_df["spend"].str.extractall(r"(\d+)").astype(float)
    spend_lb = spend.loc[pd.IndexSlice[:, 0], :].reset_index()
    spend_ub = spend.loc[pd.IndexSlice[:, 1], :].reset_index()

    ads_df["spend_lb"] = np.nan
    ads_df["spend_ub"] = np.nan
    ads_df.loc[spend_lb["level_0"], "spend_lb"] = list(spend_lb.iloc[:, 2])
    ads_df.loc[spend_ub["level_0"], "spend_ub"] = list(spend_ub.iloc[:, 2])

    # Clean estimated audience size
    audience = ads_df["estimated_audience_size"].str.extractall(r"(\d+)").astype(float)
    audience_lb = audience.loc[pd.IndexSlice[:, 0], :].reset_index()
    audience_ub = audience.loc[pd.IndexSlice[:, 1], :].reset_index()

    ads_df["audience_lb"] = np.nan
    ads_df["audience_ub"] = np.nan
    ads_df.loc[audience_lb["level_0"], "audience_lb"] = list(audience_lb.iloc[:, 2])
    ads_df.loc[audience_ub["level_0"], "audience_ub"] = list(audience_ub.iloc[:, 2])

    # Clean number of impressions
    impressions = ads_df["impressions"].str.extractall(r"(\d+)").astype(float)
    impressions_lb = impressions.loc[pd.IndexSlice[:, 0], :].reset_index()
    impressions_ub = impressions.loc[pd.IndexSlice[:, 1], :].reset_index()

    ads_df["impressions_lb"] = np.nan
    ads_df["impressions_ub"] = np.nan
    ads_df.loc[impressions_lb["level_0"], "impressions_lb"] = list(impressions_lb.iloc[:, 2])
    ads_df.loc[impressions_ub["level_0"], "impressions_ub"] = list(impressions_ub.iloc[:, 2])

    # Clean demographic distribution
    ads_df["demographic_distribution"] = ads_df["demographic_distribution"].replace("\[|\]|'", "", regex=True)

    # Clean demographics and create extra dataframe
    print("Creating demographics data frame.")
    demographics = []
    _ = ads_df.apply(lambda row: demographics.append(expand_demographic_distribution(row)), axis=1)
    demographics_df = pd.concat(demographics, sort=False).reset_index(drop=True)

    # Drop unformulated columns and save final data
    ads_df = ads_df.drop(columns=["delivery_by_region", "demographic_distribution", "estimated_audience_size", "impressions", "publisher_platforms", "spend"])

    ###############################################
    # Filter library data and reformat
    ###############################################
    
    print("Final preprocessing to create dataframe.")

    # Election date
    election_date = "2021-09-26"

    # Some ads are active after the election date => we have to adjust the number of impressions, audience size, spend
    # For ads without end date, set end data to start date
    ads_df.loc[ads_df.ad_delivery_stop_time.isna(), "ad_delivery_stop_time"] = ads_df.ad_delivery_start_time

    # Compute number of days ad is active before election and in total
    ads_df["days_before_election"] = (pd.to_datetime(election_date) - pd.to_datetime(ads_df.ad_delivery_start_time)).dt.days + 1
    ads_df["days_total"] = (pd.to_datetime(ads_df.ad_delivery_stop_time) - pd.to_datetime(ads_df.ad_delivery_start_time)).dt.days + 1
    ads_df["ad_active"] = ads_df["days_before_election"] / ads_df["days_total"]
    ads_df.loc[ads_df.ad_delivery_stop_time <= election_date, "ad_active"] = 1

    # Facebook does not report upper bounds for impressions, audience size, and spend for very large ads => use lower bound for conservative estimates
    ads_df.loc[ads_df.impressions_ub.isna(), "impressions_ub"] = ads_df.impressions_lb
    ads_df.loc[ads_df.audience_ub.isna(), "audience_ub"] = ads_df.audience_lb
    ads_df.loc[ads_df.spend_ub.isna(), "spend_ub"] = ads_df.spend_lb

    # Average lower and upper bounds for impressions, audience size, and spend
    ads_df["impressions"] = ads_df["impressions_lb"] + ads_df["impressions_ub"] / 2
    ads_df["spend"] = ads_df["spend_lb"] + ads_df["spend_ub"] / 2
    ads_df["audience"] = ads_df["audience_lb"] + ads_df["audience_ub"] / 2

    # Adjust number of impressions, audience size, and spend for ads that are active after the election date
    ads_df[["impressions", "spend", "audience"]] = ads_df[["impressions", "spend", "audience"]].apply(lambda x: x*ads_df["ad_active"])

    # Create platform indicators (1 = Facebook only, 2 = Instagram only, 3 = Facebook and Instagram)
    ads_df["platform"] = np.nan
    ads_df.loc[(ads_df["facebook"] == 1) & (ads_df["instagram"] == 0), "platform"] = 1
    ads_df.loc[(ads_df["facebook"] == 0) & (ads_df["instagram"] == 1), "platform"] = 2
    ads_df.loc[(ads_df["facebook"] == 1) & (ads_df["instagram"] == 1), "platform"] = 3

    # Drop unnecessary columns
    ads_df = ads_df.drop(columns=["ad_creative_link_captions", "ad_creative_link_titles", "ad_snapshot_url", "ad_creative_link_descriptions", "days_before_election", "days_total", "ad_active"])

    ###############################################
    # Preprocess demographic data
    ###############################################

    # Demographic
    # Create gender share per ad
    gender = demographics_df[["id", "percentage", "gender"]].groupby(by=["id", "gender"]).agg(
        {"percentage": "sum"}).reset_index()
    gender = gender.pivot(index="id", columns="gender", values="percentage").reset_index().fillna(0)
    gender = gender.rename(columns=lambda x: x.strip())
    gender = gender.rename(columns={"All (Automated App Ads)": "automated_ads_gender", "unknown": "unknown_gender"})

    # Create age share per ad
    age = demographics_df[["id", "percentage", "age"]].groupby(by=["id", "age"]).agg(
        {"percentage": "sum"}).reset_index()
    age = age.pivot(index="id", columns="age", values="percentage").reset_index().fillna(0)
    age = age.rename(columns=lambda x: x.strip())
    age = age.rename(columns={"All (Automated App Ads)": "automated_ads_age", "Unknown": "unknown_age"})

    ###############################################
    # Join ads and demographic data
    ###############################################

    data_frames = [ads_df, gender, age]

    final_df = reduce(lambda left, right: pd.merge(left, right, on="id", how="left"), data_frames)

    # Save preprocessed ad library data
    print("Saving final dataframe.")
    final_df.to_csv(os.path.join(data_folder, "fb_ad_library_preprocessed_DE"+".csv"), sep=",", index=False)


if __name__=="__main__":
    for country in ["Germany"]:
        try:
            preprocessing_ad_library(country)
        except Exception as e:
            print(e)



