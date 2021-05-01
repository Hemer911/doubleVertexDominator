import aiger
from util import Util
from subprocess import call
from buildStaticDb import BuildStaticDb
from graphSplitter import GraphSplitter
from node import Node
from edge import Edge
from graph import Graph
from cex import Cex
"""
DominatorsAndSATSolver
----------------------------
DominatorsAndSATSolver is a static class that implement an algorithm for proving AIG models.
It leverages the power of double vertex dominators to split an AIG graph to 2 cuts and proves the correctness of the model in two steps one for each cut.
The main function is proveProperty.
"""
class DominatorsAndSATSolver:

    @staticmethod
    # proveProperty tries to find a counter example in G by splitting it into 2 graphs using a double vertex dominators tuple.
    # @param: G - An AIG
    # @param: domTup - A tuple of two names of proven double vertex dominators.
    # @param: iterationsBound - maximal number of tries to split and prove.
    # @param: framesBound - maximal number of frames per BMC proof.
    # @changes: G - The split process may change G.
    # @returns: "PASS": in case that the model proved to be correct or that framesBound have been reached in one of the iterations.
    #           counter example: in case that a counter example found.
    #           False: tried iterationsBound iterations without finding counter example and without reaching to framesBound in any iteration.
    def proveProperty(G,domTup,iterationsBound,framesBound):
        (bigCutG,smallCutG) = GraphSplitter.splitGraph(G,domTup)
        intersectInputs = bigCutG.inputs.intersection(smallCutG.inputs)
        for iterNum in range(iterationsBound):
            # TODO - send copy of small cut 
            retVal = DominatorsAndSATSolver.proveIteration(bigCutG,smallCutG,domTup,intersectInputs,framesBound,iterNum)
            if retVal: return retVal
        return False    

    @staticmethod    
    def proveIteration(bigCutG,smallCutG,domTup,intersectInputs,framesBound,iterNum):
        cexBigCut = DominatorsAndSATSolver.findCex(bigCutG,'bigCutG',framesBound)
        if not cexBigCut: return "PASS"
        DominatorsAndSATSolver.augmentConstInputs(smallCutG,intersectInputs,cexBigCut,iterNum)
        DominatorsAndSATSolver.augmentProperty(smallCutG,domTup,cexBigCut,iterNum)
        cexSmallCut = DominatorsAndSATSolver.findCex(smallCutG,'smallCutG',framesBound)
        if cexSmallCut:
            return DominatorsAndSATSolver.concatCex(cexBigCut,cexSmallCut,domTup)
        DominatorsAndSATSolver.augmentAssumption(bigCutG,domTup,cexBigCut,iterNum)
        return False  

    @staticmethod
    def findCex(cutG,fileName,framesBound):
        abcPath = Util.abcPath
        outDirPath  = '.'
        cutGAagPath = outDirPath + '/' + fileName + '.aag'
        cutG.write(cutGAagPath)
        BuildStaticDb.convertAagToAig(outDirPath,fileName)
        cutGAigPath = outDirPath + '/' + fileName + '.aig'
        cmd = ['{}/./abc'.format(abcPath),'-c', "read {}; bmc3 -v -F {}".format(cutGAigPath,framesBound)]  
        print('executing cmd: ',cmd)
        call(cmd)
        # TODO - create and parse log
        return False

    @staticmethod
    def augmentConstInputs(cutG,inputsList,cex,iterNum):
        for inputName in inputsList:
            uniqNameStr = 'const_input_chain_{}_{}'.format(inputName,iterNum)
            inputValues = cex.getVal(inputName)
            inputChain  = DominatorsAndSATSolver.getInputChain(inputValues,uniqNameStr)
            DominatorsAndSATSolver.connectConstInput(cutG,inputName,inputChain)
    
    @staticmethod
    def augmentProperty(cutG,domTup,cex,iterNum):
        uniqNameStr = 'property_chain_{}_{}'.format(domTup,iterNum)
        propertyValues = DominatorsAndSATSolver.getPropertyValues(domTup,cex)
        propertyChain  = DominatorsAndSATSolver.getPropertyChain(propertyValues,uniqNameStr)
        DominatorsAndSATSolver.connectProperty(cutG,domTup,propertyChain)
    
    @staticmethod
    def augmentAssumption(cutG,domTup,cex,iterNum):
        for domName in domTup:
            uniqNameStr = 'assumption_chain_{}_{}'.format(domName,iterNum)
            domValues      = cex.getVal(domName)
            assumptionChain  = DominatorsAndSATSolver.getInputChain(domValues,uniqNameStr)
            DominatorsAndSATSolver.connectAssumption(cutG,domName,uniqNameStr,assumptionChain)

    @staticmethod
    def concatCex(cexBigCut,cexSmallCut,domTup):
        namesList = []
        values    = []
        for name in cexBigCut.getNames():
            if name in domTup: continue
            namesList.append(name)
            values.append(cexBigCut.getVal(name))
        for name in cexSmallCut.getNames():
            if name in namesList: continue
            namesList.append(name)
            values.append(cexSmallCut.getVal(name))                  
        return Cex(namesList,values)

    @staticmethod
    def getInputChain(inputValues,uniqNameStr):
        inputChain = Graph()
        outNode = Node('{}_out'.format(uniqNameStr))
        inputChain.addNode(outNode)
        lastNode = outNode
        for idx,val in enumerate(inputValues):
            nameSuffix = '{}_t{}'.format(uniqNameStr,idx) 
            if val == 1:
                newNode = Node('Inverter_{}'.format(nameSuffix))
                inputChain.addNode(newNode)
                inputChain.addEdge(Edge(newNode,lastNode))
                lastNode = newNode
            elif val != 0:
                print('ERROR: buildInputChain - unkown value = {}. should be 0 or 1.'.format(val))
                exit()
            if idx == len(inputValues)-1: continue
            newNode = Node('LatchIn_{}'.format(nameSuffix))
            inputChain.addNode(newNode)
            inputChain.addEdge(Edge(newNode,lastNode))
            lastNode = newNode
        inpNode = Node('chainInp_{}'.format(nameSuffix))
        inputChain.addNode(inpNode)
        inputChain.addEdge(Edge(inpNode,lastNode))
        inputChain.defineOutput(outNode)
        inputChain.defineInput(inpNode)
        return inputChain
      
    @staticmethod
    def getPropertyValues(domTup,cex):
        l = []
        for domName in domTup:
            l.append(cex.getVal(domName))
        retList = [(x,y) for x,y in zip(l[0],l[1])]
        return retList
    
    @staticmethod
    def tupleToGraph(domVal,uniqNameStr):
        if len(domVal) != 2:
            print('ERROR: tupleToGraph unknown input: domVal = {}'.format(domVal))
            exit()
        retGraph = Graph()
        dom1Name = 'inp1'
        dom2Name = 'inp2'
        uniqNameStr = uniqNameStr + '_comb'
        
        # all 4 options ends with out node and andGate:
        outNode = Node("{}_out".format(uniqNameStr))        
        retGraph.addNode(outNode)
        retGraph.defineOutput(outNode)        
        andNode = Node("AndGate_{}".format(uniqNameStr))
        retGraph.addNode(andNode)        
        retGraph.addEdge(Edge(andNode,outNode))
        
        # define two inputs        
        in1Node = Node("{}_{}".format(uniqNameStr,dom1Name))
        in2Node = Node("{}_{}".format(uniqNameStr,dom2Name))
        retGraph.addNode(in1Node)
        retGraph.addNode(in2Node)
        retGraph.defineInput(in1Node)
        retGraph.defineInput(in2Node)
        
        # decide whether input should drive not gate or not
        inp1Fanout = andNode
        if not domVal[0]:
            not1Node = Node("Inverter_{}_{}".format(uniqNameStr,dom1Name))
            retGraph.addNode(not1Node)
            retGraph.addEdge(Edge(not1Node,andNode))
            inp1Fanout = not1Node                        
        retGraph.addEdge(Edge(in1Node,inp1Fanout))

        inp2Fanout = andNode
        if not domVal[1]:
            not2Node = Node("Inverter_{}_{}".format(uniqNameStr,dom2Name))
            retGraph.addNode(not2Node)
            retGraph.addEdge(Edge(not2Node,andNode))
            inp2Fanout = not2Node
        retGraph.addEdge(Edge(in2Node,inp2Fanout))
        
        return retGraph
    
    @staticmethod
    def getPropertyChain(propertyValues,uniqNameStr):
        propertyChain = Graph()
        outNode = Node("{}_out".format(uniqNameStr))
        in1Node = Node("{}_inp1".format(uniqNameStr))
        in2Node = Node("{}_inp2".format(uniqNameStr))
        propertyChain.addNode(outNode)
        propertyChain.defineOutput(outNode)
        propertyChain.addNode(in1Node)
        propertyChain.addNode(in2Node)
        propertyChain.defineInput(in1Node)
        propertyChain.defineInput(in2Node)
        lastNode = outNode 
        propertyValues.reverse()
        for idx,valuesTup in enumerate(propertyValues):
            uniqStrPerCycle = "{}_t{}".format(uniqNameStr,idx)
            currCycleCombLogic = DominatorsAndSATSolver.tupleToGraph(valuesTup,uniqStrPerCycle)
            combLogicInputs  = list(currCycleCombLogic.inputs)
            combLogicOutName = list(currCycleCombLogic.outputs)[0]
            if idx == len(propertyValues)-1:
                propertyChain.connectGraph(currCycleCombLogic,[(combLogicOutName,lastNode.getName())]) 
            else:
                andNode = Node('AndGate_{}'.format(uniqStrPerCycle))
                propertyChain.addNode(andNode)
                propertyChain.addEdge(Edge(andNode,lastNode))
                propertyChain.connectGraph(currCycleCombLogic,[(combLogicOutName,andNode.getName())])
                latchNode = Node('LatchIn_{}'.format(uniqStrPerCycle))
                propertyChain.addNode(latchNode) 
                propertyChain.addEdge(Edge(latchNode,andNode))
                lastNode = latchNode
            for combLogicInput in combLogicInputs:
                dst = propertyChain.getNode(combLogicInput)
                if "inp1" in combLogicInput:                    
                    propertyChain.addEdge(Edge(in1Node,dst))
                elif "inp2" in combLogicInput:
                    propertyChain.addEdge(Edge(in2Node,dst))
                else:
                    print('ERROR: unknown comblogic input name = {}'.format(combLogicInput))
                    exit()
        propertyValues.reverse()
        return propertyChain

    @staticmethod
    def connectProperty(cutG,domTup,propertyChain):
        propertyChainOutName     = list(propertyChain.outputs)[0]
        propertyChainInputsNames = list(propertyChain.inputs)
        connections = []
        for inpName in propertyChainInputsNames:
            if 'inp1' in inpName:
                connections.append((domTup[0],inpName))
            elif 'inp2' in inpName:
                connections.append((domTup[1],inpName))
            else:
                print('ERROR: unkown input name for property connection: {}'.format(inpName))
                exit()
        cutG.connectGraph(propertyChain,connections)
        out = cutG.getNode(propertyChainOutName)
        cutG.defineOutput(out)

    @staticmethod
    def connectConstInput(cutG,inputName,inputChain):
        inputChainInpName = list(inputChain.inputs)[0]
        inputChainOutName = list(inputChain.outputs)[0]       
        constNode = Node('ConstFalse_{}'.format(inputName))              
        cutG.addNode(constNode)
        conn1 = (constNode.getName(),inputChainInpName)
        conn2 = (inputChainOutName,inputName)
        connections = [conn1,conn2]
        cutG.connectGraph(inputChain,connections)
        cutG.undefineInput(inputName)
        
    @staticmethod
    def connectAssumption(cutG,domName,uniqNameStr,assumptionChain):
        outNodeName = list(cutG.outputs)[0]
        outNode     = cutG.getNode(outNodeName)
        andNode = Node('AndGate_{}'.format(uniqNameStr))
        notGate = Node('Inverter_cex_{}'.format(uniqNameStr))
        newOutNode = Node('New_out_{}'.format(uniqNameStr))
        cutG.addNode(andNode)
        cutG.addNode(notGate)
        cutG.addNode(newOutNode)
        cutG.addEdge(Edge(outNode,andNode))
        cutG.addEdge(Edge(notGate,andNode))
        cutG.addEdge(Edge(andNode,newOutNode))
        cutG.undefineOutput(outNodeName)
        cutG.defineOutput(newOutNode.getName())       
        assumptionOutNodeName = list(assumptionChain.outputs)[0]
        assumptionInpNodeName = list(assumptionChain.inputs)[0]
        conn1 = (assumptionOutNodeName,notGate.getName())        
        conn2 = (domName,assumptionInpNodeName)
        connections = [conn1,conn2]
        cutG.connectGraph(assumptionChain,connections)
                
if __name__ == "__main__":
    # g = DominatorsAndSATSolver.getInputChain([0,0,0],'inpChainTest')
    propertyVaules = [(1,1),(0,0),(1,0)]
    g = DominatorsAndSATSolver.getPropertyChain(propertyVaules,'a')
    g.printGraph()