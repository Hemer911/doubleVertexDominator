from buildStaticDb import BuildStaticDb
from dominatorChain import DominatorChain
import pickle
from graphSplitter import GraphSplitter
class DominatorsDb:
     
    def __init__(self,dirName,fileName,validate=True,loadPkl=False):
        self.dirName = dirName
        self.fileName = fileName
        if loadPkl:
            db = self.loadPklDb()
            self.inputsToDomTupDict = db.inputsToDomTupDict
            self.domTupToInputsDict = db.domTupToInputsDict
            self.domTupHight        = db.domTupHight
            self.domTupConOfInf     = db.domTupConOfInf
            self.g                  = db.g
            self.midHight           = db.midHight
            self.graphHight         = db.graphHight
            self.maxInpNameList     = db.maxInpNameList
            return
        # init values
        self.inputsToDomTupDict = {}
        self.domTupToInputsDict = {}
        self.domTupHight        = {}
        self.domTupConOfInf     = {}
        self.g                  = None
        self.bfsTree            = None
        
        # load graph
        BuildStaticDb.handleFile(dirName,fileName)
        self.g = BuildStaticDb.loadGraph(dirName,fileName)        
        (_,dst) = self.getProperOutput(self.g)
        
        # build double vertex dominators database
        for inpName in self.g.inputs:
            src = self.g.getNode(inpName)
            self.inputsToDomTupDict[inpName] = self.getDomTupList(src,dst)        
            # validate dominators
            if validate:
                if not self.validateDominatorsTuples(inpName):
                    print('ERROR: found illegal double vertex dominators for input {}'.format(inpName))
                    exit()        
        
        # calculate bfs tree (hight for each node)
        self.bfsTree = self.g.bfsTree(dst,'fanin')
        (self.graphHight,self.maxInpNameList) = self.getMaxInpHight()
        self.midHight = self.graphHight / 2    
    
        # for each input:
        for inpName,domTupList in self.inputsToDomTupDict.items():
            for domTup in domTupList:
                if domTup not in self.domTupToInputsDict:
                    self.domTupToInputsDict[domTup] = set()
                self.domTupToInputsDict[domTup].add(inpName)
                self.domTupHight[domTup] = (self.g.getNodeHight(domTup[0]),self.g.getNodeHight(domTup[1]))
                self.domTupConOfInf[domTup] = self.g.getDoubleVertexConOfInf(domTup)               
        # unified similar domTups
        for domTup,inpSet in self.domTupToInputsDict.items():
            revDomTup  = self.getReverseDomTup(domTup)
            if revDomTup in self.domTupToInputsDict:
                self.domTupToInputsDict[domTup] = inpSet.union(self.domTupToInputsDict[revDomTup])                
        self.exportDbToPkl()

        ###########
        interestingDomTups = self.getInterestingDomTups()     
        for domTup,conOfInf in self.domTupConOfInf.items():
            conOfInfPer = len(conOfInf) / self.g.getNodesNum() * 100
            if conOfInfPer < 50:
                print('{} have {}% influence'.format(domTup,conOfInfPer))
        #    print('{} is drived by {} inputs: {}'.format(domTup,len(self.domTupToInputsDict[domTup]),self.domTupToInputsDict[domTup]))
        return 
        print('graph hight = {}, mid = {}'.format(self.graphHight,self.midHight))
        print('interestingDomTups = {}'.format(interestingDomTups))
        # print('print hight for each input:')
        # for inpName in self.inputsToDomTupDict:
        #     print("{} hight = {}".format(inpName,self.g.getNodeHight(inpName)))
        print('print hight for each double vertex dominators:')
        for domTup in self.domTupToInputsDict:
            print("{} hight = {}".format(domTup,(self.g.getNodeHight(domTup[0]),self.g.getNodeHight(domTup[1]))))
        #
        # 
    def getInterestingDomTups(self):
        interestingDomTups = []
        for domTup,hightTup in self.domTupHight.items():
            if hightTup[0] >= 0.9 * self.midHight or hightTup[1] >= 0.9 * self.midHight:
                if hightTup[0]  >= self.midHight/2 and hightTup[1] >= self.midHight/2:
                    interestingDomTups.append(domTup)
        return interestingDomTups    
       
    def getMaxInpHight(self):
        maxH = -1
        maxInpNameList = []
        for inpName in self.inputsToDomTupDict:
            h = self.g.getNodeHight(inpName)
            if h > maxH:
                maxH = h
                maxInpNameList = [inpName]
            if h == maxH:
                maxInpNameList.append(inpName)
        return (maxH,maxInpNameList)     
            
    def loadPklDb(self):
        outDirPath   = BuildStaticDb.getOutputDirPath(self.dirName,self.fileName)
        domDbPklPath = outDirPath + '/' + "domDb.pkl"         
        with open(domDbPklPath,'rb') as fh:
            retObj = pickle.load(fh)
        return retObj

    def exportDbToPkl(self):
        outDirPath   = BuildStaticDb.getOutputDirPath(self.dirName,self.fileName)
        domDbPklPath = outDirPath + '/' + "domDb.pkl"         
        with open(domDbPklPath,'wb') as fh:
            pickle.dump(self,fh)
            
    def validateDominatorsTuples(self,inpName):
        domTupList = self.inputsToDomTupDict[inpName]
        retVal = True
        for domTup in domTupList:
            v1Name = domTup[0]
            v2Name = domTup[1]
            # 1. load graph and validate that it have a valid path from source to destination
            g1 = BuildStaticDb.loadGraph(self.dirName,self.fileName)
            (_,dst1) = self.getProperOutput(g1)
            src1 = g1.getNode(inpName)
            bfsRes1 = g1.bfs(src1,dst1)
            if not bfsRes1:
                    print('ERROR :no valid path from source to target before removing any node = {}'.format(domTup))
                    retVal = False
                    continue
            # 2. remove only one node and validate that the graph still have a valid path
            g1.removeNode(v1Name)
            bfsRes2 = g1.bfs(src1,dst1)
            if not bfsRes2:
                    print('ERROR :no valid path from source to target after removing only one node (first) = {}'.format(v1Name))
                    retVal = False
                    continue
            # 3. reload the graph and remove the second node (only). validate a path from source to destination     
            g2 = BuildStaticDb.loadGraph(self.dirName,self.fileName)
            (_,dst2) = self.getProperOutput(g2)
            src2 = g2.getNode(inpName)
            g2.removeNode(v2Name)
            bfsRes3 = g2.bfs(src2,dst2)
            if not bfsRes3:
                    print('ERROR :no valid path from source to target after removing only one node (second) = {}'.format(v2Name))
                    retVal = False
                    continue
            # 4. remove the other node and validate that no path is available.      
            g2.removeNode(v1Name)
            bfsRes4 = g2.bfs(src2,dst2)
            if bfsRes4:
                print('ERROR: found path from source to target hence {} and {} are not dominators'.format(v1Name,v2Name))
                retVal = False
                continue
        return retVal

    def getDomTupList(self,srcNode,dstNode):
        self.DC = DominatorChain(self.g,dstNode,srcNode)
        self.L  = self.DC.getL()
        self.R  = self.DC.getR()
        tupList = []
        for lTup in self.L:
            lName  = lTup[0]
            _lRef  = lTup[1]
            minIdx = lTup[2]
            maxIdx = lTup[3]
            for idx in range(minIdx,maxIdx+1):
                rTup = self.R[idx]
                rName = rTup[0]
                tupList.append((lName,rName))
        return tupList
        
    def getProperOutput(self,g):
        outName = list(g.outputs)[0]
        dst  = g.getNode(outName)
        dstFanin  = g.fanin(dst)
        while len(dstFanin) == 1:
            dst = dstFanin[0]
            dstFanin = g.fanin(dst)
        return (outName,dst)
    
    def getReverseDomTup(self,domTup):
        return (domTup[1],domTup[0])
    
    def compareDomTup(self,domTupA,domTupB):
        if domTupA[0] == domTupB[0] and domTupA[1] == domTupB[1]: return True
        if domTupA[0] == domTupB[1] and domTupA[1] == domTupB[0]: return True
        return False
    
if __name__ == "__main__":
    fileName  = 'qspiflash_qflexpress_divfive-p094'
    dirName = 'hwmcc20/aig/2019/wolf/2019C'
    validate = False
    loadPkl = True
    domDb = DominatorsDb(dirName,fileName,validate=validate,loadPkl=loadPkl)
    g = domDb.g
    domTup = ('Inverter_39', 'Inverter_699')
    conOfInf = domDb.domTupConOfInf[domTup]
    numG = g.getNodesNum()
    (aig1,cutG) = GraphSplitter.splitGraph(g,domTup)
    # run native
    # run aig1 
    print("cutG = {}, g = {}, cutG/g = {}, len(conOfInf) = {}".format(cutG.getNodesNum(),numG,cutG.getNodesNum()/numG*100, len(conOfInf)))
    