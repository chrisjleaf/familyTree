import sqlite3 as lite
import sys
from collections import namedtuple

relations = {}

Person = namedtuple('Person', 'Name, Gender, Id')

class DB: 
    ###
    # DB Init/Cleanup
    def open(self, name):
        self.con = lite.connect(name)
        self.cur = self.con.cursor()
    def close(self):
        self.con.commit()
        self.con.close()

    ###
    # Table Init/Reset
    def makeTables(self):
        self.cur.execute("CREATE TABLE Members(Id integer primary key autoincrement, name TEXT, gender TEXT, PId1 INT, PId2 INT, SId INT)")

    def clearTables(self):
        self.cur.execute("DROP TABLE IF EXISTS Members")

    ###
    # Person Management
    def makePerson(self, p):
        self.cur.execute("INSERT INTO Members (Name, Gender) VALUES ('{}', '{}')".format(p.Name,p.Gender))

    def lookupByName(self, name):
        self.cur.execute("SELECT Gender,Id FROM Members WHERE Name='{}'".format(name))
        data = self.cur.fetchone()
        return Person(Name=name, Gender=data[0], Id=data[1])

    def lookupById(self, me):
        if me == None:
            return None
        self.cur.execute("SELECT Name,Gender FROM Members WHERE Id='{}'".format(me))
        data = self.cur.fetchone()
        return Person(Name=data[0], Gender=data[1], Id=me)

    def listNames(self):
        self.cur.execute("SELECT Name From Members")
        return [p[0] for p in self.cur.fetchall()]

    ###
    # Relationship Control
    def addParent(self, me, parent):
        self.cur.execute("SELECT Id,PId1,PId2 FROM Members WHERE Name='{}'".format(me))
        myId,pId1,pId2 = self.cur.fetchone()
        parentId = self.lookupByName(parent).Id
        if pId1 == None:
            self.cur.execute("UPDATE Members SET PId1='{}' WHERE Id='{}'".format(parentId, myId))
        elif pId2 == None:
            self.cur.execute("UPDATE Members SET PId2='{}' WHERE Id='{}'".format(parentId, myId))
        else:
            parents = [p.Name for p in self.getParents(me)]
            print "Two Parents already exist: {}".format(parents) 

    def addParents(self, me, parents):
        for p in parents:
            self.addParent(me, p)

    def getParents(self,me):
        self.cur.execute("SELECT PId1,PId2 FROM Members WHERE Name='{}'".format(me))
        ids = [ x for x in self.cur.fetchone() if x is not None ]
        return map(lambda x : self.lookupById(x), ids)

    def getChildren(self,me):
        myId = self.lookupByName(me).Id
        self.cur.execute("SELECT Id,Name,Gender FROM Members WHERE PId1='{}' OR PId2='{}'".format(myId,myId))
        return [Person(Id=x[0],Name=x[1],Gender=x[2]) for x in self.cur.fetchall()]

    def getSiblings(self,me):
        myId = self.lookupByName(me).Id
        self.cur.execute("SELECT PId1,PId2 FROM Members WHERE Name='{}'".format(me))
        pids = [ x for x in self.cur.fetchone() if x is not None ]
        ps = []
        for pid in pids:
            self.cur.execute("SELECT Id,Name,Gender FROM Members WHERE Id!={} AND (PId1={} OR PId2={})".format(myId,pid,pid))
            ps.extend( [Person(Id=d[0], Name=d[1], Gender=d[2]) for d in self.cur.fetchall()])
        return list(set(ps))
        
    def addSpouse(self, me, spouse):
        myId = self.lookupByName(me).Id
        spouseId = self.getIdByName(spouse)
        self.cur.execute("UPDATE Members SET SId={} WHERE Id={}".format(spouseId, myId))
        self.cur.execute("UPDATE Members SET SId={} WHERE Id={}".format(myId, spouseId))

    def getSpouse(self,me):
        self.cur.execute("SELECT SId FROM Members WHERE Name='{}'".format(me))
        return self.lookupById(self.cur.fetchone()[0])


if __name__ == "__main__":
    db = DB()
    db.open("test.db")
    '''
    db.clearTables()
    db.makeTables()
    db.makePerson("Gary Leaf", "MALE")
    db.makePerson("Patti Leaf", "FEMALE")
    db.makePerson("Chris Leaf", "MALE")
    db.makePerson("Michael Leaf", "MALE")
    db.makePerson("Marc Torres", "MALE")
    db.makePerson("Natalie Fagundo-Castro", "FEMALE")
    db.makePerson("Felix Castro", "MALE")
    db.makePerson("Ali Torres-Leaf", "FEMALE")
    db.makePerson("Karla Torres", "FEMALE")
    db.makePerson("Kevin Torres", "MALE")
    db.makePerson("Vivian Leaf", "FEMALE")
    db.makePerson("Clyde Leaf", "MALE")
    db.makePerson("Doris Wastradowski", "FEMALE")
    db.makePerson("Carl Wastradowski", "MALE")
    db.makePerson("Kristy Mcgree", "FEMALE")
    db.makePerson("Jane Sheridan", "FEMALE")
    db.makePerson("Bill Wastradowski", "MALE")


    db.addSpouse("Chris Leaf", "Ali Torres-Leaf")
    db.addSpouse("Gary Leaf", "Patti Leaf")
    db.addSpouse("Felix Castro", "Natalie Fagundo-Castro")

    db.addParents("Chris Leaf", ["Gary Leaf", "Patti Leaf"])
    db.addParents("Michael Leaf", ["Gary Leaf", "Patti Leaf"])
    db.addParents("Ali Torres-Leaf", ["Natalie Fagundo-Castro","Marc Torres"])
    db.addParents("Karla Torres", ["Natalie Fagundo-Castro","Marc Torres"])
    db.addParents("Kevin Torres", ["Natalie Fagundo-Castro","Marc Torres"])
    db.addParents("Gary Leaf", ["Clyde Leaf","Vivian Leaf"])
    db.addParents("Patti Leaf", ["Carl Wastradowski","Doris Wastradowski"])
    db.addParents("Kristy Mcgree", ["Clyde Leaf","Vivian Leaf"])
    db.addParents("Jane Sheridan", ["Carl Wastradowski","Doris Wastradowski"])
    db.addParents("Bill Wastradowski", ["Carl Wastradowski","Doris Wastradowski"])
    '''

    '''
    print (db.lookupByName('Chris Leaf'))
    print (db.getParents('Chris Leaf'))
    print (db.getChildren('Gary Leaf'))
    print (db.getSiblings('Chris Leaf'))
    '''
    db.close()
