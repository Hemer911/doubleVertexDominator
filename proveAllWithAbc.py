import sys
import os
from os import listdir
from subprocess import call
from util import Util
from buildStaticDb import BuildStaticDb

supportedAbcFunctions = ['bmc3','int','pdr','ind','dprove'] # 'iprove'
T = 180
F = 200
def runAbc(aigPath,outputDir,outputName,abcFunc,T,F):
    abcPath = Util.abcPath
    cmd = ['{}/abc'.format(abcPath),'-c', "read {}; zero; fold; {} -v -F {} -T {}; write_aiger_cex {}/{}_cex.aig.log".format(aigPath,abcFunc,F,T,outputDir,abcFunc)]  
    with open(outputDir + '/' + outputName,'w') as fh:
        call(cmd,stdout=fh)

def handleFile(dirName,fileName):
    # verify that this is an originak aig and not an output file
    if "_update" in fileName:
        return
    aigPath       = dirName + '/' + fileName + '.aig'
    outputDirPath = dirName + '/' + fileName
    # make out dir if needed
    if not os.path.isdir(outputDirPath):
        print('creating dir for ',outputDirPath)
        os.mkdir(outputDirPath)
    abcOutputsDir = outputDirPath + '/abcLogs'
    if not os.path.isdir(abcOutputsDir):
        print('creating dir for ',abcOutputsDir)
        os.mkdir(abcOutputsDir)
    # run abc for all commands
    for abcFunc in supportedAbcFunctions:
        logName = abcFunc + '.log'        
        if os.path.isfile(abcOutputsDir + '/' + logName):
            print('{} is already exists for {}'.format(logName,fileName))
            continue                       
        print('executing {} for {}'.format(abcFunc,aigPath))
        runAbc(aigPath,abcOutputsDir,logName,abcFunc,T,F)
    
def handleDir(dirName):
    for fileFullName in listdir(dirName):
        fileName, fileExtension = os.path.splitext(fileFullName)
        if os.path.isdir(dirName+'/'+ fileFullName):
            print('call handleDir for ',dirName + '/' + fileFullName)
            handleDir(dirName + '/' + fileFullName)
        elif fileExtension == '.aig':
            handleFile(dirName,fileName)
        else:
            print('ignoring: {}/{}. fileExtension = {}'.format(dirName,fileFullName,fileExtension))

fileName  = 'qspiflash_qflexpress_divfive-p094'
dirName = 'hwmcc20/aig/2019/wolf'
handleDir(dirName)