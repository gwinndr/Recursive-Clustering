from Utilities import ParseCensusfile, ParseStateCodes
from ClusteringAlgorithms import *
from Reclust import ReclustInterface
from Graph import plotClusterData
import os
import signal
from SaveClusters import *

# Starts setting up clustering
def SetupClustering(censusPath, stateCodePath, useGraphics):
    state_codes, success = ParseStateCodes(stateCodePath)
    if (success is False):
        exit(1)

    # Selection for clustering algorithm
    print("Select clustering algorithm of choice:")
    print("1) Affinity Propogation")
    print("2) Mean Shift")
    print("3) Adaptive Kmeans")
    print("4) State Defined Adaptive Kmeans")
    print("5) 4 with Sil limiting")
    print("6) Test Solution Template")
    print  # empty line
    while (True):
        answer = raw_input("Clustering algorithm (use number): ")
        if (answer == '1'):
            clustering_obj = AffinityPropogation.AffinityPropogationReclust_c()
            break
        elif (answer == '2'):
            clustering_obj = MeanShift.MeanShiftReclust_c()
            break
        elif (answer == '3'):
            clustering_obj = AdaptiveKmeans.AdaptiveKmeansReclust_c()
            break
        elif (answer == '4'):
            clustering_obj = AdaptiveKmeansStateDefined.AdaptiveKmeansStateDefinedReclust_c()
            clustering_obj.RunConfigurations(state_codes)
            break
        elif (answer == '5'):
            clustering_obj = AdaptiveKmeansStateDefinedSilLimit.AdaptiveKmeansStateDefinedSilLimitReclust_c()
            clustering_obj.RunConfigurations(state_codes)
            break
        elif (answer == '6'):
            clustering_obj = SolutionTemplate.SolutionTemplate()
            break
        else:
            print("Input not recognized!")

    print "Running " + clustering_obj.mAlgorithmName

    clustering_obj.GenerateSaveFolder()
    print

    answer = raw_input("Run all states? (y/n): ")
    if(answer == 'y'):
        RunAllClustering(clustering_obj, censusPath, state_codes.values())
        # RunAllClusteringForked(clustering_obj, censusPath, state_codes.values())
    else:
        RunSingleClustering(clustering_obj, censusPath, state_codes, useGraphics)


    return 0

# Generates reclust interface from clustering object and recluster data
def GenerateReclustInterface(clusteringObject, reclusterData):
    reclust_interface = ReclustInterface.ReclustInterface_c()
    reclust_interface.mReclusterData = reclusterData

    reclust_interface.mReclusteringFunction = clusteringObject.ReclusterFunction
    reclust_interface.mMinPointsInCluster = clusteringObject.mMinPointsInCluster
    reclust_interface.mHardThresholds = clusteringObject.mHardThresholds
    reclust_interface.mSoftThresholds = clusteringObject.mSoftThresholds

    return reclust_interface

# Runs un-automated clustering
def RunSingleClustering(clusteringObj, censusPath, stateCodes, useGraphics):
    # Letting user select state code (sorted for convenience)
    # Allows for repeats for incorrect selection
    while True:
        sorted_state_codes = sorted(stateCodes.items())
        print "STATE CODES:"
        for state, code in sorted_state_codes:
            print(state + ": " + code)
        print  # empty line

        target_state_code = raw_input("Enter state code to cluster: ")
        print  # empty line

        census_data, success = ParseCensusfile(censusPath, target_state_code)
        if (success is False):
            print "Critical error, could not parse recluster data"
            exit(1)

        print "Successfully parsed", len(census_data), "points from cluster file"
        answer = raw_input("Continue with current data? (y/n): ")
        if (answer == 'y'):
            break
    print  # empty line

    path_initial_pickle = clusteringObj.mSaveLocation + "/Initial_Pickle/" + target_state_code + ".pickle"
    path_initial_clusters = clusteringObj.mSaveLocation + "/Initial_Clusters/" + target_state_code + ".csv"
    path_initial_stats = clusteringObj.mSaveLocation + "/Initial_Stats/" + target_state_code + ".csv"
    path_initial_graphs = clusteringObj.mSaveLocation + "/Initial_Graphs/" + target_state_code + ".png"

    path_reclust_pickle = clusteringObj.mSaveLocation + "/Reclust_Pickle/" + target_state_code + ".pickle"
    path_reclust_clusters = clusteringObj.mSaveLocation + "/Reclust_Clusters/" + target_state_code + ".csv"
    path_reclust_stats = clusteringObj.mSaveLocation + "/Reclust_Stats/" + target_state_code + ".csv"
    path_reclust_graphs = clusteringObj.mSaveLocation + "/Reclust_Graphs/" + target_state_code + ".png"

    GeneratePaths([path_initial_pickle, path_initial_stats, path_initial_clusters,
                   path_reclust_pickle, path_reclust_stats, path_reclust_clusters,
                   path_initial_graphs, path_reclust_graphs], isFilePaths=True)

    reclust_interface = GenerateReclustInterface(clusteringObj, census_data)

    # Asking if you want to read in previous clusters
    answer = raw_input("Read initial clusters? (y/n): ")
    if (answer == 'y'):
        reclust_interface.mInitialClusterSolution = LoadPickledClusters(path_initial_pickle)
        clusteringObj.mClusters = reclust_interface.mInitialClusterSolution
        clusteringObj.CalculateStatistics()

    else:
        reclust_interface = CalculateInitialClusters(reclust_interface, clusteringObj)

        PickleClusters(reclust_interface.mInitialClusterSolution, path_initial_pickle)
        SaveClustersToCSV(clusteringObj.mClusters, path_initial_clusters)
        WriteStatsToCSV(clusteringObj, path_initial_stats)

    clusteringObj.PrintClusters()
    plotClusterData(clusteringObj.mClusters, useGraphics, saveFilePath=path_initial_graphs)

    # Reclustering
    answer_recluster = raw_input("Recluster? (y/n): ")
    if (answer_recluster == 'y'):
        RunReclustering(reclust_interface, clusteringObj)
        clusteringObj.PrintClusters()

        PickleClusters(clusteringObj.mClusters, path_reclust_pickle)
        SaveClustersToCSV(clusteringObj.mClusters, path_reclust_clusters)
        WriteStatsToCSV(clusteringObj, path_reclust_stats)

        plotClusterData(clusteringObj.mClusters, useGraphics, saveFilePath=path_reclust_graphs)

# Runs automated clustering of all states
def RunAllClustering(clusteringObj, censusPath, stateCodes, useGraphics=False):
    # Setting partial save paths
    partial_initial_pickle = clusteringObj.mSaveLocation + "/Initial_Pickle"
    partial_initial_clusters = clusteringObj.mSaveLocation + "/Initial_Clusters"
    partial_initial_stats = clusteringObj.mSaveLocation + "/Initial_Stats"
    partial_initial_graphs = clusteringObj.mSaveLocation + "/Initial_Graphs"

    partial_reclust_pickle = clusteringObj.mSaveLocation + "/Reclust_Pickle"
    partial_reclust_clusters = clusteringObj.mSaveLocation + "/Reclust_Clusters"
    partial_reclust_stats = clusteringObj.mSaveLocation + "/Reclust_Stats"
    partial_reclust_graphs = clusteringObj.mSaveLocation + "/Reclust_Graphs"

    GeneratePaths([partial_initial_pickle, partial_initial_stats, partial_initial_clusters,
                   partial_reclust_pickle, partial_reclust_stats, partial_reclust_clusters,
                   partial_initial_graphs, partial_reclust_graphs], isFilePaths=False)

    ################# MAIN RECLUSTERING AUTOMATION #############
    read_initial_clusters = raw_input("Read initial clusters? (y/n): ")
    for target_state_code in stateCodes:
        census_data, success = ParseCensusfile(censusPath, target_state_code)
        if (success is False):
            print "Critical error, could not parse recluster data"
            exit(1)

        print "RUNNING STATE: " + str(target_state_code)

        path_initial_pickle = partial_initial_pickle + '/' + target_state_code + ".pickle"
        path_initial_clusters = partial_initial_clusters + '/' + target_state_code + ".csv"
        path_initial_stats = partial_initial_stats + '/' + target_state_code + ".csv"
        path_initial_graphs = partial_initial_graphs + '/' + target_state_code + ".png"

        path_reclust_pickle = partial_reclust_pickle + '/' + target_state_code + ".pickle"
        path_reclust_clusters = partial_reclust_clusters + '/' +  target_state_code + ".csv"
        path_reclust_stats = partial_reclust_stats + '/' + target_state_code + ".csv"
        path_reclust_graphs = partial_reclust_graphs + '/' + target_state_code + ".png"

        reclust_interface = GenerateReclustInterface(clusteringObj, census_data)

        if(read_initial_clusters is True):
            reclust_interface.mInitialClusterSolution = LoadPickledClusters(path_initial_pickle)

            if(reclust_interface is None):
                print "Could not load pickled clusters, aborting this run"
                is_valid = False

            else:
                clusteringObj.mClusters = reclust_interface.mInitialClusterSolution
                clusteringObj.CalculateStatistics()
                is_valid = True

        else:
            reclust_interface = CalculateInitialClusters(reclust_interface, clusteringObj)

            PickleClusters(reclust_interface.mInitialClusterSolution, path_initial_pickle)
            SaveClustersToCSV(clusteringObj.mClusters, path_initial_clusters)
            WriteStatsToCSV(clusteringObj, path_initial_stats)

            #plotClusterData(clusteringObj.mClusters, useGraphics, saveFilePath=path_initial_graphs)
            is_valid = True

        # Reclustering
        if(is_valid is True):
            RunReclustering(reclust_interface, clusteringObj)

            PickleClusters(clusteringObj.mClusters, path_reclust_pickle)
            SaveClustersToCSV(clusteringObj.mClusters, path_reclust_clusters)
            WriteStatsToCSV(clusteringObj, path_reclust_stats)

# Uses forking for a speedup
def RunAllClusteringForked(clusteringObj, censusPath, stateCodes, useGraphics=False):
    # Setting partial save paths
    partial_initial_pickle = clusteringObj.mSaveLocation + "/Initial_Pickle"
    partial_initial_clusters = clusteringObj.mSaveLocation + "/Initial_Clusters"
    partial_initial_stats = clusteringObj.mSaveLocation + "/Initial_Stats"
    partial_initial_graphs = clusteringObj.mSaveLocation + "/Initial_Graphs"

    partial_reclust_pickle = clusteringObj.mSaveLocation + "/Reclust_Pickle"
    partial_reclust_clusters = clusteringObj.mSaveLocation + "/Reclust_Clusters"
    partial_reclust_stats = clusteringObj.mSaveLocation + "/Reclust_Stats"
    partial_reclust_graphs = clusteringObj.mSaveLocation + "/Reclust_Graphs"

    GeneratePaths([partial_initial_pickle, partial_initial_stats, partial_initial_clusters,
                   partial_reclust_pickle, partial_reclust_stats, partial_reclust_clusters,
                   partial_initial_graphs, partial_reclust_graphs], isFilePaths=False)

    ################# MAIN RECLUSTERING AUTOMATION WITH FORKING #############
    read_initial_clusters = raw_input("Read initial clusters? (y/n): ")
    for target_state_code in stateCodes:
        census_data, success = ParseCensusfile(censusPath, target_state_code)
        if (success is False):
            print "Critical error, could not parse recluster data"
            exit(1)
        
        child_pid_list = []
        pid = os.fork()
        
        #### PARENT ####
        if(pid):
            child_pid_list.append(pid)
        
        #### CHILD ####
        else:
            print "RUNNING STATE: " + str(target_state_code)

            path_initial_pickle = partial_initial_pickle + '/' + target_state_code + ".pickle"
            path_initial_clusters = partial_initial_clusters + '/' + target_state_code + ".csv"
            path_initial_stats = partial_initial_stats + '/' + target_state_code + ".csv"
            path_initial_graphs = partial_initial_graphs + '/' + target_state_code + ".png"

            path_reclust_pickle = partial_reclust_pickle + '/' + target_state_code + ".pickle"
            path_reclust_clusters = partial_reclust_clusters + '/' +  target_state_code + ".csv"
            path_reclust_stats = partial_reclust_stats + '/' + target_state_code + ".csv"
            path_reclust_graphs = partial_reclust_graphs + '/' + target_state_code + ".png"

            reclust_interface = GenerateReclustInterface(clusteringObj, census_data)

            if(read_initial_clusters is True):
                reclust_interface.mInitialClusterSolution = LoadPickledClusters(path_initial_pickle)

                if(reclust_interface is None):
                    print "Could not load pickled clusters, aborting this run"
                    is_valid = False

                else:
                    clusteringObj.mClusters = reclust_interface.mInitialClusterSolution
                    clusteringObj.CalculateStatistics()
                    is_valid = True

            else:
                reclust_interface = CalculateInitialClusters(reclust_interface, clusteringObj)

                PickleClusters(reclust_interface.mInitialClusterSolution, path_initial_pickle)
                SaveClustersToCSV(clusteringObj.mClusters, path_initial_clusters)
                WriteStatsToCSV(clusteringObj, path_initial_stats)

                #plotClusterData(clusteringObj.mClusters, useGraphics, saveFilePath=path_initial_graphs)
                is_valid = True

            # Reclustering, Just getting initial for now
            # if(is_valid is True):
                # RunReclustering(reclust_interface, clusteringObj)

                # PickleClusters(clusteringObj.mClusters, path_reclust_pickle)
                # SaveClustersToCSV(clusteringObj.mClusters, path_reclust_clusters)
                # WriteStatsToCSV(clusteringObj, path_reclust_stats)
            
            os.exit()

# Calculates Initial Clustering Solution
def CalculateInitialClusters(reclust_interface, clusteringObj):
    ReclustInterface.GenerateInitialClusterList(reclust_interface)
    clusteringObj.mClusters = reclust_interface.mInitialClusterSolution
    clusteringObj.CalculateStatistics()

    return reclust_interface

# Runs the main clustering algorithm using reclust
def RunReclustering(reclustInterface, clusteringObj):
    ReclustInterface.RunReclust(reclustInterface, verbose=True)

    clusteringObj.mClusters = reclustInterface.mFinalClusters
    clusteringObj.CalculateStatistics()



