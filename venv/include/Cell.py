# This is written by Gareth
from Point import *

from math import sqrt

import re

def cellLengthSort(cell):
    return abs(cell.locOverTime[-1].time - cell.locOverTime[0].time)

def cellPointDist(point1, point2):
    if abs(point1.z - point2.z) > 1:
        return float("inf");
    else:
        return sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def getChildCount(daughter):
    if daughter is None:
        return 0
    if daughter.daughterL is None and daughter.daughterR is None:
        return 1
    else:
        return getChildCount(daughter.daughterL) + getChildCount(daughter.daughterR)


class Cell:

    #establish gen naming system
    def __init__(self, ident):
        self.id = ident
        self.daughterL = None
        self.daughterR = None
        self.parent = None
        self.genName = ""
        self.idString = ""
        self.attachPoint = ""
        self.locOverTime = []
        self.regressedLocTime = None
        self.clustered = -1

    def mitosis(self,left,right):
        self.daughterL = left
        left.parent = self
        left.genName = "l"
        self.daughterR = right
        right.parent = self
        right.genName = "r"

    def death(self):
        self.locOverTime[-1].comment = "Cell has Died"

    def lastTracked(self):
        return self.locOverTime[-1].time

    def lastLoc(self):
        return self.locOverTime[-1]

    def locAt(self, time):
        for x in self.locOverTime:
            if x.time == time:
                return x
        return None

    def addDaughter(self, left, cell):
        if left:
            self.daughterL = cell
        else:
            self.daughterR = cell

    def addLocTime(self, time, x, y, z):
        self.locOverTime.append(Point(time, x, y, z))

    #requires bound checking if generalised, potentially check point subtraction
    #z coordinate checking may need to be more refined somehow
    def regressLocTime(self):
        locPresent = self.locOverTime[0]
        locFuture = self.locOverTime[1]
        vx = locFuture.x - locPresent.x
        vy = locFuture.y - locPresent.y
        self.regressedLocTime = Point(self.locOverTime[0].time - 1, locPresent.x - vx, locPresent.y - vy, self.locOverTime[0].z)

    def to_dict(self):
        loc = self.locOverTime[-1]
        return {'x': loc.x,
                'y': loc.y,
                'z': loc.z}
    
    def to_dict_cluster(self):
        loc = self.locOverTime[-1]
        return {'x': loc.x,
                'y': loc.y,
                'z': (loc.z * 15)}

    def setClustered(self, cluster):
        self.clustered = cluster

    def getBirth(self):
        if len(self.locOverTime) > 0:
            return self.locOverTime[0].time - 1
        else:
            return -2

    def attach(self, attach):
        self.attachPoint = attach

    # Overwritten String Representation for Outputting.
    # Modify to construct gen name as appropriate from relation to parent cells (find meaning of a/l split)
    # Track mitosis level
    def __str__(self):
        birth = self.getBirth()
        genLength = 0
        parentName = ""
        if self.parent is None:
            self.idString = str(self.id)
            parentName = self.attachPoint
        else:
            self.idString = self.parent.idString + self.genName
            parentName = self.parent.idString + self.parent.genName
            genLength = len(re.findall('[lr]', self.idString))
        rep = ""
        rep += ("{} {} 0 0 {}\n".format(getChildCount(self.daughterL), getChildCount(self.daughterR), parentName))
        rep += ("{} 0 -1 -1 {}\n".format(birth, self.idString))
        rep += ("{} {} -1 -1 0 -1 {}\n".format(birth, genLength, self.idString))
        rep += ("{}\n".format(len(self.locOverTime)))
        for p in self.locOverTime:
            rep += ("{} {} {} {} -1 -1 -1 {}\n".format(p.time,
                                                       p.y, p.x, p.z, p.comment))
        if self.daughterL is not None:
            rep += str(self.daughterL)
        if self.daughterR is not None:
            rep += str(self.daughterR)
        rep += "---\n"
        return rep
