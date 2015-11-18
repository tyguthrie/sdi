# Syncs TNC lands data

# get current date
today = strftime("%Y%m%d")

# parameters
gp.workspace = 'D:/Ty/tooldata/TNC Lands Domains.mdb' # workspace and location of domains database
tbl = "Database Connections/SDE.COSDE.DEFAULT.sde/replicas_fc" # replicas table
gdb1 = "Database Connections/SDELOADER.COSDE.QA.sde" # parent geodatabase
constring = "http://tncgis:zapata!@twitter.com/statuses/update.json" #twitter connection string


# get the domains tables
domains = gp.listtables()
# open the replicas table
uc = gp.UpdateCursor(tbl)
row = uc.Next()

while row:
    
    try: # synchronize datasets
        if row.sync == "X":
            # set the child default protection to public
            gp.AlterVersion_management(row.sde, "DEFAULT", "#", "#", "PUBLIC")
            # synch
            
            message = "synching " + row.replica
            tweet = urllib.urlencode({"status":message})
            f = urllib.urlopen(constring, tweet)
            gp.addmessage(message)
            
            gp.SynchronizeChanges_management(gdb1, row.replica, row.gdb2, row.direction, row.policy, row.definition)
            #set the child default protection to protected
            #gp.AlterVersion_management(row.sde, "DEFAULT", "#", "#", "PROTECTED")
            row.setvalue("result","pass")
            row.setvalue("syncdate",today)
    except:
        row.setvalue("result","fail")
        message = "Sync failed for " + row.replica
        tweet = urllib.urlencode({"status":message})
        f = urllib.urlopen(constring, tweet)
        gp.addmessage(message)
    
    try: # synchronize domains
        if row.sync == "X":
            for domain in domains:
                message = "Synchronizing Domain " + domain
                gp.addmessage(message)
                gp.TableToDomain_management(domain, "code", "field", row.gdb2, domain, "#", "REPLACE")

    except:
        message = "Domain Sync Failed for domain: " + domain
        tweet = urllib.urlencode({"status":message})
        f = urllib.urlopen(constring, tweet)
        gp.addmessage(message)

    try: # reconcile and post for local editor versions
        if row.recpost == "X":
            # rec and post
            message = "reconcile and post " + row.version
            tweet = urllib.urlencode({"status":message})
            f = urllib.urlopen(constring, tweet)
            gp.addmessage(message)
            gp.reconcileversion_management(row.gdb2, row.version, "SDELOADER.QA", row.definition, "FAVOR_EDIT_VERSION", "NO_LOCK_AQUIRED","NO_ABORT", "POST")
            row.setvalue("result","pass")
            row.setvalue("syncdate",today)
    except:
        row.setvalue("result","fail")
        message = "rec and post failed for " + row.version
        tweet = urllib.urlencode({"status":message})
        f = urllib.urlopen(constring, tweet)
        gp.addmessage(message)

    try: # get count for gdb1
        result = gp.GetCount_management(gdb1+ "\\SDELOADER.TNC_LANDS")
        record_count = int(result.GetOutput(0))
        row.setvalue("GDB1_count",record_count)
    except:
        row.setvalue("GDB1_count","-1")

    try: # get count for gdb2
        result = gp.GetCount_management(row.gdb2+ "\\SDELOADER.TNC_LANDS")
        record_count = int(result.GetOutput(0))
        row.setvalue("GDB2_count",record_count)
    except:
        row.setvalue("GDB2_count","-1")

    uc.UpdateRow(row)
    row = uc.Next()
