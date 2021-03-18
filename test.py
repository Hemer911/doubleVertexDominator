import aiger
from node import Node
from edge import Edge
from graph import Graph
import pickle
from buildStaticDb import BuildStaticDb
from dominatorChain import DominatorChain

dirName      = 'hwmcc20/aig/2019/wolf/2019C'
fileName     = "vgasim_imgfifo-p110"
aigFileName  = dirName + '/' + fileName + '.aig'
dataBaseDir  = dirName + '/' + fileName
aagFileName  = dataBaseDir + '/' + fileName + '.aag'
aagPklFileName  = dataBaseDir + '/' + fileName + '.pkl'
graphPklFileName = dataBaseDir + '/' + 'g_' + fileName + '.pkl'
if __name__ == "__main__":
    
    with open(graphPklFileName,'rb') as fh:
        g = pickle.load(fh)   
    
    print(len(g.V.keys()))
    
    dst = g.getNode('AndGate_0')
    src = g.getNode('Input_412b896e-8588-11eb-b3ea-60f81daa4180')
    
    DC = DominatorChain(g,dst,src)
    D_uStr = "("
    for tup in DC.D_u:
        firstStr = ""
        for v in tup[0]:
            firstStr += v.getName() + ','
        secStr = ""
        for v in tup[1]:
            secStr += v.getName() + ','  
        D_uStr += "(" + firstStr +" , " + secStr + "),"
    D_uStr += ")"         
    print(DC.D_u)
    print(D_uStr)    
    exit()
    
    print("-> maxFlow for each output")     
    for outName in g.outputs:
        dst  = g.getNode(outName)
        dstFanin  = g.fanin(dst)
        while len(dstFanin) == 1:
            print('amirros debug: {} fanin = 1',dst.getName())
            dst = dstFanin[0]
            dstFanin = g.fanin(dst)            
        
        for inpName in g.inputs:
            # print('amirros debug: working on input:',inpName, " fanout: = ",len(g.E[inpName]))
            source = g.getNode(inpName)
            if not source: continue
            maxFlow = g.edmonds_karp(source, dst)
            if maxFlow != 1:
                print('for root = {} and source = {} the max flow is = {}'.format(dst.getName(),source.getName(),maxFlow))
    
