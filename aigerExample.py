import aiger
from node import Node
from edge import Edge
from graph import Graph
import pickle

def recTravel(aig1,root,dst,latchList = []):
    if root in visited: return
    visited.append(root)
    print('amirros debug: nodeIndex[0] = ',nodeIndex[0])
    if type(root) == type(aiger.aig.Input('')):
        print('amirros debug: found input')
        inp = g.getNode(root.name)
        if inp:       
            e = Edge(inp,dst)
        else:
            newNode = Node(root.name)
            e = Edge(newNode,dst)
            g.addNode(newNode)
        g.addEdge(e)
        return      
    elif type(root) == type(aiger.aig.ConstFalse()):
        print('amirros debug: found const false')
        newNode = Node("{}".format(nodeIndex[0]))
        e = Edge(newNode,dst)
        g.addNode(newNode)
        g.addEdge(e)       
        nodeIndex[0]+=1
        return
    elif type(root) == type(aiger.aig.LatchIn('')):
        print('amirros debug: found LatchIn')
        if root.name not in latchList:
            print('amirros debug: new LatchIn')
            latchList.append(root.name)
            newNode = Node(root.name)
            e = Edge(newNode,dst)
            g.addNode(newNode)
            g.addEdge(e)
            print('amirros debug: latch add to graph. calling recursivly')
            recTravel(aig1, aig1.latch_map[root.name],newNode,latchList)
        return
    elif type(root) == type(aiger.aig.Inverter('')):
        print('amirros debug: found Inverter')
        newNode = Node("{}".format(nodeIndex[0]))
        nodeIndex[0]+=1
        g.addNode(newNode)
        e = Edge(newNode,dst)
        g.addEdge(e)
        for child in root.children:
            recTravel(aig1, child,newNode,latchList)
        return
    elif type(root) == type(aiger.aig.AndGate(None,None)):
        print('amirros debug: found AndGate')
        newNode = Node("{}".format(nodeIndex[0]))
        nodeIndex[0]+=1
        g.addNode(newNode)
        e = Edge(newNode,dst)
        g.addEdge(e)
        for child in root.children:
            recTravel(aig1, child,newNode,latchList)
        return
    else:
        print('ERROR: unknown type: ',root)
        exit()


# create aag out of 
#fileName = "hwmcc20/aig/2019/beem/anderson.3.prop1-back-serstep.aag" # 3K nodes
#fileName = "hwmcc20/aig/2019/beem/at.6.prop1-back-serstep.aag"      # 3K nodes
fileName = "hwmcc20/aig/2019/beem/rushhour.4.prop1-func-interl.aag" # 58K nodes
#fileName = "i10.aag" # 3K nodes

print('--> loading aig')
#aig1 = aiger.load(fileName)
with open('aig1.pkl','rb') as fh:
    aig1 = pickle.load(fh)
print('--> building graph from aig')
for outName in aig1.outputs:
    print('--> start for output = {}:'.format(outName))
    nodeIndex = [0]
    g = Graph()
    dst = Node(outName)
    dst.setRoot()
    g.addNode(dst)
    root = aig1.node_map[outName]
    visited = []
    recTravel(aig1,root,dst)
    print('--> calculating max flow for each source and target')
    for inpName in aig1.inputs:
        print('amirros debug: working on input:',inpName)
        source = g.getNode(inpName)
        if not source: continue
        maxFlow = g.edmonds_karp(source, dst)
        if maxFlow != 1:
            print('for root = {} and source = {} the max flow is = {}'.format(dst.getName(),source.getName(),maxFlow))