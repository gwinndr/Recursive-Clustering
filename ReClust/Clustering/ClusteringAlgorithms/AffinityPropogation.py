from sklearn.cluster import AffinityPropagation
import math
import numpy as np
import os

# Affinity Propogation info class
class AffinityPropogationReclust_c:
    def __init__(self):
        self.mAlgorithmName     = "Affinity Propogation" # REQUIRED
        self.mSaveLocation      = "./Outputs/Affinity_Propogation" # REQUIRED

        self.mDistanceFormula       = self.HaversineDistance
        self.mMinPointsInCluster    = 10 # REQUIRED
        self.mMaxDistance           = 5 # Defines the distance threshold
        self.mMaxPopulation         = 20000 # Defines the population threshold

        self.mHardThresholds        = [] # REQUIRED
        self.mSoftThresholds        = [self.DistanceThreshold, self.PopulationThreshold] # REQUIRED (can be empty)

        self.mClusters = None # REQUIRED

        # ALL REQUIRED
        # Statistics information
        self.mDistances         = None
        self.mTotalPoints       = None
        self.mMean              = None
        self.mMin               = None
        self.mMax               = None
        self.mStdev             = None
        self.mMedian            = None
        self.mTotalPop          = None


    # REQUIRED
    # Affinity Propogation parameters here for Reclust
    def ReclusterFunction(self, cluster):
        # Using Euclidean distances for now
        coordinates = []
        for point in cluster.Points:
            coordinates.append([point.mLatitude, point.mLongitude])

        np_coords = np.array(coordinates)

        affinityProp = AffinityPropagation(damping=0.9, verbose=True, max_iter=2000, convergence_iter=200).fit(np_coords)

        centroid_indices = affinityProp.cluster_centers_indices_
        label_indices = affinityProp.labels_

        # Reclust expects actual centroids, not indices
        centroids = []
        for index in centroid_indices:
            centroids.append(cluster.Points[index])

        return centroids, label_indices

    # REQUIRED
    # For getting statistics
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

    # REQUIRED
    # Prints the cluster information
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
    # A value of true denotes the soft threshold passes (all soft thresholds must pass to stop recursion)
    def DistanceThreshold(self,cluster):
        centroid = cluster.Centroid
        sum = 0.0

        for point in cluster.Points:
            sum += self.HaversineDistance(point, centroid)

        mean = sum / float(len(cluster.Points))
        return (mean <= self.mMaxDistance)

    # Will use sum of populations as a soft threshold
    # A value of true denotes the soft threshold passes (all soft thresholds must pass to stop recursion)
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
                cluster_distances.append(self.HaversineDistance(centroid, point))

            self.mDistances.append(cluster_distances)

