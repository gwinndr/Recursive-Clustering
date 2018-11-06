# Recursive-Clustering
Original paper found here: https://tars.clarkson.edu/papers/BlockGroup_GISTAM2018.pdf

# About
Recursive clustering is an augmentation of existing clustering methods. Once a set of initial clusters is generated in the usual way, this algorithm will evaluate a set of **Hard** and **Soft** thresholds on set of clustered points. These thresholds use user-defined property values about each cluster. For example, a point threshold could say "if the number of points of any cluster is less than 10, terminate." 

If a cluster does not meet the specified thresholds, the set of points defined by said cluster is re-clustered recursively. This will generate a new set of clusters and this algorithm will evaluate this new set recursively until desired thresholds are achieved.

This re-clustering is performed independently of points in other clusters. For example, consider a set of 6 points in the first cluster and 9 points in the second cluster. If the first cluster fails to meet thresholds, those 6 points will be recursively re-clustered independently of the other 9 points (or any points not in the first cluster).

## Hard and Soft Thresholds
**Hard** thresholds are thresholds such that if any hard threshold is meant, the algorithm will stop the recursion. In contrast, all **Soft** thresholds must be meant in order for the algorithm to stop recursion. Note that these work independently of one another, meaning even if only a few soft thresholds are meant, a single hard threshold will terminate the recursion. 

Hard thresholds are typically used to describe conditions where further re-clustering would result in a program crash, or anomaly. Soft thresholds typically describe the actual parameters you ideally want each cluster to meet.

I recommend there always be a hard threshold for the number of points in a cluster. This way, the algorithm is guaranteed to terminate since on each recursive step, the clusters evaluated will continue to decrease in size. The provided algorithm requires it to avoid such unattainable thresholds conditions.

# Example Set, Census Data
I have provided the census dataset from the paper to play with this algorithm. I defined a single hard threshold for the number of points. For the soft thresholds, I used average Euclidean distance between each point and the total population of all points in the cluster. This resulted in sparse clusters for rural areas where drive times are less impactful and dense clusters in very urban areas where drive times are more significant. Tweaking the values for the population and distance value thresholds will achieve varied results.

[README IN PROGRESS]

