import ReclustInterface

# Generates cluster objects from data and indices
def ConstructClusters(cluster, labels, centroids):
    Clusters = [ReclustInterface.Cluster_c(centroid, []) for centroid in centroids]
    for i in range(len(labels)):
        label_index = labels[i]
        (Clusters[label_index]).Points.append(cluster.Points[i])
    return Clusters

# Generates clusters using the reclustering function
def GenerateClusters(reclustInterface, cluster):
    centroids, cluster_labels = reclustInterface.mReclusteringFunction(cluster)
    return ConstructClusters(cluster, cluster_labels, centroids)

# Reclustering algorithm
def RunRecursiveClustering(reclustInterface, cluster):
    # At least one threshold said to terminate
    if((len(cluster.Points) <= reclustInterface.mMinPointsInCluster) or
            (TestHardThresholds(reclustInterface.mHardThresholds, cluster)) or
            (TestSoftThresholds(reclustInterface.mSoftThresholds, cluster))):

        return [cluster]  # we do 'extend'

    else:
        reclustered_array = []
        clusters = GenerateClusters(reclustInterface, cluster)
        for new_cluster in clusters:
            reclustered_array.extend(RunRecursiveClustering(reclustInterface, new_cluster))

        return reclustered_array


# Hard thresholds, if any return true, returns true
def TestHardThresholds(hardThresholds, cluster):
    for hard_threshold in hardThresholds:
        if(hard_threshold(cluster) is True):
            return True
    return False

# Soft thresholds, all must return true to return true
def TestSoftThresholds(softThresholds, cluster):
    if len(softThresholds) == 0:
        return False

    for soft_threshold in softThresholds:
        if(soft_threshold(cluster) is False):
            return False
    return True

# Main (for testing)
if __name__ == "__main__":
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    centroids = [10, 11, 12]
    labels = [0, 0, 1, 2, 1, 2, 0, 2, 1]

    Clusters = ConstructClusters(data, labels, centroids)

    for Cluster in Clusters:
        print "CLUSTER:"
        print "Centroid: %d" % (Cluster.Centroid)
        for point in Cluster.Points:
            print point



