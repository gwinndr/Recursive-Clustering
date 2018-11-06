import pickle
import csv
import os

def GeneratePaths(paths, isFilePaths):
    if (isFilePaths is True):
        for path in paths:
            path_head = os.path.dirname(path)

            if(not os.path.isdir(path_head)):
                os.makedirs(path_head)
    else:
        for path in paths:
            if(not os.path.isdir(path)):
                os.makedirs(path)

def PickleClusters(clusters, filePath):
    try:
        output_stream = open(filePath, "wb")

        pickle.dump(clusters, output_stream)

        print "PickleClusters: Pickle successfully saved to " + filePath

        return True

    except IOError, ioe:
        print "Error, could not save pickle to " + filePath
        print str(ioe)

        return False

def LoadPickledClusters(filePath):
    try:
        input_stream = open(filePath, "rb")

        clusters = pickle.load(input_stream)

        print "LoadPickledClusters: Pickle successfully loaded from " + filePath

        return clusters

    except IOError, ioe:
        print "LoadPickledClusters: Error, could not load pickle from " + filePath
        print str(ioe)

        return None

def SaveClustersToCSV(clusters, filePath):
    try:
        output_stream = open(filePath, "wb")
        csv_writer = csv.writer(output_stream)

        for cluster in clusters:
            centroid = cluster.Centroid
            csv_writer.writerow(["Centroid"])
            csv_writer.writerow([str(centroid.mLatitude), str(centroid.mLongitude)])

            csv_writer.writerow(["Points"])
            for point in cluster.Points:
                csv_writer.writerow([str(point.mLatitude), str(point.mLongitude)])

        return True

    except IOError, ioe:
        print "SaveClustersToCSV: Failed to save clusters to csv at " + filePath
        print str(ioe)

        return False

# Writes statistics to file
def WriteStatsToCSV(clusteringObject, path):
    try:
        output_stream = open(path, "wb")
        csv_writer = csv.writer(output_stream)
        csv_writer.writerow(["Cluster","Total Points", "Mean", "Min", "Max", "Median", "Stdev", "TotalPop"])

        for i in range(len(clusteringObject.mClusters)):
            csv_writer.writerow(
                [str(i + 1), str(clusteringObject.mTotalPoints[i]), str(clusteringObject.mMean[i]), str(clusteringObject.mMin[i]),
                 str(clusteringObject.mMax[i]), str(clusteringObject.mMedian[i]), str(clusteringObject.mStdev[i]),
                 str(clusteringObject.mTotalPop[i])])

        return True

    except IOError, ioe:
        print "Affinity_Prop: Failed to save clusters to csv at " + path
        print str(ioe)

        return False


