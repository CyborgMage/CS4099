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
    i = 1
    switcher = {
        1: "1 1 0 0 P0\n-2 0 -1 -1\n-3 0 -1 -1 4 16711935\n0",
        2: "1 1 0 0 AB\n-2 0 -1 -1\n0 0 -1 -1 0 255\n0",
        3: "1 1 0 0 ABa\n-2 0 -1 -1\n3 0 -1 -1 0 255\n0",
        4: "1 1 0 0 ABaa\n-2 0 -1 -1 ABal\n6 0 -1 -1 0 255 ABal\n0",
        5: "1 1 0 0 ABaaa\n-2 0 -1 -1 ABala\n9 0 -1 -1 0 255 ABala\n0",
        6: "1 1 0 0 ABaaaa\n-2 0 -1 -1 ABalaa\n11 0 -1 -1 0 255 ABalaa\n0",
        7: "1 1 0 0 ABaaaaa\n-2 0 -1 -1 ABalaaa\n14 0 -1 -1 0 255 ABalaaa\n0",
        8: "1 1 0 0 ABaaaaaa\n-2 0 -1 -1 ABalaaaa\n17 0 -1 -1 0 33023 ABalaaaa\n0",
        9: "1 1 0 0 ABaaaaaaa\n-2 0 -1 -1 ABalaaaal\n20 0 -1 -1 0 33023 ABalaaaal\n0"
    }
    dummyName = "ABalaaaal"
    while i < 10:
        text += switcher[i]
        i += 1
    for cell in cellLists:
        if cell.parent is None:
            cell.attach(dummyName)
        text += str(cell)
    file_save = "../Output/output.smd"
    txt_output = open(file_save, 'w')
    update_console("Saving the SBD file at location: " + file_save)
    txt_output.write(text)
    txt_output.close()
