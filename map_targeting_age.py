'''
A function to map age intervals from the Ad Targeting to the Ad Library data
Written by (30/06/2023)
'''

# A function to compute overlap between two intervals
def get_overlap(interval1, interval2):
    """
    Given [0, 4] and [1, 10] returns [1, 4]
    """
    if interval2[0] <= interval1[0] <= interval2[1]: 
        start = interval1[0]
    elif interval1[0] <= interval2[0] <= interval1[1]:
        start = interval2[0]
    else:
        return 0

    if interval2[0] <= interval1[1] <= interval2[1]:
        end = interval1[1]
    elif interval1[0] <= interval2[1] <= interval1[1]:
        end = interval2[1]
    else:
        return 0

    return [start, end]

# A function to map an age interval from Targeting data to the bins specified in the Ad Library
def map_age_interval(age_interval_str):
    mapping = dict()
    age_interval = age_interval_str.replace("+", "") # changing "65+"" in 65
    
    left = int(age_interval.split(" - ")[0])
    if age_interval.split(" - ").__len__() == 1:
        right = left
    else:
        right = int(age_interval.split(" - ")[1])

    for age_bin_str in ['13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']:
        if age_bin_str == "65+":
            age_bin = [65, 65]
        else:
            age_bin = [int(i) for i in age_bin_str.split("-")]
            
        overlap = get_overlap([left, right], age_bin)

        # computer percentage of overlap
        if overlap == 0:
            mapping[age_bin_str] = 0
        elif overlap == age_bin:
            mapping[age_bin_str] = 1
        else:
            mapping[age_bin_str] = (overlap[1] - overlap[0] + 1)/(age_bin[1] - age_bin[0] + 1)
            
    return mapping

if __name__ == "__main__":
    example = '15 - 48'
    result = map_age_interval(example)
    print(result)
    # It will print: {'13-17': 0.6, '18-24': 1, '25-34': 1, '35-44': 1, '45-54': 0.4, '55-64': 0,'65+': 0}
