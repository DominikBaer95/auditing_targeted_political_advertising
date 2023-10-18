# Auditing Targeted Political Advertising on Social Media During the 2021 German Election

This repository contains the code for the implementation of “Auditing Targeted Political Advertising on Social Media During the 2021 German Election.” 

## Abstract

Political advertising on social media has become a central element in election campaigns. However, granular information about political advertising on social media was previously unavailable, thus raising concerns regarding fairness, accountability, and transparency in electoral processes. In this paper, we analyze targeted political advertising on social media using a unique, large-scale dataset of over 80000 political ads from Meta during the 2021 German federal election, with more than $1.1$ billion impressions. For each political ad, our dataset records granular information about targeting strategies, spending, and actual impressions. We then study (i) the prevalence of targeted ads across the political spectrum; (ii) the discrepancies between targeted and actual audiences due to algorithmic distribution; and (iii) what makes an efficient targeting strategy on social media. We find that targeted ads are prevalent across the entire political spectrum, with considerable differences in strategies and efficiency between the political left and right. Furthermore, there are significant discrepancies between the targeted and actual audience, which vary across parties. Notably, the efficiency of political ads (as measured by impressions per EUR) is particularly high when ads are targeted at a broad audience, or published by far-right parties - which raises important fairness concerns. Overall, our work contributes to a better understanding of targeted political advertising on social media and informs policymakers about the design of effective regulatory frameworks to promote fairness, accountability, and transparency.

## Data

All data used for the analysis is publicly available.\
Data on political ads on Facebook and Instagram is available via the Meta Ad Library: https://www.facebook.com/ads/library/ \
Targeting data is available via the Meta Ad Targeting Dataset: https://developers.facebook.com/docs/fort-ads-targeting-dataset/ \
To ensure reproducibility, we provide all ad IDs for all ads in our dataset. Due to Meta's privacy policy, we cannot share any further information.

## Code

Ads are mapped to the corresponding parties using the "mapping_parties_germany.Rmd" file. \
Data from the Meta Ad Library and the Meta Ad Targeting Dataset is merged and preprocessed via "create_DE_data.py." \
The analysis for RQ1 and RQ2 are performed via "paper_figures.ipynb." \
The regression analysis and machine learning approach are implemented in "regression_analysis.ipynb."
