# This is written by Gareth
from Point import *


def cellLengthSort(cell):
    return abs(cell.locOverTime[-1].time - cell.locOverTime[0].time)

    
class Cell:

    #establish gen naming system
    def __init__(self, ident):
        self.id = ident
        self.daughterL = None
        self.daughterR = None
        self.parent = None
        self.genName = ""
        self.locOverTime = []
        self.clustered = -1

    def mitosis(self,left,right):
        self.daughterL = left
        left.parent = self
        left.genName = self.genName + "l"
        self.daughterR = right
        right.parent = self
        right.genName = self.genName + "r"

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
        vz = locFuture.z - locPresent.z
        locPast = Point(self.locOverTime[0].time - 1, locPresent.x - vx, locPresent.y - vy, locPresent.z - vz)
        return locPast

    def getChildCount(self, daughter):
        if daughter is None:
            return 0
        if (daughter.daughterL is None and daughter.daughterR is None):
            return 1
        else:
            return getChildCount(daughter.daughterL) + getChildCount(daughter.daughterR)

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

    #this means of determining birth frame seems unreliable
    def getBirth(self):
        if len(self.locOverTime) > 0:
            return self.locOverTime[0].time - 1
        else:
            return -2

    # Overwritten String Representation for Outputting.
    # Modify to construct gen name as appropriate from relation to parent cells (find meaning of a/l split)
    # Track mitosis level
    def __str__(self):
        birth = self.getBirth()
        rep = ""
        rep += ("{} {} 0 0 genName\n".format(self.getChildCount(self.daughterL),
                                             self.getChildCount(self.daughterR)))
        rep += ("{} 0 -1 -1 genName2\n".format(birth))
        rep += ("{} {} -1 -1 0 -1 {}\n".format(birth, len(self.genName), str(self.id) + self.genName))
        rep += ("{}\n".format(len(self.locOverTime)))
        for p in self.locOverTime:
            rep += ("{} {} {} {} -1 -1 -1 {}\n".format(p.time,
                                                       p.y, p.x, p.z, p.comment))
        if self.daughterL != None:
            rep += str(self.daughterL)
        if self.daughterR != None:
            rep += str(self.daughterR)
        rep += "---\n"
        return rep
