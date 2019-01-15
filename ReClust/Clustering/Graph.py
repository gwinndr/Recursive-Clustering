import matplotlib.pyplot as plt
#plt.switch_backend("Qt4Agg")

import numpy as np
import os


# This function plots the centroids and labels the points based on the cluster
def plotClusterData(Clusters, useGraphics, plotCentroids=True, saveFilePath=None):
    colors = ['r.', 'g.', 'b.', 'c.', 'm.', 'y.', 'k.'] * len(Clusters)  # Colors for matplotlib
    plt.axis('equal')

    centroid_latitudes = []
    centroid_longitudes = []

    for i in range(len(Clusters)):
        centroid_latitudes.append(Clusters[i].Centroid.mLatitude)
        centroid_longitudes.append(Clusters[i].Centroid.mLongitude)

        for point in Clusters[i].Points:
            plt.plot(point.mLongitude, point.mLatitude, colors[i], markersize=4, marker='o')
            #plt.plot(point.coordinate[1], point.coordinate[0], colors[2], markersize=4, marker='o')

    if(plotCentroids is True):
        np_latitudes = np.array(centroid_latitudes)
        np_longitudes = np.array(centroid_longitudes)

        plt.scatter(np_longitudes, np_latitudes, marker='x', s=100)

    if (not saveFilePath is None):
        plt.savefig(saveFilePath)

    if (useGraphics is True):
        plt.show()
    else:
        plt.clf()
