from Clustering.ClusteringAlgorithms import CensusPoint_s
import csv

# Parses state code file and places data into dictionary
# Returns true iff parsed successfully
def ParseStateCodes(stateFile):
    try:
        state_stream = open(stateFile, "rb")
        state_csv_reader = csv.reader(state_stream)

        result_dict = {}
        for row in state_csv_reader:
            state = row[0]
            code = row[1]

            result_dict[state] = code

        return result_dict, True

    except IOError, ioe:
        print("Exception at ParseStateCodes:")
        print(str(ioe))
        print("With file:")
        print(stateFile)

        return {}, False

# Parses census file and only extracts rows with the correct state code
# Returns true iff parsed successfully
def ParseCensusfile(censusFile, stateCode):
    try:
        census_stream = open(censusFile, "rb")
        census_csv_reader = csv.reader(census_stream)

        result_list = []
        for row in census_csv_reader:
            if(row[0] == stateCode):
                census_point = CensusPoint_s.CensusPoint_s()

                census_point.mStateCode     = stateCode
                census_point.mPopulation    = int(row[4])
                census_point.mLatitude      = float(row[5])
                census_point.mLongitude     = float(row[6])

                # print census_point.mLatitude, census_point.mLongitude

                result_list.append(census_point)

        return result_list, True

    except IOError, ioe:
        print("Exception at ParseCensusFile:")
        print(str(ioe))
        print("With file:")
        print(censusFile)

        return {}, False



