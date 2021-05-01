class Cex:
    def __init__(self,orderedInputNamesList,values):
        self.inpValMap = {}
        for inpName,val in (orderedInputNamesList,values):
            self.inpValMap[inpName] = val

    def getNames(self):
        return list(self.inpValMap.keys())
 
    def getVal(self,name):
        return self.inpValMap[name]