from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import math
import numpy as np
import os
import csv
import CensusPoint_s


# State Defined Adaptive Kmeans info class
class AdaptiveKmeansStateDefinedReclust_c:
    def __init__(self):
        self.mMaxClusterNumStatePath    = None
        self.mNameAddition              = None
        self.mVerbose                   = True

        self.mClusterLimits             = {}

        self.mAlgorithmName             = "State Defined Adaptive Kmeans"
        self.mSaveLocation              = "./Outputs/AdaptiveKmeans_StateDefined_"

        self.mDistanceFormula       = self.HaversineDistance
        self.mMinPointsInCluster    = 10
        self.mMaxDistance           = 5
        self.mMaxPopulation         = 20000

        self.mHardThresholds        = []
        self.mSoftThresholds        = [self.DistanceThreshold, self.PopulationThreshold]

        self.mClusters = None

        # Statistics information
        self.mDistances         = None
        self.mTotalPoints       = None
        self.mMean              = None
        self.mMin               = None
        self.mMax               = None
        self.mStdev             = None
        self.mMedian            = None
        self.mTotalPop          = None


    # Runs configuration
    def RunConfigurations(self, stateMap):
        print "Needs configurations..."
        self.mMaxClusterNumStatePath = raw_input("Enter path: ")
        self.mNameAddition = raw_input("Enter save path addition: ")

        self.mSaveLocation += self.mNameAddition

        print "Reading state cluster numbers..."
        cluster_stream = open(self.mMaxClusterNumStatePath)
        cluster_csv_reader = csv.reader(cluster_stream)

        for row in cluster_csv_reader:
            state = row[0]
            num_clusters = int(row[1])

            state_code = stateMap[state]
            self.mClusterLimits[state_code] = num_clusters

    # State Defined Adaptive Kmeans parameters here for Reclust (REQUIRED)
    def ReclusterFunction(self, cluster):
        # Using Euclidean distances for now
        coordinates = []
        for point in cluster.Points:
            coordinates.append([point.mLatitude, point.mLongitude])

        np_coords = np.array(coordinates)

        # Cluster all is set to false to make sure orphans are not grouped with far away clusters
        best_sil_score      = 0
        best_centroids      = None
        best_labels         = None
        num_points          = len(coordinates)

        max_cluster_range = self.mClusterLimits[cluster.Points[0].mStateCode] + 1
        if(self.mVerbose):
            print "For state: " + str(cluster.Points[0].mStateCode) + " cluster range is " + str(max_cluster_range)

        if(max_cluster_range > num_points):
            actual_max_clusters = num_points
        else:
            actual_max_clusters = max_cluster_range

        cluster_solution_nums = range(2, actual_max_clusters)
        for n_clusters in cluster_solution_nums:
            kmeans = KMeans(n_clusters=n_clusters, precompute_distances=True, n_jobs=-1).fit(np_coords)
            sil_score = silhouette_score(np_coords, kmeans.labels_)

            # print sil_score

            if(sil_score > best_sil_score):
                best_sil_score = sil_score
                best_centroids  = kmeans.cluster_centers_
                best_labels     = kmeans.labels_

        # Converting centroids to census point
        centroids = []
        for centroid in best_centroids:
            census_point = CensusPoint_s.CensusPoint_s()
            census_point.mLatitude = centroid[0]
            census_point.mLongitude = centroid[1]

            centroids.append(census_point)

        return centroids, best_labels

    # For getting statistics (REQUIRED)
    def CalculateStatistics(self):
        self.CalculateDistanceList()

        self.mMean          = []
        self.mMin           = []
        self.mMax           = []
        self.mStdev         = []
        self.mMedian        = []
        self.mTotalPop      = []
        self.mTotalPoints   = []

        for cluster_distance_list in self.mDistances:
            self.mMean.append(np.mean(cluster_distance_list))
            self.mMin.append(min(cluster_distance_list))
            self.mMax.append(max(cluster_distance_list))
            self.mMedian.append(np.median(cluster_distance_list))
            self.mStdev.append(np.std(cluster_distance_list))
            self.mTotalPoints.append(len(cluster_distance_list))

        for cluster in self.mClusters:
            total_pop = 0

            for point in cluster.Points:
                total_pop += point.mPopulation

            self.mTotalPop.append(total_pop)

    # Prints the cluster information (REQUIRED)
    def PrintClusters(self):
        print "Number of clusters:", len(self.mClusters), "\n"

        for i in range(len(self.mClusters)):
            print "========================="
            print "Cluster:", i+1
            print 'Centroid:', self.mClusters[i].Centroid.mLatitude, ',', self.mClusters[i].Centroid.mLongitude
            print 'Number of Points:', len(self.mClusters[i].Points)
            print 'Total Population:', self.mTotalPop[i], '\n'
            print 'Min:', self.mMin[i]
            print 'Max:', self.mMax[i]
            print 'Mean:', self.mMean[i]
            print 'Median:', self.mMedian[i]
            print 'Stdev:', self.mStdev[i]

        print


    # Generates a save folder
    def GenerateSaveFolder(self):
        if (not os.path.isdir(self.mSaveLocation)):
            os.makedirs(self.mSaveLocation)

    # Will be used as a soft distance threshold
    # Calcluates the mean distance to centroid using the haversine
    def DistanceThreshold(self,cluster):
        centroid = cluster.Centroid
        sum = 0.0

        for point in cluster.Points:
            sum += self.mDistanceFormula(point, centroid)

        mean = sum / float(len(cluster.Points))
        return (mean <= self.mMaxDistance)

    # Will use sum of populations as a soft threshold
    def PopulationThreshold(self, cluster):
        sum = 0.0

        for point in cluster.Points:
            sum += point.mPopulation

        return (sum <= self.mMaxPopulation)

    # Distance stored in KM
    def HaversineDistance(self, censusPoint1, censusPoint2):
        radius = 6371  # FAA approved globe radius in km

        dlat = math.radians(censusPoint2.mLatitude - censusPoint1.mLatitude)
        dlon = math.radians(censusPoint2.mLongitude - censusPoint1.mLongitude)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(censusPoint1.mLatitude)) \
            * math.cos(math.radians(censusPoint2.mLatitude)) * math.sin(
            dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d

    # Calculates the distance lists to centroid using the Haversine Formula
    def CalculateDistanceList(self):
        self.mDistances = []
        for cluster in self.mClusters:
            cluster_distances = []

            centroid = cluster.Centroid
            for point in cluster.Points:
                cluster_distances.append(self.mDistanceFormula(point, centroid))

            self.mDistances.append(cluster_distances)






