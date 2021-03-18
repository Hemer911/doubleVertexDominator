class DominatorChain:
    def __init__(self,G,root,u):
        self.G = G
        self.u = u
        self.root = root
        self.D_u = False
        paths = self.G.findDisjointPaths(self.u,self.root)        
        if paths: 
            p1 = paths[0]
            p2 = paths[1]
        else: 
            return    
        # Exact 2 disjoint paths
        self.G.markAllNodes(False)
        self.assignMinMax(p1,p2)
        self.G.markAllNodes(False)
        self.assignMinMax(p2,p1)
        self.L = self.constructVector(p1,p2)
        self.R = self.constructVector(p2,p1)
        print('amirros debug: L = {}'.format(self.L))
        print('amirros debug: R = {}'.format(self.R))
        print('amirros debug: R = {}'.format(self.pathAsStr(self.R)))
        self.convertMinMax(self.L,self.R,p2)
        self.convertMinMax(self.R,self.L,p1)
        self.constructD_U(self.L,self.R)
    
    def pathAsStr(self,path):
        pStr = ""
        for v in path:
            pStr += v.getName() +'.(min({}),max({}),prime({}))'.format(v.getMin(),v.getMax(),v.getPrime()) +  '-> ' 
        return pStr
            
    def assignMinMax(self,p1,p2):
        self.reached_p1 = 1
        self.reached_p2 = 2
        self.new_reached_p1 = self.reached_p1
        self.new_reached_p2 = self.reached_p2
        self.last_prime = 1
        for i in range(2,len(p1)):
            if self.reached_p1 > i:
                self.setMin(p1,i,len(p2))
                self.setPrime(p1,i,self.last_prime)
            else:
                self.setMin(p1,i,self.reached_p2)
                self.setPrime(p1,self.last_prime,i)
                self.last_prime = i
            v_i = p1[i-1]
            for y in self.G.fanout(v_i):
                if y in p1: continue
                self.findReachable(y,p1,p2)
            if self.reached_p1 < self.new_reached_p1:
                self.reached_p1 = self.new_reached_p1
            if self.reached_p2 >= self.new_reached_p2: 
                continue
            for j in range(self.reached_p2,self.new_reached_p2):
                self.setMax(p2,j,i)
            self.reached_p2 = self.new_reached_p2
        for j in range(self.reached_p2,len(p2)):
            self.setMax(p2,j,len(p1)-1)
       
        self.setPrime(p1, self.last_prime, len(p1))
        
    # the fanout includes the partial path p that we allready found.
    # we remove one pointer to vertex of p. 
    def cleanFanout(self,partialPath,transFanout):
        for v in partialPath:
            if v in transFanout:
                transFanout.remove(v)
        return transFanout
                    
    def findReachable(self,y,p1,p2):
        if y.isMarked(): return
        y.mark(True)
        if y.isRoot():
            self.new_reached_p1 = len(p1)
            # self.new_reached_p2 = len(p2)
            return
        if y in p1:
            i = p1.index(y) + 1
            if i > self.new_reached_p1: 
                    self.new_reached_p1 = i
                    return
        if y in p2:
            j = p2.index(y) + 1
            if j > self.new_reached_p2:
                self.new_reached_p2 = j
                return           
        for v in self.G.fanout(y):
            self.findReachable(v,p1,p2)                 
    
    
    def constructVector(self,p1,p2):
        retV = []
        for i in range(2,len(p1)+1):
            v_i = p1[i-1]
            minVi = v_i.getMin()
            maxVi = v_i.getMax()
            w_min = p2[minVi-1]
            w_max = p2[maxVi-1]
            if minVi == len(p2): break
            if w_min.getMin() == len(p1):
                primeIndex_w_min = w_min.getPrime()
                w_min_prime =  p2[primeIndex_w_min-1]
                v_i.setMin(w_min_prime.getPrime())
            if w_max.getMin == len(p1):
                v_i.setMax(w_max.getPrime())
            if v_i.getMin() <= v_i.getMax():
                retV.append(v_i)              
        return retV    

    def convertMinMax(self,V1,V2,p):
        print('amirros debug: V1 = {}'.format(V1))
        print('amirros debug: V2 = {}'.format(V2))
        print('amirros debug: p = {}'.format(p))
        for v in V1:
            minVIndex = v.getMin() # index in p
            maxVIndex = v.getMax() # index in p
            print('amirros debug: minVIndex = {}, maxVIndex = {}'.format(minVIndex,maxVIndex))
            minV = p[minVIndex-1] # actual vertex
            maxV = p[maxVIndex-1] # actual vertex 
            # assign min\max index in L\R domain instead of p1,p2 domain
            v.setMin(V2.index(minV)+1) 
            v.setMax(V2.index(maxV)+1)
            
        # TODO
    def constructD_U(self,L,R):
        beginL = 1
        beginR = 1
        endL = 1
        endR = 1
        D_u = []
        while endL < len(L):
            while True:
                vEndL = L[endL-1]
                endRNew = vEndL.getMax()
                if endRNew == endR: break
                endR = endRNew
                wEndR = R[endR-1]
                endLNew = wEndR.getMax()
                print('amirros debug: endL = {}, endLNew = {}, endR = {}, endRNew = {}'.format(endL,endLNew,endR,endRNew))
                if endLNew == endL: break
                endL = endLNew
            C      = L[beginL-1:endL]
            C_comp = R[beginR-1:endR] 
            D_u.append((C,C_comp))
            beginL = endL+1
            beginR = endR+1
            endL +=1
        self.D_u = D_u
       
    def setMin(self,p,i,val):
        v = p[i-1]
        v.setMin(val)
    
    def setMax(self,p,i,val):
        v = p[i-1]
        v.setMax(val)
    
    def setPrime(self,p,i,prime):
        v = p[i-1]
        v.setPrime(prime)