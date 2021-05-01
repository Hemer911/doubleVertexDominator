from node import Node
from edge import Edge
from dominatorChain import DominatorChain
import collections
import copy
import re

class Graph:
    def __init__(self):
        self.V = {}
        self.E = {}
        self.latches = {}
        self.inputs  = set()
        self.outputs = set()
    
    def initNodes(self):
        for _,v in self.V.items():
            v.initNode()

    def addNode(self,node):
        name = node.getName()
        if name in self.V: 
            print("ERROR: node name = {} is already taken.".format(name))
            exit()
        self.V[name] = node
        self.E[name] = {}
        self.E[name]['in'] = []
        self.E[name]['out'] = []
        if re.search('^LatchIn_',name):
            self.latches[name] = node
        node.mark(False)
    
    def getLatches(self):
        return self.latches
    
    def markAllNodes(self,val):
        for _,node in self.V.items():
            self.markNode(node,val)
    
    def markNode(self,node,val):
        node.mark(val)
     
    def addEdge(self,edge):
        src = edge.getSrc()
        dst = edge.getDst()
        srcName = src.getName()
        dstName = dst.getName()
        if srcName not in self.V or dstName not in self.V:
            print("ERROR: illegal edge: one (or both) nodes are not in the graph: srcName = {}, dstName = {}".format(srcName,dstName))
            exit()
        self.E[srcName]['out'].append(dst)
        self.E[dstName]['in'].append(src)
        
    def defineInput(self,node):
        name = node.getName()
        if name not in self.V: 
            print("ERROR: defineInput node name = {} is not part of the graph.".format(name))
            exit()
        self.inputs.add(name)
    
    def undefineInput(self,node):
        name = node.getName()
        if name not in self.V: 
            print("ERROR: undefineInput node name = {} is not part of the graph.".format(name))
            exit()
        if name in self.inputs:
            self.inputs.remove(name)

    def connectGraph(self,subGraph,listOfNamedConnections):
        for _,subV in subGraph.V.items():
            self.addNode(subV)
        for subSrcName,edgeDict in subGraph.E.items():
            for subDstNode in edgeDict['out']:
                src = self.getNode(subSrcName)
                dst = self.getNode(subDstNode.getName())
                self.addEdge(Edge(src,dst))
        for namedConn in listOfNamedConnections:
            srcName = namedConn[0]
            dstName = namedConn[1]
            src = self.getNode(srcName)
            dst = self.getNode(dstName)
            self.addEdge(Edge(src,dst))            
        
    def isInput(self,name):
        return name in self.inputs             
    
    def defineOutput(self,node):
        name = node.getName()
        if name not in self.V: 
            print("ERROR: defineOutput node name = {} is not part of the graph.".format(name))
            exit()
        self.outputs.add(name)
        node.setRoot()

    def fanout(self,v):
        return self.E[v.getName()]['out']
 
    def fanin(self,v):
        return self.E[v.getName()]['in']

    def transFanout(self,v):
        dfsList = self.dfs(v,'fanout')
        return dfsList  
 
    def transFanin(self,v):
        dfsList = self.dfs(v,'fanin')
        return dfsList
         
    def dfs(self,source,direction='fanout'):
        self.setAllVisited(False)
        return self.recDfs(source,direction)
    
    def setAllVisited(self,val):
        self.visited = {}
        for vName in self.V:
            self.visited[vName] = val
            
    def recDfs(self,source,direction):
        sourceName = source.getName()    
        if self.visited[sourceName]: return []
        retList = [source]
        self.visited[sourceName] = True
        if direction == 'fanout':
            children = self.fanout(source)
        elif direction == 'fanin':
            children = self.fanin(source)
        else:
            print('ERROR: recDfs: unknown dir value = {}'.format(dir))
            exit()
        for child in children:
            retList += self.recDfs(child,direction)
        return retList        
        
    def findPath(self,sourceName,targetName,sign):
        source = self.V[sourceName]
        target = self.V[targetName]
        source.mark(False)
        target.mark(False)
        p = self.findPathRec(source,target)
        self.markPath(p,sign)
        source.mark(False)
        target.mark(False)
        return p
        
    def findPathRec(self,source,target):
        if source == target:
            return [target]
        for child in self.fanout(source):
            if child.isMarked(): continue
            retVal = self.findPathRec(child,target)
            if retVal:
                retVal.insert(0,source)
                return retVal
        return False
    
    def getNode(self,name):
        if name in self.V:
            return self.V[name]
        return False
    
    def getNodes(self):
        return list(self.V.values())
    
    def markPath(self,path,sign):
        if not path: return
        
        for node in path:
            if not node.getName() in self.V:
                print("ERROR: node is not member of this graph.")
                node.printNode()
                exit() 
            node.mark(sign)
    
    def printGraph(self):
        print('outputs: = {}'.format(self.outputs))
        print('inputs: = {}'.format(self.inputs))
        print('latches: = {}'.format(self.latches.keys()))
        for vName,v in self.V.items():
            conn = ""
            for node in self.fanout(v):
                conn += "({},{}) ".format(vName,node.getName())
            print(conn) 
            v.printNode()
    
    
    def bfsTree(self,source,direction,visited = {}):        
        bfsParentTree = {}
        for vName in self.V:
            if vName not in visited:                
                visited[vName] = False    
        queue = collections.deque()
        queue.append(source)
        source.setHight(0)
        bfsParentTree[source] = False
        visited[source.getName()] = True
        while queue:
            u = queue.popleft()
            if direction == 'fanout':
                children = self.fanout(u)
            elif direction == 'fanin':
                children = self.fanin(u)
            else:
                print('ERROR: bfsTree - unknown direction = {}'.format(direction))
                exit()
            for dst in children:
                if visited[dst.getName()] == False:
                    bfsParentTree[dst] = u
                    dst.setHight(u.getHight()+1)
                    queue.append(dst)
                    visited[dst.getName()] = True
        return bfsParentTree    
    
    def getDoubleVertexConOfInf(self,doubleVertexTup):
        v1 = self.getNode(doubleVertexTup[0])
        v2 = self.getNode(doubleVertexTup[1])
        conOfInf1 = self.getNodeConOfInf(v1,'fanin')
        conOfInf2 = self.getNodeConOfInf(v2,'fanin',conOfInf1)
        return conOfInf2
 
    def getNodeConOfInf(self,source,direction,prevConOfInf = {}):
        conOfInf = copy.deepcopy(prevConOfInf)
        visited = {}
        for vName in self.V:
            if vName in conOfInf:
                visited[vName] = True
            else:
                visited[vName] = False                
        queue = collections.deque()
        queue.append(source)
        visited[source.getName()] = True
        conOfInf[source.getName()] = True
        while queue:
            u = queue.popleft()
            if direction == 'fanout':
                children = self.fanout(u)
            elif direction == 'fanin':
                children = self.fanin(u)
            else:
                print('ERROR: bfsTree - unknown direction = {}'.format(direction))
                exit()
            for dst in children:
                if visited[dst.getName()] == False:
                    conOfInf[dst.getName()] = True
                    queue.append(dst)
                    visited[dst.getName()] = True
        return conOfInf               
        
    def getNodeHight(self,nodeName):
        node = self.getNode(nodeName)
        return node.getHight()
        
    def bfs(self,source,target):
        visited = {}
        parent = {}
        for vName in self.V:
            visited[vName] = False
        # Create a queue for BFS
        queue = collections.deque()
        # Mark the source node as visited and enqueue it
        queue.append(source)
        visited[source.getName()] = True
        # Standard BFS loop
        while queue:
            u = queue.popleft()
            # Get all adjacent vertices of the dequeued vertex u
            # If an adjacent has not been visited, then mark it
            # visited and enqueue it
            for dst in self.fanout(u):
                dstName = dst.getName()
                if (visited[dstName] == False):
                    queue.append(dst)
                    visited[dstName] = True
                    parent[dstName] = u
        # If we reached sink in BFS starting from source, then return
        # true, else false
        if not visited[target.getName()]: return False
        return parent
    
    def buildResidualGraph(self):
        self.resG = Graph()
        for vName in self.V:
            v_in   = Node("{}_in".format(vName))
            v_out  = Node("{}_out".format(vName))
            e      = Edge(v_in,v_out)
            self.resG.addNode(v_in)
            self.resG.addNode(v_out)
            self.resG.addEdge(e)            
        for srcName,connDict in self.E.items():
            resSrcName = "{}_out".format(srcName)
            for dst in connDict['out']:
                dstName = dst.getName()
                resDstName = "{}_in".format(dstName)
                self.resG.connect(resSrcName,resDstName)

    def connect(self,srcName,dstName):
        e = Edge(self.V[srcName],self.V[dstName])
        self.addEdge(e)

    
    def removeEdge(self,edge):
        src = edge.getSrc()
        dst = edge.getDst()
        srcName = src.getName()
        dstName = dst.getName()
        if dst in self.fanout(src):
            self.E[srcName]['out'] = list(filter((dst).__ne__, self.E[srcName]['out']))
            self.E[dstName]['in'] = list(filter((src).__ne__, self.E[dstName]['in']))
    
    def removeNode(self,vName):
        v = self.V[vName]        
        for u in self.fanin(v):
            e = Edge(u,v)
            self.removeEdge(e)
        for u in self.fanout(v):
            e = Edge(v,u)
            self.removeEdge(e)
        for uName in self.V:
            if v in self.E[uName]['in']:
                print('ERROR: found {} in E[{}][in]'.format(vName,uName))
            if v in self.E[uName]['out']:
                print('ERROR: found {} in E[{}][out]'.format(vName,uName))    
            
        del self.E[vName]
        del self.V[vName]         
            
    def edmonds_karp(self,source,target,maxFlowBound=3):
        self.buildResidualGraph()
        source = self.resG.V["{}_out".format(source.getName())]
        target = self.resG.V["{}_in".format(target.getName())]
        maxFlow = 0 
        # Augment the flow while there is path from source to sink
        parent = self.resG.bfs(source, target)
        while parent:
            # here path flow is 1 but in the general case we should find the min residual capacity
            path_flow = 1
            maxFlow += path_flow
            if maxFlow >= maxFlowBound: return maxFlow
            v = target
            while v != source:
                vName = v.getName()
                u = parent[vName]
                e = Edge(u,v) 
                revE = Edge(v,u)
                self.resG.removeEdge(e)
                self.resG.addEdge(revE)
                v = parent[vName]
            parent = self.resG.bfs(source, target)
        return maxFlow

    def printPath(self,path,source,target):
        v = target
        str = ""
        while v!= source:
            vName  = v.getName()
            str = " -> " + vName + str
            v = path[vName]
        print('amirros debug: path = ',str)            
        
    def getEdge(self,srcName,dstName):
        if srcName not in self.E: return False
        src = self.V[srcName]
        for dst in self.fanout(src):
            if dstName == dst.getName():                
                return Edge(src,dst)
        return False
    
    def getNodesNum(self):
        return len(self.V)
    
    def findDisjointPaths(self,source,target):        
        maxFlow = self.edmonds_karp(source,target)
        if maxFlow != 2: return False
        retVal = [0,0]
        # remove all original edges from the residual graph:
        edgesToRemove =[]
        for resSrcName,connDict in self.resG.E.items():
            srcName = resSrcName.replace('_in','')
            srcName = srcName.replace('_out','')
            for resDst in connDict['out']:
                resDstName = resDst.getName()
                dstName = resDstName.replace('_in','')
                dstName = dstName.replace('_out','')
                # print('amirros debug: trying res = ({},{}), orig = ({},{})'.format(resSrcName,resDstName,srcName,dstName))
                if self.getEdge(srcName,dstName):
                    # print('amirros debug: found  ({},{}) in the original graph'.format(resSrcName,resDstName))
                    resSrc = self.resG.V[resSrcName]
                    edgesToRemove.append(Edge(resSrc,resDst))
        for e in edgesToRemove:
            self.resG.removeEdge(e)
        targetRes = self.resG.getNode('{}_in'.format(target.getName()))
        sourceRes = self.resG.getNode('{}_out'.format(source.getName()))
        for i in range(2):
            reversePathInRes = self.resG.bfs(targetRes,sourceRes)
            pathInOrig = [source]
            vRes = sourceRes
            while vRes != targetRes:
                vResName = vRes.getName()
                uRes = reversePathInRes[vResName]
                uName = uRes.getName().replace('_in','')
                uName = uName.replace('_out','')
                u = self.getNode(uName)
                if u not in pathInOrig:
                    pathInOrig.append(u)
                e = Edge(uRes,vRes)
                self.resG.removeEdge(e)
                vRes = reversePathInRes[vResName]
            retVal[i] = pathInOrig                
        return retVal
      
if __name__ == "__main__":
    u = Node('u')
    a = Node('a')
    b = Node('b')
    c = Node('c')
    d = Node('d')
    e = Node('e')
    f = Node('f')
    g = Node('g')
    h = Node('h')
    k = Node('k')
    l = Node('l')
    m = Node('m')
    n = Node('n')

    f.setRoot()
    
    G = Graph()
        
    G.addNode(u)
    G.addNode(a)
    G.addNode(b)
    G.addNode(c)
    G.addNode(d)
    G.addNode(e)
    G.addNode(f)
    G.addNode(g)
    G.addNode(h)
    G.addNode(k)
    G.addNode(l)
    G.addNode(m)
    G.addNode(n)
    

    
    G.addEdge(Edge(u,a))
    G.addEdge(Edge(u,b))

    G.addEdge(Edge(a,e))
    G.addEdge(Edge(a,c))    

    G.addEdge(Edge(b,c))

    G.addEdge(Edge(c,d))    

    G.addEdge(Edge(d,e))
    G.addEdge(Edge(d,h))
    G.addEdge(Edge(d,g))
    
    G.addEdge(Edge(e,h))

    G.addEdge(Edge(g,k))
    G.addEdge(Edge(g,l))

    G.addEdge(Edge(h,l))
    G.addEdge(Edge(h,k))
    
    G.addEdge(Edge(k,m))
    
    G.addEdge(Edge(l,n))
    
    G.addEdge(Edge(m,f))

    G.addEdge(Edge(n,f)) 
    
    # G.printGraph()
    DC = DominatorChain(G,f,u)
    dfsNode = d
    dfsList = G.transFanout(dfsNode)
    s = ""
    for node in dfsList:
        s += node.getName() + ' '    
    print('transFanout: ',s)
    dfsList = G.transFanin(dfsNode)
    s = ""
    for node in dfsList:
        s += node.getName() + ' '   
    print('transFanin: ',s)
    exit()
    D_uStr = "("
    for tup in DC.D_u:
        firstStr = ""
        for v in tup[0]:
            firstStr += v.getName() + ','
        secStr = ""
        for v in tup[1]:
            secStr += v.getName() + ','  
        D_uStr += "(" + firstStr +" | " + secStr + "),"
    D_uStr += ")"         
    print(DC.D_u)
    print(D_uStr)