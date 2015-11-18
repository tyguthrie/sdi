# Runs ETL for TNC Lands

# profile parameters
gp.workspace = "Database Connections\\SDEDEV_SA_STEWARD.sde"
gdb1 = "Database connections\\sdedev_sa_steward.sde"
gdb2 = "Database connections\\cosde_rmnode.sde"
replica = "SA_STEWARD.CA_TNC_LANDS"
direction = "FROM_GEODATABASE2_TO_1"
policy = "IN_FAVOR_OF_GDB2"
definition = "BY_ATTRIBUTE"
in_dataset = "SA_STEWARD.CA_TNC_INTEREST"
out_dataset = "SA_STEWARD.TEMP"
out_coor_system = "C:\\Program Files\\ArcGIS\\Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984.prj"
transform_method = "NAD_1983_To_WGS_1984_1"
sourceDataset = "wosdedev"
destDataset = "not_used"

# synchronize the replica
gp.SynchronizeChanges_management(gdb1, replica, gdb2, direction, policy, definition)
gp.addmessage("Synchronization completed successfully")

# reproject the dataset
gp.Project_management(in_dataset, out_dataset, out_coor_system, transform_method)
gp.addmessage("Reprojection completed successfully")

# create a temporary version
gp.CreateVersion_management(gp.workspace, "sde.DEFAULT", "TempETL", "PRIVATE")
gp.addmessage("Temporary version successfully created")

# run the ETL transformation
gp.CARO2RMProfile(sourceDataset, destDataset)
gp.addmessage("ETL transformation completed successfully")

# rec and post the edits to default
gp.reconcileversion_management(gp.workspace, "TempETL", "DEFAULT", "BY_ATTRIBUTE", "FAVOR_EDIT_VERSION", "NO_LOCK_AQUIRED","NO_ABORT", "POST")
gp.addmessage("Data reconciled and posted successfully")

# delete the temporary version
gp.DeleteVersion_management(gp.workspace, "TempETL")
gp.addmessage("Temporary version successfully deleted")

gp.addmessage(gp.getmessages)
