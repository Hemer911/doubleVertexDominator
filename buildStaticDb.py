import aiger
from util import Util
from node import Node
from edge import Edge
from graph import Graph
import pickle
import os
from os import listdir
from subprocess import call
from pympler.asizeof import asizeof
from dominatorChain import DominatorChain
import sys
sys.setrecursionlimit(1000)
    
class GlobalVars:
    def __init__(self):
        self.debug = False
        self.visited = {}
        self.nodeIndex = 0
        self.exceptionFiles = {}       

class BuildStaticDb:
    globalVars = GlobalVars() 

    @staticmethod
    def genDirForAigFile(dirName,fileName):
        print('-> genDirForAigFile')
        fullDirPath = BuildStaticDb.getOutputDirPath(dirName, fileName)
        fullFileName = fullDirPath+'.aig'
        if not os.path.isfile(fullFileName):
            print('ERROR: something went wrong, trying to genDirForAigFile but ',fullFileName,' does not exist')
            exit()
        if not os.path.isdir(fullDirPath):
            print('no dir for ',fullDirPath)
            os.mkdir(fullDirPath)

    @staticmethod
    def convertAigToAag(dirName,fileName):
        print('-> convertAigToAag')
        fullDirPath = BuildStaticDb.getOutputDirPath(dirName, fileName)
        fullAigFileName = fullDirPath + '/' + fileName + '_update.aig'
        fullAagFileName = fullDirPath + '/' + fileName + '.aag'
        # if not os.path.isfile(fullAagFileName):
        cmd = ['./aigtoaig',fullAigFileName,fullAagFileName]
        print('executing cmd: ',cmd)
        call(cmd)

    @staticmethod
    def convertAagToAig(dirName,fileName):
        print('-> convertAagToAig')
        fullAigFileName = dirName + '/' + fileName + '.aig'
        fullAagFileName = dirName + '/' + fileName + '.aag'
        # if not os.path.isfile(fullAagFileName):
        cmd = ['./aigtoaig',fullAagFileName,fullAigFileName]
        print('executing cmd: ',cmd)
        call(cmd)
 
    @staticmethod
    def loadAagAndExportToPkl(dirName,fileName):
        print('-> loadAagAndExportToPkl')
        fullDirPath = BuildStaticDb.getOutputDirPath(dirName, fileName)
        fullAagFileName = fullDirPath + '/' + fileName + '.aag'
        fullPklFileName = BuildStaticDb.getAagPklPath(dirName, fileName)
        if not os.path.isfile(fullPklFileName):
            pyaig1 = aiger.load(fullAagFileName)
            #print(asizeof(pyaig1))
            with open(fullPklFileName,'wb') as fh:
                pickle.dump(pyaig1,fh)

    @staticmethod
    def buildGraph(aig1,outName):
        print('-> buildGraph')
        g = Graph()
        dst = Node(outName)
        g.addNode(dst)
        g.defineOutput(dst)
        root = aig1.node_map[outName]
        BuildStaticDb.recTravel(g,aig1,root,dst)
        return g
    
    @staticmethod
    def amirrosDebug(msg):
        if BuildStaticDb.globalVars.debug:
            print('amirros debug: ',msg)
    
    @staticmethod
    def addNode(g,aigNodeRef,nodeName,dstNode):
            newNode = Node(nodeName)
            BuildStaticDb.globalVars.visited[aigNodeRef] = newNode
            e = Edge(newNode,dstNode)
            g.addNode(newNode)
            g.addEdge(e)
            return newNode
    
    @staticmethod
    def recTravel(g,aig1,aigNodeRef,dstNode):
        if aigNodeRef in BuildStaticDb.globalVars.visited:
            e = Edge(BuildStaticDb.globalVars.visited[aigNodeRef],dstNode)
            g.addEdge(e)
            return        
        if type(aigNodeRef) == type(aiger.aig.Input('')):
            BuildStaticDb.amirrosDebug('recTravel: Input')
            nodeName = 'Input_{}'.format(aigNodeRef.name)
            newNode = BuildStaticDb.addNode(g,aigNodeRef,nodeName,dstNode)
            g.defineInput(newNode)
            return      
        elif type(aigNodeRef) == type(aiger.aig.ConstFalse()):
            BuildStaticDb.amirrosDebug('recTravel: ConstFalse')
            nodeName = 'ConstFalse_{}'.format(BuildStaticDb.globalVars.nodeIndex)
            BuildStaticDb.globalVars.nodeIndex+=1
            newNode = BuildStaticDb.addNode(g,aigNodeRef,nodeName,dstNode)
            return
        elif type(aigNodeRef) == type(aiger.aig.LatchIn('')):
            BuildStaticDb.amirrosDebug('recTravel: LatchIn')
            nodeName = 'LatchIn_{}'.format(aigNodeRef.name)
            newNode = BuildStaticDb.addNode(g, aigNodeRef, nodeName,dstNode)
            BuildStaticDb.recTravel(g,aig1,aig1.latch_map[aigNodeRef.name],newNode)
            return
        elif type(aigNodeRef) == type(aiger.aig.Inverter('')):
            BuildStaticDb.amirrosDebug('recTravel: Inverter, nodeIndex = {}'.format(BuildStaticDb.globalVars.nodeIndex))
            nodeName = "Inverter_{}".format(BuildStaticDb.globalVars.nodeIndex)
            BuildStaticDb.globalVars.nodeIndex+=1
            newNode = BuildStaticDb.addNode(g,aigNodeRef,nodeName,dstNode)
            for child in aigNodeRef.children:
                BuildStaticDb.recTravel(g,aig1,child,newNode)
            return
        elif type(aigNodeRef) == type(aiger.aig.AndGate(None,None)):
            BuildStaticDb.amirrosDebug('recTravel: AndGate')
            nodeName = "AndGate_{}".format(BuildStaticDb.globalVars.nodeIndex)
            BuildStaticDb.globalVars.nodeIndex+=1
            newNode = BuildStaticDb.addNode(g,aigNodeRef,nodeName,dstNode)
            for child in aigNodeRef.children:
                BuildStaticDb.recTravel(g,aig1,child,newNode)
            return
        else:
            print('ERROR: unknown type: ',aigNodeRef)
            exit()
    
    @staticmethod
    def loadPklGenGraphPerOutputAndExportToPkl(dirName,fileName):
        print('-> loadPklGenGraphPerOutputAndExportToPkl')
        fullPklFileName = BuildStaticDb.getAagPklPath(dirName,fileName)
        if not os.path.isfile(fullPklFileName):
            print('ERROR: no pkl file: ',fullPklFileName)
            exit()
        with open(fullPklFileName,'rb') as fh:
            pyaig1 = pickle.load(fh)
        for outName in pyaig1.outputs:
            fullPklGraphFileName = BuildStaticDb.getGraphPklPath(dirName, fileName)
            if not os.path.isfile(fullPklGraphFileName):
                g = BuildStaticDb.buildGraph(pyaig1,outName)
                with open(fullPklGraphFileName,'wb') as fh:
                    pickle.dump(g,fh)
            break
               
    @staticmethod
    def convertNewAigFormatToLegacy(dirName,fileName):
        abcPath = Util.abcPath
        inputFilePath  =  dirName + '/' + fileName + '.aig'
        outputFilePath =  BuildStaticDb.getOutputDirPath(dirName, fileName) + '/' + fileName + '_update.aig'
        if not os.path.isfile(outputFilePath):
            cmd = ['{}/./abc'.format(abcPath),'-c', "read {}; zero; fold; write_aiger {}".format(inputFilePath,outputFilePath)]  
            print('executing cmd: ',cmd)
            call(cmd)


    @staticmethod
    def getOutputDirPath(dirName,fileName):
        return "{}/{}".format(dirName,fileName)
    
    @staticmethod
    def getAagPklPath(dirName,fileName):
        outputDirPath = BuildStaticDb.getOutputDirPath(dirName,fileName)
        return "{}/{}.pkl".format(outputDirPath,fileName)
            
    @staticmethod
    def getGraphPklPath(dirName,fileName):
        outputDirPath = BuildStaticDb.getOutputDirPath(dirName, fileName)
        return "{}/g_{}.pkl".format(outputDirPath,fileName) 
    
    @staticmethod
    def loadGraph(dirName,fileName):
        graphPklPath = BuildStaticDb.getGraphPklPath(dirName, fileName)
        with open(graphPklPath,'rb') as fh:
            g = pickle.load(fh)
        return g        

    @staticmethod
    def handleFile(dirName,fileName):
        try:
            BuildStaticDb.genDirForAigFile(dirName,fileName)
            BuildStaticDb.convertNewAigFormatToLegacy(dirName,fileName)
            BuildStaticDb.convertAigToAag(dirName,fileName)
            BuildStaticDb.loadAagAndExportToPkl(dirName,fileName)
            BuildStaticDb.loadPklGenGraphPerOutputAndExportToPkl(dirName,fileName)
        except:
            print('ERROR: {} failed. adding it to the exception list'.format(fileName))
            BuildStaticDb.globalVars.exceptionFiles[fileName] = True
    
    @staticmethod
    def handleDir(dirName):
        for fileFullName in listdir(dirName):
            fileName, fileExtension = os.path.splitext(fileFullName)
            if os.path.isdir(dirName+'/'+fileFullName):
                print('call handleDir for ',dirName + '/' + fileFullName)
                BuildStaticDb.handleDir(dirName + '/' + fileFullName)
            elif fileExtension == '.aig' and '_update.aig' not in fileFullName:
                print('call handleFile for ',dirName + ',' + fileName)
                if fileName in BuildStaticDb.globalVars.exceptionFiles: continue
                BuildStaticDb.handleFile(dirName,fileName)
            else:
                print('ignoring: {}/{}. fileExtension = {}'.format(dirName,fileFullName,fileExtension))
                       
if __name__ == "__main__":
    print('-> starting')
    rootDir = 'hwmcc20/aig/2019/wolf/2018D'
    dirName      = 'hwmcc20/aig/2019/wolf/2019C'
    fileName     = "vgasim_imgfifo-p110"    
    # BuildStaticDb.handleDir(rootDir)
    #BuildStaticDb.handleFile(rootDir,'VexRiscv-regch0-30-p1')
    print(BuildStaticDb.globalVars.exceptionFiles)