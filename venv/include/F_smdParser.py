# This is written by Gareth
import csv, math
from Cell import *
from F_Lib import update_console


def parseSMD(smdfile):
    cellList = []
    # Skip first 8 lines as they are SIMI Biocell Metadata
    smd = open(smdfile, "r")
    reader = csv.reader(smd)
    for x in range(0, 8):
        next(reader)
    cellCounter = 0
    for line in reader:
        # Ignore first few lines of input as they are cell metadata.
        for x in range(0, 3):
            line = next(reader)
        cell = Cell(cellCounter)
        rows = int(line[0])

        # Obtain Cell Postitions
        for coordLine in range(0, rows):
            line = next(reader)
            coord = line[0].split()
            cell.addLocTime(int(coord[0]), int(coord[1])
                            , int(coord[2]), int(coord[3]))
            if len(coord) == 8:
                if 'CD' in coord[7]:
                    cell.locOverTime[-1].comment = 'CD'

        cellCounter += 1
        if rows > 0:
            cellList.append(cell)
        line = next(reader)
    for x in range(0, len(cellList)):
        cellList[x].locOverTime = interpolatePoints(cellList[x])
    return cellList


def parseSMDMitotic(smdfile):
    cellList = []
    referenceList = []
    # Skip first 8 lines as they are SIMI Biocell Metadata
    smd = open(smdfile, "r")
    reader = csv.reader(smd)
    for x in range(0, 8):
        next(reader)
    cellCounter = 0
    for line in reader:
        # Ignore first few lines of input as they are cell metadata.
        mitotic = False
        # Instead: locate mitosis level(?) and/or left/right active cells and mark cell as involved in mitosis
        for x in range(0, 3):
            meta = line[0].split()
            if x == 0:
                mitotic = int(meta[0]) > 0 or int(meta[1]) > 0
            elif x == 2 and mitotic == False:
                mitotic = int(meta[1]) > 0
            line = next(reader)
        cell = Cell(cellCounter)
        meta = line[0].split()
        rows = int(meta[0])

        # Obtain Cell Postitions
        for coordLine in range(0, rows):
            line = next(reader)
            coord = line[0].split()
            cell.addLocTime(int(coord[0]), int(coord[1])
                            , int(coord[2]), int(coord[3]))
            if len(coord) == 8:
                if 'CD' in coord[7]:
                    cell.locOverTime[-1].comment = 'CD'

        cellCounter += 1
        if rows > 0:
            referenceList.append(cell)
            if mitotic:
                cellList.append(cell)
        line = next(reader)
    for x in range(0, len(cellList)):
        cellList[x].locOverTime = interpolatePoints(cellList[x])
    update_console("Number of overall cells in {}: {}, of which {} are involved in mitosis".format(smdfile, len(referenceList), len(cellList)))
    return cellList


# Interpolate the Movement of Cells provided from data.
def interpolatePoints(cell):
    locs = cell.locOverTime
    additionaltimes = []
    # Check every entry for missed time steps.
    for x in range(0, len(locs) - 1):
        time = locs[x].time
        diff = locs[x + 1].time - locs[x].time
        x_movement = (locs[x + 1].x - locs[x].x) / diff
        y_movement = (locs[x + 1].y - locs[x].y) / diff
        z_movement = (locs[x + 1].z - locs[x].z) / diff
        # If cell tracking is missed for a frame or more, interpolate.
        if diff > 1:
            for d in range(1, diff):
                newx = int(x_movement * d + locs[x].x)
                newy = int(y_movement * d + locs[x].y)
                newz = int(z_movement * d + locs[x].z)
                additionaltimes.append(Point(time + d, newx, newy, newz))
    # Return interpolated results.
    locs = locs + additionaltimes
    locs.sort()
    return locs


# For mitosis: restrict specifically to mitotic cells in both files?
def error_tracking(auto_tracked_file_path, manual_tracked_file_path, csv_name, mitosis):
    update_console("Starting SBD file parsing...")
    if mitosis:
        objectCells = parseSMDMitotic(manual_tracked_file_path)
        subjectCells = parseSMDMitotic(auto_tracked_file_path)
    else:
        objectCells = parseSMD(auto_tracked_file_path)
        subjectCells = parseSMD(manual_tracked_file_path)

    errorfile = open(csv_name, 'w')
    errorfile.write("Manual Cell ID,RMSError,AverageError,ManualLength,AutoLength\n")

    for subCell in subjectCells:
        if len(subCell.locOverTime) > 10:
            distanceList = [avPointDifference(subCell, c) for c in objectCells]
            minDist = min(distanceList)
            match = objectCells[distanceList.index(minDist)]

            average_error, rms_error = avPointDifference(subCell, match, False)

            update_console(
                "Report for cell ID: {}, RMS error: {}, Average error: {}, Auto tracked length: {}, Manual tracked length: {}".
                format(subCell.id, rms_error, average_error, len(match.locOverTime), len(subCell.locOverTime)))

            errorfile.write("{},{},{},{},{}\n".format(subCell.id, rms_error, average_error, len(match.locOverTime),
                                                      len(subCell.locOverTime)))


def error_centroid(auto_tracked_file_path, manual_tracked_file_path, csv_name, mitosis):
    update_console("Starting SBD file parsing...")
    if mitosis:
        outputCells = parseSMDMitotic(auto_tracked_file_path)
        manualCells = parseSMDMitotic(manual_tracked_file_path)
    else:
        outputCells = parseSMD(auto_tracked_file_path)
        manualCells = parseSMD(manual_tracked_file_path)

    errorfile = open(csv_name, 'w')
    errorfile.write("Time,RMSError,TotalError,AverageError,ManTrackedCells,AutoTrackedCells\n")
    for t in range(0, 369):
        counter = 0
        manLocsT = getListOfPointsAtTime(manualCells, t + 19)
        outLocsT = getListOfPointsAtTime(outputCells, t)
        error = 0
        avError = 0
        rmsError = 0
        if len(manLocsT) > 0 and len(outLocsT) > 0:
            for loc in manLocsT:
                distances = [pointDist(loc, l) for l in outLocsT]
                minDist = min(distances)
                error += minDist
                counter += 1
            avError = error / counter
            rmsError = math.sqrt(avError)
        update_console("Report at time frame: Frame no: {}, RMS Error: {}, Total Error: {}, Average Error: {}, "
                       "Manual cell count: {}, Auto cell count: {}".format(t, rmsError, error, avError,
                                                                           len(manLocsT), len(outLocsT)))
        errorfile.write("{},{},{},{},{},{}\n".format(t, rmsError, error, avError, len(manLocsT), len(outLocsT)))


def error_death(auto_tracked_file_path, manual_tracked_file_path, csv_name):
    # update_console("Starting SBD file parsing...")
    outputCells = parseSMD(auto_tracked_file_path)
    manualCells = parseSMD(manual_tracked_file_path)

    errorfile = open(csv_name, 'w')
    errorfile.write("Manual Cell ID,TrackedDead,RMSError\n")

    for single_manual_cell in manualCells:
        if len(single_manual_cell.locOverTime) > 10:
            if single_manual_cell.locOverTime[-1].comment == 'CD':

                # 4 Frame as offset
                min_range_frame = single_manual_cell.locOverTime[-1].time - 4
                max_range_frame = single_manual_cell.locOverTime[-1].time + 4

                possible_auto_dead = []
                # Select possible similar dead cell.
                for single_auto_cell in outputCells:
                    if len(single_auto_cell.locOverTime) > 10:
                        if min_range_frame < single_auto_cell.locOverTime[-1].time < max_range_frame:
                            possible_auto_dead.append(single_auto_cell)

                # Select with minimum error.
                distanceList = []
                for single_possible_auto_dead in possible_auto_dead:
                    distanceList.append(pointDist(single_possible_auto_dead.locOverTime[-1],
                                                  single_manual_cell.locOverTime[-1]))

                if len(distanceList) > 0:
                    minDist = min(distanceList)
                    match = possible_auto_dead[distanceList.index(minDist)]
                    rms_error = math.sqrt(minDist)
                    errorfile.write("{},{},{}\n".format(single_manual_cell.id, 'Yes', rms_error))
                else:
                    errorfile.write("{},{},{}\n".format(single_manual_cell.id, 'No', 0))
    print('Completed...')


# Get a list of all the points which are occupied at time T.
def getListOfPointsAtTime(cells, t):
    cellAtT = []
    for cell in cells:
        locs = cell.locOverTime
        locAtTime = checkForTime(locs, t)
        if locAtTime is not None:
            cellAtT.append(Point(locAtTime.time, locAtTime.x, locAtTime.y, locAtTime.z))
    return cellAtT


# Find matching time locations.
def checkForTime(locs, time):
    for point in locs:
        if point.time == time:
            return point
    return None


# Calculate average distance between like points.
def avPointDifference(manCell, autoCell, compute=True):
    auto_locs = autoCell.locOverTime
    counter = 0
    totalDist = 0
    for loc in manCell.locOverTime:
        for au_loc in auto_locs:
            if au_loc.time == loc.time:
                counter += 1
                totalDist += pointDist(loc, au_loc)
    av = 1000000
    rms = 1000000

    if counter > 0:
        av = int(totalDist / counter)
        rms = math.sqrt(totalDist / counter)

    if compute:
        av = av * (len(manCell.locOverTime) / len(autoCell.locOverTime))
        rms = rms * (len(manCell.locOverTime) / len(autoCell.locOverTime))

    return av, rms


def pointDist(pointOne, pointTwo):
    x_dist = abs(pointOne.x - pointTwo.x) ** 2
    y_dist = abs(pointOne.y - pointTwo.y) ** 2
    z_dist = (abs(pointOne.z - pointTwo.z)) ** 2
    return math.sqrt(x_dist + y_dist + z_dist)
