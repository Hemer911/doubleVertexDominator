class DominatorChain:
    def __init__(self,G,root,u):
        self.G = G
        self.G.initNodes()
        self.u = u
        self.root = root
        self.D_u = False
        self.L = False
        self.R = False
        self.maxFlow = False
        paths = self.G.findDisjointPaths(self.u,self.root)        
        if paths: 
            self.maxFlow = 2
            p1 = paths[0]
            p2 = paths[1]
        else: 
            return    
        # Exact 2 disjoint paths
        # print('amirros debug: found 2 paths:')
        # print('amirros debug: len(p1) = {}, p1 = {}'.format(len(p1),self.pathAsStr(p1)))
        # print('amirros debug: len(p2) = {}, p2 = {}'.format(len(p2),self.pathAsStr(p2)))        
        self.G.markAllNodes(False)
        # print('amirros debug: assignMinMax(p1,p2)')
        self.assignMinMax(p1,p2)
        self.G.markAllNodes(False)
        # print('amirros debug: assignMinMax(p2,p1)')
        self.assignMinMax(p2,p1)
        # print('amirros debug: after assignMinMax: len(p1) = {}, p1 = {}'.format(len(p1),self.pathAsStr(p1)))
        # print('amirros debug: after assignMinMax: len(p2) = {}, p2 = {}'.format(len(p2),self.pathAsStr(p2)))         
        self.L = self.constructVector(p1,p2)
        self.R = self.constructVector(p2,p1)
        # print('amirros debug: after constructVector - L = {}'.format(self.L))
        # print('amirros debug: after constructVector - R = {}'.format(self.R))
        # print('amirros debug: after constructVector - L = {}'.format(self.pathAsStr(self.L)))
        # print('amirros debug: after constructVector - R = {}'.format(self.pathAsStr(self.R)))
        if len(self.L) == 0 or len(self.R) == 0:
            print('found empty vector') 
            return
        self.convertMinMax(self.L,self.R,p2)
        self.convertMinMax(self.R,self.L,p1)
        # print('amirros debug: after convertMinMax - L = {}'.format(self.pathAsStr(self.L)))
        # print('amirros debug: after convertMinMax - R = {}'.format(self.pathAsStr(self.R)))
        return     
        self.constructD_U(self.L,self.R)
    
    def getVector(self,name):
        retList = []
        if name == 'L':
            vec = self.L
        elif name == 'R':
            vec = self.R
        else:
            print('ERROR: unknown name = {} to getVector'.format(name))
            exit()
        if vec:      
            for node in vec:
                tup = (node.getName(),node,node.getMin(),node.getMax())
                retList.append(tup)
        return retList
    
    def getR(self):
        return self.getVector('R')
    
    def getL(self):
        return self.getVector('L')
    
    def pathAsStr(self,path):
        pStr = ""
        for v in path:
            pStr += v.getName() +'.(min({}),max({}),prime({}))'.format(v.getMin(),v.getMax(),v.getPrime()) +  '-> ' 
        return pStr
            
    def assignMinMax(self,p1,p2):
        self.reached_p1 = 0
        self.reached_p2 = 1
        self.new_reached_p1 = self.reached_p1
        self.new_reached_p2 = self.reached_p2
        self.last_prime = 0
        for i in range(0,len(p1)-1):
            # print('amirros debug: beginning of assignMinMax iter: p1 = {}'.format(self.pathAsStr(p1)))
            # print('amirros debug: beginning of assignMinMax iter: p2 = {}'.format(self.pathAsStr(p2)))
            if self.reached_p1 > i:
                self.setMin(p1,i,len(p2)-1)
                self.setPrime(p1,i,self.last_prime)
            else:
                self.setMin(p1,i,self.reached_p2)
                self.setPrime(p1,self.last_prime,i)
                self.last_prime = i
            v_i = p1[i]
            # print('amirros debug: v_i = {}'.format(v_i.getName()))
            for y in self.G.fanout(v_i):
                if self.isNext(v_i,i,y,p1,p2): continue
                # print('amirros debug: finding reach of {}: y = {}'.format(v_i.getName(),y.getName()))
                self.findReachable(y,p1,p2)
            if self.reached_p1 < self.new_reached_p1:
                self.reached_p1 = self.new_reached_p1
            if self.reached_p2 > self.new_reached_p2:
                print('ERROR: self.reached_p2 >= self.new_reached_p2: self.reached_p2 = {}, self.new_reached_p2 = {}'.format(self.reached_p2,self.new_reached_p2))                 
                exit()
            if self.reached_p2 == self.new_reached_p2:
                continue
            for j in range(self.reached_p2,self.new_reached_p2):
                # print('amirros debug: first loop')
                self.setMax(p2,j,i)
            self.reached_p2 = self.new_reached_p2
            # print('amirros debug: end of assignMinMax iter: p1 = {}'.format(self.pathAsStr(p1)))
            # print('amirros debug: end of assignMinMax iter: p2 = {}'.format(self.pathAsStr(p2)))
        for j in range(self.reached_p2,len(p2)):
            # print('amirros debug: second loop')
            self.setMax(p2,j,len(p1)-2)
       
        self.setPrime(p1, self.last_prime, len(p1)-1)
    
    def isNext(self,v,i,y,p1,p2):
        if v == self.u:
            if y == p1[1] or y == p2[1]:
                return True
        if y == p1[i+1]: 
            return True
        return False
                    
    def findReachable(self,y,p1,p2):
        if y.isMarked(): return
        y.mark(True)
        if y.isRoot():
            # print('amirros debug: found root')
            self.new_reached_p1 = len(p1)-1
            return
        if y in p1:
            # print('amirros debug: {} found in p1'.format(y.getName()))
            i = p1.index(y)
            if i > self.new_reached_p1: 
                    self.new_reached_p1 = i
                    # print('amirros debug: after {}, i = {}, new_reached_p1 = {}'.format(y.getName(),i,self.new_reached_p1))
                    return
        if y in p2:
            # print('amirros debug: {} found in p2'.format(y.getName()))
            j = p2.index(y)
            if j > self.new_reached_p2:
                self.new_reached_p2 = j
                # print('amirros debug: after {}, j = {}, new_reached_p2 = {}'.format(y.getName(),j,self.new_reached_p2))
                return           
        for v in self.G.fanout(y):
            self.findReachable(v,p1,p2)                 
    
    
    def constructVector(self,p1,p2):
        retV = []
        for i in range(1,len(p1)-1):
            v_i = p1[i]
            minVi = v_i.getMin()
            maxVi = v_i.getMax()
            w_min = p2[minVi]
            w_max = p2[maxVi]
            # print('amirros debug: constructVector: v_i = {}, minVi = {}, maxVi = {}'.format(v_i.getName(),minVi,maxVi))
            # print('amirros debug: constructVector: w_min = {}, minVi = {}, maxVi = {}'.format(w_min.getName(),w_min.getMin(),w_min.getMax()))
            # print('amirros debug: constructVector: w_max = {}, minVi = {}, maxVi = {}'.format(w_max.getName(),w_max.getMin(),w_max.getMax()))
            if minVi == len(p2)-1: continue
            if w_min.getMin() == len(p1)-1:
                # print('amirros debug: constructVector: w_min.getMin() == len(p1)-1')
                primeIndex_w_min = w_min.getPrime()
                w_min_prime =  p2[primeIndex_w_min]
                v_i.setMin(w_min_prime.getPrime())                
            if w_max.getMin() == len(p1)-1:
                # print('amirros debug: constructVector: w_max.getMin() == len(p1)-1')
                v_i.setMax(w_max.getPrime())
            if v_i.getMin() <= v_i.getMax():
                # print('amirros debug: constructVector: append')
                retV.append(v_i)              
        return retV    

    def convertMinMax(self,V1,V2,p):
        # print('amirros debug: V1 = {}'.format(self.pathAsStr(V1)))
        # print('amirros debug: V2 = {}'.format(self.pathAsStr(V2)))
        # print('amirros debug: p = {}'.format(self.pathAsStr(p)))
        for v in V1:
            minVIndex = v.getMin() # index in p
            maxVIndex = v.getMax() # index in p
            # print('amirros debug: v = {}, minVIndex = {}, maxVIndex = {}'.format(v.getName(),minVIndex,maxVIndex))
            minV = p[minVIndex] # actual vertex
            maxV = p[maxVIndex] # actual vertex 
            # assign min\max index in L\R domain instead of p1,p2 domain
            v.setMin(V2.index(minV)) 
            v.setMax(V2.index(maxV))
            
    def constructD_U(self,L,R):
        beginL = 0
        beginR = 0 
        endL = 0
        endR = 0
        D_u = []
        while endL < len(L):
            while True:
                vEndL = L[endL]
                endRNew = vEndL.getMax()
                if endRNew == endR: break
                endR = endRNew
                wEndR = R[endR]
                endLNew = wEndR.getMax()
                # print('amirros debug: endL = {}, endLNew = {}, endR = {}, endRNew = {}'.format(endL,endLNew,endR,endRNew))
                if endLNew == endL: break
                endL = endLNew
            C      = L[beginL:endL+1]
            C_comp = R[beginR:endR+1] 
            D_u.append((C,C_comp))
            beginL = endL+1
            beginR = endR+1
            endL +=1
        self.D_u = D_u
       
    def setMin(self,p,i,val):
        v = p[i]
        v.setMin(val)
    
    def setMax(self,p,i,val):
        v = p[i]
        v.setMax(val)
    
    def setPrime(self,p,i,prime):
        v = p[i]
        v.setPrime(prime)