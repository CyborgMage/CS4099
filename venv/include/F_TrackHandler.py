from Cell import *
from F_Lib import update_console
import math

distFloor = 20

def cellDist(cellOne, cellTwo):
    x_dist = abs(cellOne.locOverTime[-1].x - cellTwo.locOverTime[-1].x) **2
    y_dist = abs(cellOne.locOverTime[-1].y - cellTwo.locOverTime[-1].y) **2
    z_dist = (abs(cellOne.locOverTime[-1].z - cellTwo.locOverTime[-1].z) *2 )** 2
    return math.sqrt(x_dist + y_dist + z_dist)

def pointDist(pointOne, pointTwo):
    x_dist = abs(pointOne.x - pointTwo.x) **2
    y_dist = abs(pointOne.y - pointTwo.y) **2
    z_dist = (abs(pointOne.z - pointTwo.z) *2 )** 2
    return math.sqrt(x_dist + y_dist + z_dist)

# Add a given cell to tracking info.
def addCellToTracked(time, newcell, cellList):
    distances = []
    counter = 0
    for cell in cellList:
        distance = cellDist(cell, newcell)
        distances.append(distance)
    while (counter < 2):
        minDist = min(distances)
        index = distances.index(minDist)
        diff = abs(cellList[index].lastTracked() - newcell.lastTracked())
        if abs(minDist) > distFloor:
            newCell = Cell(len(cellList))
            loc = newcell.lastLoc()
            newCell.addLocTime(loc.time, loc.x, loc.y, loc.z)
            cellList.append(newCell)
            break
        if diff > 0:
            loc = newcell.lastLoc()
            cellList[index].addLocTime(loc.time, loc.x, loc.y, loc.z)
            return
        else:
            distances[index] = 100000
        counter += 1


# Add new cellsto cell List.
def iterateThroughCells(cells, cellList):
    if len(cells) == 0:
        return cellList, []
    time = cells[0].lastLoc().time
    for cell in cells:
        addCellToTracked(1, cell, cellList)
    cellLis, discarded = cellCleanup(cellList, time)
    return cellLis, discarded


def cellCleanup(cellList, time):
    discarded = [x for x in cellList if tooOld(x, time)]
    lis = cellList
    lis = [x for x in cellList if not tooOld(x, time)]
    return lis, discarded


def tooOld(cell, time):
    return abs((cell.locOverTime[-1].time - time)) > 3


def tooShort(cell, time):
    return len(cell.locOverTime) < time


# Output Framework for Lists of Cells.
def outputData(cellLists):
    text = "SIMI*BIOCELL\n400\n---\n0\n---\n1 1\n0\n---\n"
    for cell in cellLists:
        text += str(cell)
    file_save = "../Output/output.smd"
    txt_output = open(file_save, 'w')
    update_console("Saving the SBD file at location: " + file_save)
    txt_output.write(text)
    txt_output.close()
