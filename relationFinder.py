import sys
from db import DB
from collections import namedtuple

Degrees = namedtuple('Degrees', 'Name, Level, Id, Gender, Step, Inlaw')
relations = {
        0: { 
            0: { "MALE": "Husband", "FEMALE": "Wife" },
            -1:{ "MALE": "Son", "FEMALE": "Daughter"},
            -2:{ "MALE": "Grandson", "FEMALE": "Granddaughter"}
            },
        1: { 
            1: { "MALE": "Father", "FEMALE": "Mother"},
            0: { "MALE": "Brother", "FEMALE": "Sister" }
            },
        2: {
            2: { "MALE": "Grandfather", "FEMALE": "Grandmother" },
            1: { "MALE": "Uncle", "FEMALE": "Aunt" },
            0: { "MALE": "Cousin", "FEMALE": "Cousin" },
            -1: {"MALE": "Nephew", "FEMALE": "Neice"},
            -2: {"MALE": "Grandnephew", "FEMALE": "Grandneice"}
            },
        'spouse' : { "MALE": "Husband", "FEMALE":"Wife" },
        'parent' : { "MALE": "Father",  "FEMALE": "Mother" },
        'child'  : { "MALE": "Son",     "FEMALE": "Daughter"},
        'sibling': { "MALE": "Brother", "FEMALE": "Sister"  }
        }
class RelationFinder(DB):
    def printMember(self,me):
        print "Name: {}".format(me)
        spouse = self.getSpouse(me)
        if spouse != None:
            print "{}: {}".format(relations["spouse"][spouse.Gender], spouse.Name)
        parents = self.getParents(me)
        for parent in parents:
            print "{}: {}".format(relations["parent"][parent.Gender], parent.Name)
        children = self.getChildren(me)
        for child in children:
            print "{}: {}".format(relations["child"][child.Gender], child.Name)
        siblings = self.getSiblings(me)
        for sibling in siblings:
            print "{}: {}".format(relations["sibling"][sibling.Gender], sibling.Name)

    def findAllAncestors(self,me,ls=None,lvl=0):
        if me == None:
            return ls 
        if ls == None:
            ls = list()
        p = self.lookupByName(me)
        ls.append( Degrees(Name=p.Name, Id=p.Id, Gender=p.Gender, Level=lvl, Step=False, Inlaw=False) )
        parents = self.getParents(me)
        p = self.getSpouse(me)
        if p:
            ls.append( Degrees(Name=p.Name, Id=p.Id, Gender=p.Gender, Level=lvl, Step=False, Inlaw=True) )
        for p in parents:
            spouse = self.getSpouse(p.Name)
            if spouse and spouse not in parents:
                ls.append( Degrees(Name=spouse.Name, Id=spouse.Id, Gender=spouse.Gender, Level=lvl+1, Step=True, Inlaw=False) )
            self.findAllAncestors(p.Name,ls,lvl+1)
        return ls

    def findRelationship(self,name1,name2,doSpouse=0):
        p1 = self.lookupByName(name1)
        p2 = self.lookupByName(name2)
        if p1.Id == p2.Id:
            return "Self"
        source = self.findAllAncestors(name1)
        dest = self.findAllAncestors(name2)
        ids = map(lambda x: x.Id, dest)
        minDist = 999
        minRelate = ""
        for x in source:
            try:
                d = dest[ids.index(x.Id)]
                if doSpouse == 2:
                    spouse = self.getSpouse(p2.Name)
                    relate = relations[ x.Level ][ x.Level - d.Level ][ spouse.Gender ] 
                else:
                    relate = relations[ x.Level ][ x.Level - d.Level ][ p2.Gender ] 
                if d.Step:
                    relate = "Step " + relate
                if x.Level+d.Level < minDist:
                    minDist = x.Level+d.Level
                    minRelate = relate
            except:
                pass
        if minRelate != "":
            return minRelate

        # Not directly related, try in-laws"
        spouse = self.getSpouse(name1)
        if spouse and doSpouse < 1: 
            relate = self.findRelationship(spouse.Name,name2,doSpouse=1)
            if relate == "Self":
                return relations['spouse'][spouse.Gender]
            if relate != "None":
                return "{}-in-law".format(relate)
        spouse = self.getSpouse(name2)
        if spouse and doSpouse < 1: 
            relate = self.findRelationship(name1,spouse.Name,doSpouse=2)
            if relate != "None":
                return "{}".format(relate)
        return "None"

if __name__ == "__main__": 
    rf = RelationFinder()
    rf.open("test.db")
    '''
    name1 = sys.argv[1]
    name2 = sys.argv[2]
    print "{}->{}, {}".format(name1,name2,rf.findRelationship(name1,name2))
    '''
    '''
    for p in rf.listNames():
        print "---------------------"
        rf.printMember(p)
        print "---------------------"
    '''
    names = [ 
            ("Chris Leaf", "Chris Leaf"),
            ("Ali Torres-Leaf", "Chris Leaf"),
            ("Ali Torres-Leaf", "Natalie Fagundo-Castro"),
            ("Chris Leaf", "Gary Leaf"),
            ("Chris Leaf", "Clyde Leaf"),
            ("Chris Leaf", "Natalie Fagundo-Castro"),
            ("Ali Torres-Leaf", "Felix Castro"),
            ("Chris Leaf", "Felix Castro"),
            ("Ali Torres-Leaf", "Carl Wastradowski"),
            ("Carl Wastradowski", "Chris Leaf"),
            ("Carl Wastradowski", "Ali Torres-Leaf")
            ]
    for name1,name2 in names:
        print "{}->{}, {}".format(name1,name2,rf.findRelationship(name1,name2))

