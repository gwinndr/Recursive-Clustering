import os

# A ReClust solution template for custom re-clustering solutions
class SolutionTemplate:
    def __init__(self):
        self.mAlgorithmName     = "ALG" # REQUIRED, feedback for the user
        self.mSaveLocation      = "./Outputs/ALG" # REQUIRED, directory where the output is stored

        # REQUIRED, used as a rudimentary "base" case. Will terminate recursion as a hard threshold
        self.mMinPointsInCluster    = 10

        # REQUIRED. These must be lists of functions that return a boolean
        # A True output means the threshold has been met
        # If a single hard threshold is met, recursion terminates
        # Similarly, only when all soft thresholds are met will recursion terminate
        # These work independently (ex: even if not all soft thresholds are met, a single hard threshold will terminate recursion)
        self.mHardThresholds        = []
        self.mSoftThresholds        = []

        # REQUIRED, leave this defaulted to None
        # Contains a snapshot of the current clustering solution across all clusters
        # At the termination of ReClust, this will contain the final solution
        self.mClusters = None

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
    # The main re-clustering solution, takes a single cluster object and outputs centroids with label_indices
    # The label_indices is a list that denotes the cluster
    # (ex: label index at position 2 with a value of 0 means the 2nd point goes to the 0th cluster)
    # The cluster variable contains two noteworthy elements, Centroid and Points which are the center and corresponding
    #       points of the cluster respectively
    def ReclusterFunction(self, cluster):
        print("Must be implemented")
        centroids = []
        label_indices = []
        return centroids, label_indices

    # REQUIRED
    # For getting statistics
    def CalculateStatistics(self):
        print "Must be implemented"
        self.mDistances = []
        self.mTotalPoints = 0
        self.mMean = 0
        self.mMin = 0
        self.mMax = 0
        self.mStdev = 0
        self.mMedian = 0
        self.mTotalPop = 0

    # REQUIRED, can leave as is
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

    # REQUIRED, leave as is
    # Generates a save folder from the given save location
    def GenerateSaveFolder(self):
        if (not os.path.isdir(self.mSaveLocation)):
            os.makedirs(self.mSaveLocation)





