class Node:
    def __init__(self,name):
        self.name = name
        self.min    = -1
        self.prime  = -1
        self.max    = -1
        self.hight  = -1
        self.marked = False
        self.root = False
    
    def initNode(self):
        self.min    = -1
        self.prime  = -1
        self.max    = -1
        self.hight  = -1
        self.marked = False
    
    def __str__(self):
        print('amirros debug') 
               
    def setRoot(self):
        self.root = True
    
    def isRoot(self):
        return self.root
    
    def mark(self,val):
        self.marked = val

    def getMark(self):
        return self.marked
        
    def isMarked(self):
        if self.getMark(): return True
        return False

    def changeName(self,newName):
        self.name = newName

    def getName(self):
        return self.name
    
    def setMin(self,val):
        self.min = val
    
    def getMin(self):
        return self.min
    
    def getMax(self):
        return self.max
    
    def setMax(self,val):
        self.max =val
    
    def setPrime(self,val):
        self.prime = val
 
    def getPrime(self):
        return self.prime
    
    def setHight(self,val):
        self.hight = val
    
    def getHight(self):
        return self.hight
    
    def printNode(self):
        print("name: {}".format(self.name))
        print("marked: {}".format(self.marked))
        print('----------------')

class AndNode(Node):
    fanin = 2
    def __init__(self,name):
        Node.__init__(self,name)

class NotNode(Node):
    fanin = 1
    def __init__(self,name):
        Node.__init__(self,name)

class CINode(Node):
    fanin = 0
    def __init__(self,name):
        Node.__init__(self,name)

class CONode(Node):
    fanin = 1
    def __init__(self,name):
        Node.__init__(self,name)

class PINode(Node):
    fanin = 0
    def __init__(self,name):
        Node.__init__(self,name)