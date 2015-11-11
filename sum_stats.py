# summarizes statistics on map service activity 
import time, datetime, os

# run in the current location of the py script
dir = os.getcwd()

# get user input to create date filter
start = raw_input("Start date in format mm/dd/yy or ENTER for all ")
end = raw_input("End date in format mm/dd/yy or ENTER for all ")

# if user input not a valid date, then use default date values (e.g. all dates)
try:
    dt_start = datetime.datetime.strptime(start, '%m/%d/%y')
except ValueError:
    dt_start = datetime.datetime.fromordinal(1) 
try:
    dt_end = datetime.datetime.strptime(end, '%m/%d/%y')
except ValueError:
    dt_end = datetime.datetime.now()

# read each file in the folder that meets the filter criteria
hitDict = {}
for name in os.listdir(dir):
    basename, extension = os.path.splitext(name)
    fileDate = datetime.datetime.fromtimestamp(os.stat(name).st_mtime)
    if (extension.lower() == ".txt" and
       fileDate >= dt_start and
       fileDate <= dt_end and
       name <> "LogSummary.txt"):
        
# open the txt file and parse its contents (exccept if its the header)
        with open(os.path.join(dir, name),'r') as filestream:
             for line in filestream:
                 if line <> "Service,Number of hits,Average seconds per draw\n":
                     currentline = line.split(",")
                     keyCheck = currentline[0]
                     numberHits = int(currentline[1])
                     elapsed = float(currentline[2]) * numberHits
                     if keyCheck in hitDict:
                         stats = hitDict[keyCheck]
                         stats[0] += numberHits
                         stats[1] += elapsed
                     else:
                         hitDict[keyCheck] = [numberHits,elapsed]

# summarize the dictionary and then write to file 
summaryFile = open(os.path.join(dir,"LogSummary.txt"), "w")
header = "Service,Number of hits,Average seconds per draw\n"
summaryFile.write(header)
for key in hitDict:
    totalDraws = hitDict[key][0]
    totalElapsed = hitDict[key][1]
    avgElapsed = 0
    if totalDraws > 0: avgElapsed = (1.0 * (totalElapsed / totalDraws)) 
    line = key + "," + str(totalDraws) + "," + str(avgElapsed) + "\n"
    summaryFile.write(line)
summaryFile.close()
