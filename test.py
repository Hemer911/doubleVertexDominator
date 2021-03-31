import aiger
from node import Node
from edge import Edge
from graph import Graph
import pickle
from buildStaticDb import BuildStaticDb
from dominatorChain import DominatorChain

def validateDominatorsTuples(domTupList,graphPklFileName,inpName): 
    retVal = True
    for domTup in domTupList:
        with open(graphPklFileName,'rb') as fh:
            g = pickle.load(fh)
        src = g.getNode(inpName)
        outName = list(g.outputs)[0]
        dst  = g.getNode(outName)
        dstFanin  = g.fanin(dst)
        while len(dstFanin) == 1:
            dst = dstFanin[0]
            dstFanin = g.fanin(dst)        
        v1Name = domTup[0]
        v2Name = domTup[1]
        bfs = g.bfs(src,dst)
        if not bfs:
                print('amirros debug: ERROR :no valid path from source to target before removing any node = {}'.format(domTup))
                retVal = False
        print('amirros debug: removing {}'.format(domTup))
        g.removeNode(v1Name)
        g.removeNode(v2Name)
        bfs = g.bfs(src,dst)
        if bfs:
            retVal = False
            print('amirros debug: found path from source to target hence {} and {} are not dominators'.format(v1Name,v2Name))
        return retVal


def test(dirName,fileName):
    fileDb = {}
    aigFileName  = dirName + '/' + fileName + '.aig'
    dataBaseDir  = dirName + '/' + fileName
    aagFileName  = dataBaseDir + '/' + fileName + '.aag'
    aagPklFileName  = dataBaseDir + '/' + fileName + '.pkl'
    graphPklFileName = dataBaseDir + '/' + 'g_' + fileName + '.pkl'    

    # gen graph from aig
    BuildStaticDb.handleFile(dirName,fileName)
    
    # load pkl
    with open(graphPklFileName,'rb') as fh:
        g = pickle.load(fh)

    # find target node
    outName = list(g.outputs)[0]
    dst  = g.getNode(outName)
    dstFanin  = g.fanin(dst)
    while len(dstFanin) == 1:
        dst = dstFanin[0]
        dstFanin = g.fanin(dst)
   
    # find DC for each
    # TODO --------        
    # inpName = "Input_944a1b84-8a28-11eb-a500-60f81daa4180"
    
    # DC  =  DominatorChain(g,dst,src)
    # TODO --------
    
       
    for inpName in g.inputs:
        src = g.getNode(inpName)
        print('fanout {} = {}'.format(src.getName(),len(g.fanout(src))))
        DC  =  DominatorChain(g,dst,src)
        fileDb[inpName] = {}
        fileDb[inpName]['L'] = DC.getL()
        fileDb[inpName]['R'] = DC.getR()
        fileDb[inpName]['maxFlow'] = DC.maxFlow
    print('printing vectors:')
    for inpName in fileDb:
        if fileDb[inpName]['maxFlow'] and fileDb[inpName]['L'] and fileDb[inpName]['R']:
            print("{} to {}:".format(inpName,outName))
            print("maxFlow = {}".format(fileDb[inpName]['maxFlow']))
            print("L = {}".format(fileDb[inpName]['L']))
            print("R = {}".format(fileDb[inpName]['R']))
        
    

if __name__ == "__main__":

    
    dirName  = 'hwmcc20/aig/2019/wolf/2019C'
    # fileName = "vgasim_imgfifo-p110"
    fileName = "qspiflash_dualflexpress_divfive-p074"
    # fileName = "vgasim_imgfifo-p036"
    test(dirName,fileName)
    
 
