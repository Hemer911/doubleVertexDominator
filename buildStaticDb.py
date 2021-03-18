import aiger
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
class maxFlowDb:
    def __init__(self):
        self.maxFlowMap = {}
    
    def storeMaxFlow(self,fileName,outName,inpName,maxFlow):
        if not fileName in self.maxFlowMap:
            self.maxFlowMap[fileName] = {}
        if not outName in self.maxFlowMap[fileName]:
            self.maxFlowMap[fileName] = {}
        if inpName in self.maxFlowMap[fileName][outName]:
            print('ERROR: trying to save max flow for {},{},{} but it already exist'.format(fileName,outName,inpName))
            exit()
        self.maxFlowMap[fileName][outName][inpName] = maxFlow
            
        
    
class GlobalVars:
    def __init__(self):
        self.debug = False
        self.visited = {}
        self.nodeIndex = 0
        self.exceptionFiles = {  'beemlifts1b1': True,
                                 'beemcoll2f1': True,
                                 'beemndhm3f1': True,
                                 'beemfwt2b2': True,
                                 'beemrshr4b1': True,
                                 'beemprng2f1': True,
                                 'beemsnpse4f1': True,
                                 'beemlup2b1': True,
                                 'beemfwt2b3': True,
                                 'beemlifts8f1': True,
                                 'beemfwt2b1': True,
                                 'beemsnpse6f1': True,
                                 'beemlifts3b1': True,
                                 'beemmsmie3b1': True,
                                 'beemldelec6b1': True,
                                 'beemfwt4b2': True,
                                 'beemlifts7b1': True,
                                 'beemcoll4f1': True,
                                 'beemlup4b1': True,
                                 'beemfwt4b3': True,
                                 'beemndhm1f4': True,
                                 'beemndhm3f4': True,
                                 'beemfwt4b1': True,
                                 'beemlifts5b1': True,
                                 'beemldelec4b1': True,
                                 'beemprng1f1': True,
                                 'beemsnpse7f1': True,
                                 'beemndhm4f4': True,
                                 'beemfwt3b1': True,
                                 'beemfwt1b3': True,
                                 'beemskbn3b1': True,
                                 'beemfwt1b2': True,
                                 'beemlifts2b1': True,
                                 'beempgmprot8b2': True,
                                 'beemldelec3b1': True,
                                 'beemmsmie4b1': True,
                                 'beemfwt3b2': True,
                                 'beemskbn1b1': True,
                                 'beemlptna5f1': True,
                                 'beemfwt1b1': True,
                                 'beemlup3b1': True,
                                 'beempgmprot8b1': True,
                                 'beemfwt3b3': True,
                                 'beemsnpse5f1': True,
                                 'beemfwt5b1': True,
                                 'beempgmprot8b5': True,
                                 'beemsnpse1f1': True,
                                 'beemndhm2f4': True,
                                 'beemldelec5b1': True,
                                 'beemlifts4b1': True,
                                 'beemlifts6b1': True,
                                 'beemfwt5b2': True,
                                 'beempgmprot8b6': True,
                                 'beemrshr3b1': True,
                                 'beemsnpse3f1': True,
                                 'beemfwt5b3': True,
                                 'beempgmprot2b1': True,
                                 'beemlifts3f1': True,
                                 'beempgmprot6b5': True,
                                 'beempgsol6b1': True,
                                 'beemsnpse6b1': True,
                                 'beempgmprot4b6': True,
                                 'beemplc4b2': True,
                                 'beempgmprot2b2': True,
                                 'beemlptna4b1': True,
                                 'beemlifts8b1': True,
                                 'beempgmprot6b6': True,
                                 'beemsnpse4b1': True,
                                 'beemprng2b1': True,
                                 'beempgmprot4b5': True,
                                 'beempgsol4b1': True,
                                 'beemlifts5f1': True,
                                 'beempgmprot4b1': True,
                                 'beempgmprot6b2': True,
                                 'beemfwt4f1': True,
                                 'beempgmprot2b6': True,
                                 'beemexit5b1': True,
                                 'beemrether4b1': True,
                                 'beemrether6b1': True,
                                 'beemsnpse2b1': True,
                                 'beemfwt4f3': True,
                                 'beemplc2b2': True,
                                 'beempgmprot4b2': True,
                                 'beemlifts7f1': True,
                                 'beempgmprot6b1': True,
                                 'beemfwt4f2': True,
                                 'beempgsol2b1': True,
                                 'beempgmprot2b5': True,
                                 'beempgmprot7b6': True,
                                 'beemsnpse5b1': True,
                                 'beemfwt3f3': True,
                                 'beemfwt1f1': True,
                                 'beempgmprot3b2': True,
                                 'beemlptna5b1': True,
                                 'beempgmprot1b1': True,
                                 'beemfwt3f2': True,
                                 'beempgsol5b1': True,
                                 'beemmsmie4f1': True,
                                 'beempgmprot5b5': True,
                                 'beempgmprot7b5': True,
                                 'beemlifts2f1': True,
                                 'beemfwt1f2': True,
                                 'beemskbn3f1': True,
                                 'beempgmprot3b1': True,
                                 'beemfwt1f3': True,
                                 'beempgmprot1b2': True,
                                 'beemfwt3f1': True,
                                 'beemsnpse7b1': True,
                                 'beemprng1b1': True,
                                 'beemndhm4b4': True,
                                 'beempgmprot5b6': True,
                                 'beemplc3b2': True,
                                 'beempgmprot5b2': True,
                                 'beemfwt5f3': True,
                                 'beemrether7b1': True,
                                 'beemsnpse3b1': True,
                                 'beempgmprot1b6': True,
                                 'beempgmprot3b5': True,
                                 'beempgsol3b1': True,
                                 'beempgmprot7b1': True,
                                 'beemfwt5f2': True,
                                 'beemndhm4b1': True,
                                 'beemlifts6f1': True,
                                 'beemndhm4b3': True,
                                 'beempgmprot5b1': True,
                                 'beemlifts4f1': True,
                                 'beempgmprot1b5': True,
                                 'beempgmprot3b6': True,
                                 'beemsnpse1b1': True,
                                 'beemrether5b1': True,
                                 'beempgmprot7b2': True,
                                 'beemfwt5f1': True,
                                 'beemplc1b2': True,
                                 'beemndhm4b2': True}

       

class BuildStaticDb:
    globalVars = GlobalVars() 

    @staticmethod
    def genDirForAigFile(dirName,fileName):
        print('-> genDirForAigFile')
        fullDirPath = dirName+'/'+fileName
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
        fullDirPath = dirName+'/'+ fileName 
        fullAigFileName = fullDirPath + '/' + fileName + '_update.aig'
        fullAagFileName = fullDirPath + '/' + fileName + '.aag'
        # if not os.path.isfile(fullAagFileName):
        cmd = ['./aigtoaig',fullAigFileName,fullAagFileName]
        print('executing cmd: ',cmd)
        call(cmd)
        return False
    
    @staticmethod
    def loadAagAndExportToPkl(dirName,fileName):
        print('-> loadAagAndExportToPkl')
        fullDirPath = dirName+'/'+fileName
        fullAagFileName = fullDirPath + '/' + fileName + '.aag'
        fullPklFileName = fullDirPath + '/' + fileName + '.pkl'
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
        fullDirPath = dirName+'/'+fileName
        fullPklFileName = fullDirPath + '/' + fileName + '.pkl'
        if not os.path.isfile(fullPklFileName):
            print('ERROR: no pkl file: ',fullPklFileName)
            exit()
        with open(fullPklFileName,'rb') as fh:
            pyaig1 = pickle.load(fh)
        for outName in pyaig1.outputs:
            fullPklGraphFileName = fullDirPath + '/g_' + fileName + '.pkl'
            if not os.path.isfile(fullPklGraphFileName):
                g = BuildStaticDb.buildGraph(pyaig1,outName)
                with open(fullPklGraphFileName,'wb') as fh:
                    pickle.dump(g,fh)
            break
    @staticmethod
    def tryLoadPkl(dirName,fileName):
        print('-> tryLoadPkl')
        fullDirPath = dirName+'/'+fileName
        fullPklFileName = fullDirPath + '/' + fileName + '.pkl'
        fullPklGraphFileName = fullDirPath + '/g_' + fileName + '.pkl'
        if not os.path.isfile(fullPklFileName):
            print('ERROR: no pkl file: ',fullPklFileName)
            exit()
        with open(fullPklFileName,'rb') as fh:
            pyaig1 = pickle.load(fh)
        for outName in pyaig1.outputs:
            g = BuildStaticDb.buildGraph(pyaig1,outName)       
        with open(fullPklGraphFileName,'wb') as fh:
            pickle.dump(g,fh)           
        

                    
                    
    @staticmethod
    def convertNewAigFormatToLegacy(dirName,fileName):
        abcPath = '/Users/amirrosenbaum/git/abc'
        inputFilePath  =  dirName + '/' + fileName + '.aig'
        outputFilePath =  dirName + '/' + fileName + '/' + fileName + '_update.aig'
        if not os.path.isfile(outputFilePath):
            cmd = ['{}/./abc'.format(abcPath),'-c', "read {}; zero; fold; write_aiger {}".format(inputFilePath,outputFilePath)]  
            print('executing cmd: ',cmd)
            call(cmd)
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
                
            

    @staticmethod
    def runMaxFlow(dirName,fileName):
        # load aig
        # convert aig to graph
        # for each output
        #    for each input
        #         calc max flow and store it
        return
       
if __name__ == "__main__":
    print('-> starting')
    rootDir = 'hwmcc20/aig/2019/wolf/2018D'
    dirName      = 'hwmcc20/aig/2019/wolf/2019C'
    fileName     = "vgasim_imgfifo-p110"    
    # BuildStaticDb.handleDir(rootDir)
    #BuildStaticDb.handleFile(rootDir,'VexRiscv-regch0-30-p1')
    BuildStaticDb.tryLoadPkl(dirName,fileName)
    print(BuildStaticDb.globalVars.exceptionFiles)