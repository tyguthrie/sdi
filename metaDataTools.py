def XMLSearch(): # Searches for metadata in XML files

    # set variables
    xmlFiles = []
    xmlDocs = []
    Folders = [sys.argv[1]]
    subFolders = sys.argv[2]  # true or false
    strFind = sys.argv[3]
    strSection = sys.argv[4]
    dateBegin = sys.argv[5]   # searches publication date
    dateEnd = sys.argv[6]
    varProg = sys.argv[7]     # domain: 'complete', 'in work' or 'planned'
    varProj = sys.argv[8]
    varCoord = sys.argv[9]    # from reference shapefile, or feature class
    varInt = sys.argv[10]     # intersects or contains

        
        # return list of XML files in the target folder
        # by using glob to extract files with .xml extension
        # decide whether to search subfolders from user input
    if not (subFolders == "true"):
        xmlFiles = glob.glob(os.path.join(Folders[0],"*.xml"))
    else:
        # return list of XML files in folder and subfolders
        # by using glob to extract files with .xml extension
        # then loop, extracting list of subfolders until none left
        while Folders:
            newFolders = []
            for f in Folders:
                xmlFiles = xmlFiles + glob.glob(os.path.join(f,"*.xml"))
                newFolders = newFolders + [os.path.join(f,nf) for nf in os.listdir(f)
                                           if (os.path.isdir(os.path.join(f,nf)))]
            Folders = newFolders

    # write list of selected files to message window
    for x in xmlFiles:
        print x
    #    gp.addmessages(x)

    # parse the xml files into document object models
    xmldoc = xml.dom.minidom.parse(xmlFiles[0])
    alist = xmldoc.getElementsByTagName('citeinfo')

    # write xml output
    print alist[0].toxml()
