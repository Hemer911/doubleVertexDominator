import pickle
from buildStaticDb import BuildStaticDb
from dominatorChain import DominatorChain
from wolfDb import wolfDb
from validDominatorsDb import validDominatorsDb
import os

def loadGraphAndFindOutput(graphPklFileName,inpName=False):
    with open(graphPklFileName,'rb') as fh:
        g = pickle.load(fh)
    outName = list(g.outputs)[0]
    dst  = g.getNode(outName)
    dstFanin  = g.fanin(dst)
    while len(dstFanin) == 1:
        dst = dstFanin[0]
        dstFanin = g.fanin(dst)
    src = False
    if inpName:
        src = g.getNode(inpName)
    return (g,dst,src)
 
def validateDominatorsTuples(domTupList,graphPklFileName,inpName): 
    print('validateDominatorsTuples: validating {} of {}: {}'.format(inpName,graphPklFileName,domTupList))
    retVal = True
    for domTup in domTupList:
        v1Name = domTup[0]
        v2Name = domTup[1]
        # 1. load graph and validate that it have a valid path from source to destination
        (g1,dst1,src1) = loadGraphAndFindOutput(graphPklFileName,inpName)
        bfsRes1 = g1.bfs(src1,dst1)
        if not bfsRes1:
                print('ERROR :no valid path from source to target before removing any node = {}'.format(domTup))
                retVal = False
                continue
        # 2. remove only one node and validate that the graph still have a valid path
        print('removing one node {}'.format(v1Name))
        g1.removeNode(v1Name)
        bfsRes2 = g1.bfs(src1,dst1)
        if not bfsRes2:
                print('ERROR :no valid path from source to target after removing only one node (first) = {}'.format(v1Name))
                retVal = False
                continue
        # 3. reload the graph and remove the second node (only). validate a path from source to destination     
        (g2,dst2,src2) = loadGraphAndFindOutput(graphPklFileName,inpName)
        print('removing one node {}'.format(v2Name))
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
            print('amirros debug: found path from source to target hence {} and {} are not dominators'.format(v1Name,v2Name))
            retVal = False
            continue
    return retVal


def testFile(dirName,fileName):
    aigFileName  = dirName + '/' + fileName + '.aig'
    dataBaseDir  = dirName + '/' + fileName
    aagFileName  = dataBaseDir + '/' + fileName + '.aag'
    aagPklFileName    = dataBaseDir + '/' + fileName + '.pkl'
    graphPklFileName  = dataBaseDir + '/' + 'g_' + fileName + '.pkl'
    fileDbPklFileName = dataBaseDir + '/' + 'db_' + fileName + '.pkl'
    if os.path.isfile(fileDbPklFileName):
        print('{} exists.'.format(fileDbPklFileName))
        return
    fileDb = {}
    fileDb['dirName']          = dirName
    fileDb['fileName']         = fileName
    fileDb['aigFileName']      = aigFileName
    fileDb['dataBaseDir']      = dataBaseDir
    fileDb['aagFileName']      = aagFileName
    fileDb['aagPklFileName']   = aagPklFileName
    fileDb['graphPklFileName'] = graphPklFileName
    
    # gen graph from aig
    print('testFile -> BuildStaticDb.handleFile({},{})'.format(dirName,fileName))
    BuildStaticDb.handleFile(dirName,fileName)
    
    # load pkl
    print('testFile -> load pkl graph')
    with open(graphPklFileName,'rb') as fh:
        g = pickle.load(fh)

    # find target node
    print('testFile -> find proper target')
    outName = list(g.outputs)[0]
    dst  = g.getNode(outName)
    dstFanin  = g.fanin(dst)
    while len(dstFanin) == 1:
        dst = dstFanin[0]
        dstFanin = g.fanin(dst)
    
    fileDb['outputName'] = dst.getName()
    fileDb['inputs'] = {}

    print('testFile -> for each input find dominators')          
    for inpName in g.inputs:
        src = g.getNode(inpName)
        DC  =  DominatorChain(g,dst,src)
        fileDb['inputs'][inpName] = {}
        fileDb['inputs'][inpName]['L'] = DC.getL()
        fileDb['inputs'][inpName]['R'] = DC.getR()
        fileDb['inputs'][inpName]['maxFlow'] = DC.maxFlow

    print('testFile -> export dominators db to pkl')          
    with open(fileDbPklFileName,'wb') as fh:
        pickle.dump(fileDb,fh)

def findAllDominatorsForDb(db,maxSize):        
    for tup in db:
        graphSize = tup[0]
        filePath  = tup[1]
        if graphSize > maxSize: 
            continue
        splitedPath = filePath.split('/')
        fileName = splitedPath.pop()
        dirName = "/".join(splitedPath)
        testFile(dirName,fileName)

def loadAndValidateDb(dirName,fileName):
    fileDbPklFileName = getDbPklFileName(dirName,fileName)
    # 1. load db
    with open(fileDbPklFileName,'rb') as fh:
        db = pickle.load(fh)
    # 2. load graph
    graphPklFileName = db['graphPklFileName']    
    # 3. for each input:
    for inputName,inputDict in db['inputs'].items():
        if inputDict['maxFlow'] != 2: continue
        # 3.1 build dominators tuples list
        tupList = getDomTupList(inputDict)
        # 3.2  validate tuples
        if not validateDominatorsTuples(tupList,graphPklFileName,inputName):
            print('ERROR: tupList of {} for input {} is not valid. tupLsit = {}'.format(graphPklFileName,inputName,tupList))
            return        

def getDbPklFileName(dirName,fileName):
    dataBaseDir  = dirName + '/' + fileName
    fileDbPklFileName = dataBaseDir + '/' + 'db_' + fileName + '.pkl'
    return fileDbPklFileName

def buildBfsTree(dirName,fileName,direction='fanin'):
    fileDbPklFileName = getDbPklFileName(dirName,fileName)
    # 1. load db
    with open(fileDbPklFileName,'rb') as fh:
        db = pickle.load(fh)
    # 2. load graph
    graphPklFileName = db['graphPklFileName']    
    (g,dst,_src) = loadGraphAndFindOutput(graphPklFileName)
    bfsTree = g.bfsTree(dst,direction)
    return bfsTree
       
def getDomTupList(inputDict):
    L = inputDict['L']
    R = inputDict['R']
    tupList = []
    for lTup in L:
        lName  = lTup[0]
        _lRef  = lTup[1]
        minIdx = lTup[2]
        maxIdx = lTup[3]
        for idx in range(minIdx,maxIdx+1):
            rTup = R[idx]
            rName = rTup[0]
            tupList.append((lName,rName))
    return tupList



if __name__ == "__main__":
    fileName  = 'qspiflash_qflexpress_divfive-p094'
    dirName = 'hwmcc20/aig/2019/wolf/2019C'
    # testFile(dirName,fileName)
    # for (dirName,fileName) in validDominatorsDb:
    #     loadAndValidateDb(dirName,fileName)
    # findAllDominatorsForDb(wolfDb,10000)
    bfsTree = buildBfsTree(dirName,fileName,'fanin')
    
    
