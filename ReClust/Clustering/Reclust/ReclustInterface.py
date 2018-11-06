import sys
import CoreRecursiveCalls

# Interface object where the user sets various methods required by the main API
class ReclustInterface_c:
    def __init__(self):
        # Required API recluster function to be set
        self.mReclusteringFunction = None

        # The data interested in reclustering
        self.mReclusterData = None

        # Hard and soft threshold functions for terminating case
        self.mHardThresholds = None
        self.mSoftThresholds = None

        # For bounding the number of iterations
        self.mMaxIterations = None # Currently unused
        self.mMinPointsInCluster = 1

        # Holds the final clusters
        self.mFinalClusters = None

        # Set of initial clusters
        self.mInitialClusterSolution = None

    # Checks if the necessary variables are set to None
    # Returns True if all variables are correctly instantiated
    def IsValidInstance(self, verbose = False):
        return_value = True

        if((not callable(self.mReclusteringFunction)) or (self.mReclusteringFunction.func_code.co_argcount != 2)):
            if(verbose is True):
                print("IsValidInstance: Invalid instance of ReclusterInterface_c: mReclusteringFunction must be a function with one argument")
            return_value = False

        if ((not isinstance(self.mReclusterData, list)) or (len(self.mReclusterData) == 0)):
            if (verbose is True):
                print("IsValidInstance: Invalid instance of ReclusterInterface_c: mReclusterData must be a list with at least one element")
            return_value = False

        if (self.mMinPointsInCluster < 1):
            if (verbose is True):
                print("IsValidInstance: Invalid instance of ReclusterInterface_c: mMinPointsInCluster must be at least 1")
            return_value = False

        return return_value

    # Clear methods
    def ClearHardThresholds(self):
        self.mHardThresholds = None

    def ClearSoftThresholds(self):
        self.mHardThresholds = None

    def ClearStatistics(self):
        self.mMinDistanceToCenter = None
        self.mMaxDistanceToCenter = None
        self.mMeanDistanceToCenter = None
        self.mMedianDistanceToCenter = None
        self.mStdevOfDistancesToCenter = None

    def ClearInitialClusters(self):
        self.mInitialClusterSolution = None

# Simple object encapsulating a single cluster
class Cluster_c:
    def __init__(self):
        self.Centroid = None
        self.Points = None

    def __init__(self, centroidArg, pointsArg):
        self.Centroid = centroidArg
        self.Points = pointsArg

# Generates initial clusters
def GenerateInitialClusterList(reclustInterface):
    placeholder_cluster = Cluster_c(None, reclustInterface.mReclusterData)
    reclustInterface.mInitialClusterSolution = CoreRecursiveCalls.GenerateClusters(reclustInterface, placeholder_cluster)

# The core recursive reclustering algorithm
def RunReclust(reclustInterface, verbose=False):
    if(not reclustInterface.IsValidInstance(verbose = True)):
        print("RunReclust: Error: Invalid reclustInterface argument")
        return False

    if(reclustInterface.mInitialClusterSolution is None):
        print("RunReclust: Error: Please generate initial clusters before running Reclust")
        return False

    # Main reclustering function
    reclustInterface.mFinalClusters = []
    for cluster in reclustInterface.mInitialClusterSolution:
        reclustInterface.mFinalClusters.extend(CoreRecursiveCalls.RunRecursiveClustering(reclustInterface, cluster))


    return True

if(__name__ == "__main__"):
    interface = ReclustInterface_c()
    interface.IsValidInstance(verbose=True)

