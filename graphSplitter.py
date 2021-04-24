from graph import Graph
from node import Node
from edge import Edge
import re
import aiger
class GraphSplitter:
    
    @staticmethod
    def splitGraph(g,domTup):
        v1Name = domTup[0]
        v2Name = domTup[1]
        v1 = g.getNode(v1Name)
        v2 = g.getNode(v2Name)
        outName = list(g.outputs)[0]
        out     = g.getNode(outName)
        GraphSplitter.replaceNodeWithNewInp(g,v1)
        GraphSplitter.replaceNodeWithNewInp(g,v2)
        gCut  = GraphSplitter.cutGraph(g,[v1,v2])
        gRest = GraphSplitter.cutGraph(g,[out])
        gRestOut = gRest.getNode(outName)
        gRest.defineOutput(gRestOut)
        aig1  = GraphSplitter.graphToAig(gRest)      
        return (aig1,gCut)
        
    @staticmethod
    def cutGraph(g,outputsList):
        cutG = Graph() 
        inputs = g.inputs
        for out in outputsList:
            transFanin = g.transFanin(out)
            # add all nodes       
            for node in transFanin:
                nodeName = node.getName()
                if not cutG.getNode(nodeName):
                    newNode = Node(nodeName)
                    cutG.addNode(newNode)
                    if nodeName in inputs:
                        cutG.defineInput(newNode)                    
        # add all edges
        for newDst in cutG.getNodes():
                newDstName = newDst.getName()
                dst = g.getNode(newDstName)
                fanin = g.fanin(dst)
                for src in fanin:
                    newSrc = cutG.getNode(src.getName())                    
                    e = Edge(newSrc,newDst)
                    cutG.addEdge(e)                       
        return cutG
      
    @staticmethod
    def graphToAig(g):
        latches = g.getLatches()
        outName = list(g.outputs)[0]
        out     = g.getNode(outName)
        combExpr = GraphSplitter.getCombExpr(g,out)
        combExpr = combExpr.with_output(out.getName())
        fullAig  = combExpr.aig
        for latchName,latchNode in latches.items():
            print('amirros debug: latchName = {}'.format(latchName))
            faninNode = g.fanin(latchNode)[0] 
            combExpr = GraphSplitter.getCombExpr(g,faninNode)
            combExpr = combExpr.with_output(latchName+'_CO')
            fullAig = fullAig | combExpr.aig
        for latchName in latches:
            fullAig = fullAig.feedback([latchName + '_CI'],[latchName + '_CO'])
        return fullAig 
        
    @staticmethod
    def getCombExpr(g,node):
        nodeName = node.getName()
        print('amirros debug: getCombExpr - nodeName = {}'.format(nodeName))
        if re.search("^Input_",nodeName):
            atomName = nodeName.replace("Input_","")
            return aiger.atom(atomName)
        elif re.search("^ConstFalse_",nodeName):            
            retVal = aiger.atom(nodeName) & False
            print('amirros debug: retVal = ',retVal)
            return retVal
        elif re.search("^LatchIn_",nodeName):
            atomName = nodeName + "_CI"
            return aiger.atom(atomName)
        elif re.search("^Inverter_",nodeName):
            invFanIn = g.fanin(node)
            child = invFanIn[0]
            return ~GraphSplitter.getCombExpr(g,child)
        elif re.search("^AndGate_",nodeName):
            andFanIn = g.fanin(node)
            a = andFanIn[0]
            b = andFanIn[1]
            return GraphSplitter.getCombExpr(g,a) & GraphSplitter.getCombExpr(g,b)
        else:
            fanin = g.fanin(node)
            if len(fanin) != 1:
                print('ERROR: unknown node type. nodeName = {} with unknown fanin len = {}'.format(nodeName,len(fanin)))
                exit()
            child = fanin[0]
            return GraphSplitter.getCombExpr(g,child)
        
    @staticmethod
    def replaceNodeWithNewInp(g,v):
        fanout = g.fanout(v)
        newInp  = Node('Input_new_{}'.format(v.getName()))
        g.addNode(newInp)
        g.defineInput(newInp)
        for u in fanout:
            eToRem = Edge(v,u)            
            g.removeEdge(eToRem)
            eToAdd = Edge(newInp,u)
            g.addEdge(eToAdd)