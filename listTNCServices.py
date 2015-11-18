def publish_map_services(): # Publish services from mxds or msds 
    import arcpy, os, sys, string, os.path
    scanfolder = "d:\\services101"
    con = "d:\\services101\\stratus_publisher.ags"
    arcpy.env.workspace = scanfolder
    print "Executing..."

    for root, dirs, files in os.walk(scanfolder):
        for name in files:
            basename, extension = os.path.splitext(name)
            if extension.lower() == ".mxd":
                path = string.split(root,"\\")
                folder = path[2]
                service = string.split(path[3],".")[0]
                filename = os.path.join(root,name)
                mapDoc = arcpy.mapping.MapDocument(filename)
                print "Publishing " + service + " in folder " + folder + " from " + filename + "\n"

                try:

                    # Create service definition draft
                    sddraft = folder + service + ".sddraft"
                    arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, service, "", con, "", folder)
                    print "Draft created \n"

                    # Analyze the service definition draft
                    analysis = arcpy.mapping.AnalyzeForSD(sddraft)
                    print "Service successfully analyzed \n"

                    # Stage and upload the service if the sddraft analysis did not contain errors
                    if analysis['errors'] == {}:
                        sd = folder + service + ".sd"
                        # Execute StageService.
                        arcpy.StageService_server(sddraft, sd)
                        print "Service successfully staged \n"
                        # Execute UploadServiceDefinition. 
                        arcpy.UploadServiceDefinition_server(sd, con)
                        print "Service successfully published \n"

                except:
                    print "Service could not be published \n"
                    print arcpy.GetMessages(2)
                    

    input("Press ENTER to continue...")


def listServices(): #This function will list all services on TNC Servers

    import urllib, urllib2, json

    def gentoken(url,parameters):
        #function to get a token required for Admin changes
        token = json.loads(urllib.urlopen(url + "?f=json", parameters).read())
        if "token" not in token:
            arcpy.AddError(token['messages'])
            quit()
        else:
            return token['token']

    def getServiceList(server, port,adminUser, adminPass, AGOUser, AGOPass, token=None, AGOtoken=None):
        if token is None:
            url = "http://{}:{}/arcgis/admin/generateToken".format(server, port)
            parameters = urllib.urlencode({'username':   adminUser,
                                           'password':   adminPass,
                                           'expiration': '60',
                                           'client':     'requestip'}) 
            token = gentoken(url,parameters) 

        services = []    
        folder = ''    
        url = "http://{}:{}/arcgis/admin/services{}?f=pjson&token={}".format(server, port, folder, token)    
        serviceList = json.loads(urllib2.urlopen(url).read())

        # Build up list of services at the root level
        for single in serviceList["services"]:
            services.append(["//",single['serviceName'],single['type']])
         
        # Build up list of folders and remove the System and Utilities folder (we dont want anyone playing with them)
        folderList = serviceList["folders"]
        folderList.remove("Utilities")             
        folderList.remove("System")
            
        if len(folderList) > 0:
            for folder in folderList:                                              
                url = "http://{}:{}/arcgis/admin/services/{}?f=pjson&token={}".format(server, port, folder, token)    
                fList = json.loads(urllib2.urlopen(url).read())
                
                for single in fList["services"]:
                    services.append([folder + "//", single['serviceName'],single['type']])

        for s in services:
            print s[0]+s[1]+"."+s[2]
            # add item to arcgis.com
            # get token
    ##        if AGOtoken is None:
    ##            url = 'https://www.arcgis.com/sharing/rest/generateToken?'
    ##            parameters = urllib.urlencode({'username':AGOUser,
    ##                                           'password':AGOPass,
    ##                                           'client':'referer',
    ##                                           'referer':'http://www.arcgis.com'})
    ##            AGOtoken = gentoken(url,parameters) 
    ##
    ##        url = 'http://tnc.maps.arcgis.com/sharing/rest/content/users/tguthrie@tnc.org_TNC/addItem?'
    ##        sourceURL = "http://{}:{}/arcgis/admin/services".format(server, port)
    ##        sourceType = ""
    ##        if s[2] == "MapServer": sourceType = "Map Service"
    ##        if s[2] == "FeatureServer": sourceType = "Feature Service"
        ##        if s[2] == "ImageServer": sourceType = "Image Service"
    ##        
    ##        parameters = urllib.urlencode({'URL':sourceURL,'title':s[1],'type':sourceType,'tags':'TNC,SDI','token':AGOtoken,'f':'json'})
    ##        response = urllib.urlopen(url, parameters).read()

    if __name__ == "__main__":     
        
        # Gather inputs      
        
        adminUser = "agsadmin" 
        adminPass = "This4now!"
        AGOUser = "tguthrie@tnc.org_TNC"
        AGOPass = "8ETh8dre"

        serverlist = [["wasde.tnc",6080],
                      ["mnsde.tnc",6080],
                      ["masde.tnc",6080],
                      ["ncsde.tnc",6080],
                      ["cosde.tnc",6080],
                      ["cospatial.tnc.org",6080],
                      ["nyspatial.tnc.org",6080],
                      ["cnbejarcgis.tnc",6080],
                      ["arfoarcgis.tnc.org",6080],
                      ["arcgis-cumulus-1459942432.us-west-1.elb.amazonaws.com",443]]

        for server,port in serverlist:
            print "-------------"
            print server
            print "-------------"
            try:
                getServiceList(server, port, adminUser, adminPass, AGOUser, AGOPass)
            except:
                print "Could not get list for", server



        
          
            
