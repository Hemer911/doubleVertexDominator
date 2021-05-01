import pickle
import os

from wolfDb import wolfDb
from validDominatorsDb import validDominatorsDb

from buildStaticDb import BuildStaticDb
from dominatorChain import DominatorChain
from graphSplitter import GraphSplitter
from dominatorsAndSATSolver import DominatorsAndSATSolver
from dominatorsDb import DominatorsDb
  
if __name__ == "__main__":
    fileName  = 'qspiflash_qflexpress_divfive-p094'
    dirName = 'hwmcc20/aig/2019/wolf/2019C'
    #dirName = 'hwmcc20/aig/2019/beem/'
    #fileName  = 'krebs.3.prop1-func-interl'
    validate = False
    loadPkl = True
    print('-> genDb')
    domDb = DominatorsDb(dirName,fileName,validate=validate,loadPkl=loadPkl)
    g = domDb.g
    print('-> choose double vertex dominators')
    domTup = ('Inverter_39', 'Inverter_699') # 15%
    #domTup = ('Inverter_39', 'AndGate_22') # 50%
    print('-> split graphs')
    (restGAig,cutG) = GraphSplitter.splitGraph(g,domTup)
    DominatorsAndSATSolver.handleCutGraph(cutG,domTup,[],[])
    print('-> solve for splitted graph')
    DominatorsAndSATSolver.solveGraph(restGAig, cutG, domTup,boundT=600)