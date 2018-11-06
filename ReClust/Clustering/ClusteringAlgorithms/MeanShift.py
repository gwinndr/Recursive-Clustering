from sklearn.cluster import MeanShift
import math
import numpy as np
import os
import CensusPoint_s


# Mean Shift info class
class MeanShiftReclust_c:
    def __init__(self):
        # Tweaks the algorithm to keep orphans seperated
        self.mIncludeOrphans = False # Edge case breaks this when True (TODO)
        self.mAlgorithmName     = "Mean Shift"

        if(self.mIncludeOrphans is True):
            self.mSaveLocation      = "./Outputs/MeanShift_BinSeeding_OrphansIncluded"
        else:
            self.mSaveLocation = "./Outputs/MeanShift_BinSeeding_OrphansSeparated"

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


    # Mean Shift parameters here for Reclust (REQUIRED)
    def ReclusterFunction(self, cluster):
        # Using Euclidean distances for now
        coordinates = []
        for point in cluster.Points:
            coordinates.append([point.mLatitude, point.mLongitude])

        np_coords = np.array(coordinates)

        # Cluster all is set to false to make sure orphans are not grouped with far away clusters
        # n_jobs=-1 just tells it to use all CPU's
        mean_shift = MeanShift(n_jobs=-1, cluster_all=self.mIncludeOrphans, bin_seeding=True).fit(np_coords)

        centroid_coords = mean_shift.cluster_centers_.tolist()
        label_indices = mean_shift.labels_

        # Converting centroids to census point
        centroids = []
        for centroid in centroid_coords:
            census_point = CensusPoint_s.CensusPoint_s()
            census_point.mLatitude = centroid[0]
            census_point.mLongitude = centroid[1]

            centroids.append(census_point)

        # -1 indicates orphan point and we need to create special cluster centroids for those
        if(self.mIncludeOrphans is False):
            current_cluster_index = max(label_indices) + 1
            for i in range(len(label_indices)):
                if(label_indices[i] == -1):
                    centroids.append(cluster.Points[i])
                    label_indices[i] = current_cluster_index
                    current_cluster_index += 1

        return centroids, label_indices

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

