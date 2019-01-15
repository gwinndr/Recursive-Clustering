# Recursive-Clustering Demo
Original paper found here: https://tars.clarkson.edu/papers/BlockGroup_GISTAM2018.pdf

Note that this not a general-purpose library at the moment, I am still working on that. This is just a workable demo from the paper. This code is also not documented so please refer to this README for usage instructions.

The *X11 forwarding message* was present for when this was run on a server without X11 forwarding set up. If you're running locally, just answer yes.

# Requirements 
* Python 2.7 (Python 3 currently unsupported)
* Numpy
* Scikit-Learn
* Matplotlib
* Pickle

# About
Recursive clustering is an augmentation of existing clustering methods. Once a set of initial clusters is generated in the usual way, this algorithm will evaluate a set of **Hard** and **Soft** thresholds on set of clustered points. These thresholds use user-defined property values about each cluster. For example, a point threshold would say "if the number of points in a cluster is less than 10, stop recursion." 

If a cluster does not meet the specified thresholds, the set of points in said cluster is re-clustered recursively. This will generate a new set of clusters which will then be similarly evaluated recursively. Clustering algorithms are user-defined.

This re-clustering is performed independently of points in other clusters. For example, consider a set of 6 points in the first cluster and 9 points in the second cluster. If the first cluster fails to meet thresholds, those 6 points will be recursively re-clustered independently of the other 9 points. Dependent re-clustering is not currently being considered.

## Hard and Soft Thresholds
**Hard** thresholds are thresholds such that if _any_ hard threshold is meant, the algorithm will stop the recursion. In contrast, **Soft** thresholds must _all_ be met in order for the algorithm to stop recursion. Note that these work independently of one another, meaning even if not all soft thresholds are met, a single hard threshold will terminate the recursion (and vice-versa). 

Hard thresholds are typically used to describe conditions where further re-clustering would result in a program crash, or data anomaly. Soft thresholds typically describe the actual parameters you ideally want each cluster to meet. A typical example of a hard threshold would be number of points in a cluster. A typical example of a soft threshold would be average distance from each point in a cluster to the centroid.

I require there always be a hard threshold for the number of points in a cluster. This way, the algorithm is guaranteed to terminate assuming the clustering algorithm used always generates at least two non-empty clusters.

# Running ReClust
The original paper is based on the usage of Scikit-Learn's Affinity Propogation algorithm. The implementation is present in ReClust/Clustering/ClusteringAlgorithms. This algorithms uses the required hard point threshold, a soft distance threshold, and a soft population threshold. More details on those specific thresholds are present in the **Example Set** section.

Run the Python 2.7 interpretor on Reclust/main.py with the paths to the census and state FIPS code databases as the first and second arguments respectively. These databases are currently present as CSV files in Reclust/CensusData. Then, select the ReClust solution desired. The framework will ask which state to run the solution on, but be careful with expensive solutions on particularly large states such as California which can take a long time to complete. The framework will create an Outputs folder and save all applicable cluster solution information (statistics, cluster points, etc.).

The script, main.py, will make a call to SetupClustering.py present in the Reclust/Clustering directory. The main thing to note from SetupClustering is the selection logic at the beginning of the file. Here, you can see that adding a new ReClust solution is as simple as adding the option and setting the *clustering_obj* variable. Additionally, modifying any ReClust solution requires no changes to any selection and re-clustering logic.

## A Note on Running Time
The time complexity of clustering algorithms with respect to the number of elements is typically quadratic. What this means is that on any particular dataset, it takes significantly less time to cluster each subset in a partition than it does to cluster the full dataset of points. The majority of time it takes to run ReClust actually comes from the initial cluster generation and not the recursive steps. Of course, you could set up thresholds that are expensive to compute, but this would be atypical.

Even better, the re-clustering steps can very easily run in parallel which, when implemented, will further increase the time gap between generating initial clusters and the re-clustering step.

To this end, any initial clusters are always available to be read in. If there is a particular set of initial clusters that are well liked, they are always saved as a pickle in the output directories under the *Initial_Pickle* directory. If you have initial clusters for a state you want to use, simply copy it into the corresponding directory of your current solution's save path and run ReClust. ReClust will ask if you want to read in those initial clusters! From my experience, this has saved a significant amount of time.

## Creating a ReClust Solution
In order to make a robust system for easily testing different clustering algorithms, a general *ReClust object* must be used. All required members and methods are marked as such and must be implemented for the framework to accept it. A template class is present in ReClust/Clustering/ClusteringAlgorithms/SolutionTemplate.py. Examples of required elements include the ReCluster method and a list of hard threshold functions. **Make sure to add your new clustering solution to \_\_init\_\_.py in the ClusteringAlgorithms directory**

A Python class is used as ReClust solutions because it is extensible and allows the user to use and store whatever data is required. For example, the soft distance threshold makes use of the Haversine formula which is implemented as a class method. This model also allows for any number and combination of hard and soft threshold functions can be used and still have access to all resources of the current clustering solution should they be required.

The template class will contain additional information about the required elements and what they are used for.

# Example Set, Census Data
I have provided the census dataset from the paper to play with this algorithm. The goal from the paper was to cluster intelligently such that each cluster would be able to combine multiple block groups into single points without sacrificing drive time accuracy. 

I defined only the required hard threshold for the number of points. For the soft thresholds, I used average Haversine distance between each point to the centroid and the total population of all points in the cluster. This resulted in sparse clusters for rural areas where drive times are less impactful and dense clusters in very urban areas where drive times are more significant. Tweaking the values for the population and distance value thresholds will achieve varied results.

Each solution will be graphed at the initial cluster stage and the final re-clustered stage. These differences can be compared. Statistical analysis of generated Affinity Propogation results are present in the paper.

# Special Thanks
* Sean Banerjee, for his mentoring, without which this project wouldn't even exist
* Jordan Helmick, for his access to census data and statistical mastery
* Natasha Banerjee, for her proofreading skills and machine learning guidance







