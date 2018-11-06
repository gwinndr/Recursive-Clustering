import sys
from Clustering.SetupClustering import SetupClustering


###################### MAIN ######################
# Where all data is read in and where selection of clustering algorithm lies
def main(argc, argv):
    if(argc != 3):
        print("USAGE: [exec] [CensusDatabasePath] [StateCodePath]")
        exit(1)
    print # empty line

    census_path     = argv[1]
    state_code_path = argv[2]

    answer = raw_input("Use graphics, requires X11 forwarding? (y/n): ")
    if(answer == 'y'):
        use_graphics = True
    else:
        use_graphics = False

    return SetupClustering(census_path, state_code_path, use_graphics)



if __name__ == "__main__":
    return_code = main(len(sys.argv), sys.argv)

    print "\nMain exited with code: %d" % return_code















