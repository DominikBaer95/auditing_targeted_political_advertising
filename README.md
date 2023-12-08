# Auditing Targeted Political Advertising on Social Media During the 2021 German Election

  

This repository contains the code for the implementation of “Auditing Targeted Political Advertising on Social Media During the 2021 German Election.”

  

## Abstract

  

Political advertising on social media has become a central element in election campaigns. However, granular information about political advertising on social media was previously unavailable, thus raising concerns regarding fairness, accountability, and transparency in electoral processes. In this paper, we analyze targeted political advertising on social media using a unique, large-scale dataset of over 80000 political ads from Meta during the 2021 German federal election, with more than 1.1 billion impressions. For each political ad, our dataset records granular information about targeting strategies, spending, and actual impressions. We then study (i) the prevalence of targeted ads across the political spectrum; (ii)~the discrepancies between targeted and actual audiences due to algorithmic distribution; and (iii)~what are targeting strategy on social media with far reach at low cost. We find that targeted ads are prevalent across the entire political spectrum, with considerable differences in strategies and reach for a given budget between the political left and right. Furthermore, there are significant discrepancies between the targeted and actual audience, which vary across parties. Notably, the reach of political ads for a given budget (as measured by impressions per EUR) is particularly high when ads are targeted at a broad audience, or published by far-right parties---which raises important fairness concerns. Overall, our work contributes to a better understanding of targeted political advertising on social media and informs policymakers about the design of effective regulatory frameworks to promote fairness, accountability, and transparency.

  

## Data

  

All data used for the analysis is publicly available.

Data on political ads on Facebook and Instagram is available via the Meta Ad Library: https://www.facebook.com/ads/library/

Targeting data is available via the Meta Ad Targeting Dataset: https://developers.facebook.com/docs/fort-ads-targeting-dataset/

To ensure reproducibility, we provide ids for all ads in our dataset, which can be used to retrieve the original data through Meta Ad Library (both through the API and with the web interface by simply using the id as query). Due to Meta's ToS we cannot share any further information.

## Code

Scripts to reproduce our results should be run in the following order:

 1. Collect all ads from the Meta Ad library and the Ad Targeting dataset using the ad IDs provided in the file `DE_fb_ids.csv` and save it as `fb_ad_library_data.csv` in a folder named "Data" in your repository.
 2. Execute the file `preprocessing_ad_library_DE.py` for initial preprocessing.
 3. Map all ads to the corresponding party using `mapping_parties_germany.Rmd`.
 4. Data from the Meta Ad Library and the Meta Ad Targeting Dataset is merged and preprocessed via `create_DE_data.py`.
 5. The analysis for RQ1 and RQ2 are performed via `paper_figures.ipynb`.
 6. The regression analysis and machine learning approach are implemented in `regression_analysis.ipynb`.
