# sdi
Code supporting Spatial Data Infrastructure at The Nature Conservancy

A collection of custom python scripts, classes and functions for spatial data analysis. Use as templates, or import the whole thing into your python project

## Tips:
- Use “feature layer” input to select layers within arcmap
- Filters can be used for validating parameters
- Multivalues - use python split function to create list
- do projection on the fly with search cursor using the spatial reference parameter
- Use testSchemaLock when updating features
- Use objects to set parameters where really long strings required such as spatial reference
- Use a value table instead of a long string for multivalue parameters
- Addfielddelimiters will create the appropriate delimiters for a workspace/fc/fieldname
- Use describe shapefieldname rather than [shape] in case it has a different name
- In services: use feature sets and record sets instead of feature classes
- In script use addToolbox to add the url of the services
- ArcSDESQLExecute object can access the database directly
- Write to scratch workspace when using services
- to see layer's data source: print arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT"))[i].dataSource
