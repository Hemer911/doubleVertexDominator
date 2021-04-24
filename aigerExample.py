import aiger
from node import Node
from edge import Edge
from graph import Graph
import pickle
from graphSplitter import GraphSplitter
o = Node('out1')
l1 = Node('LatchIn_1')
l2 = Node('LatchIn_2')
and1 = Node('AndGate_1')
and2 = Node('AndGate_2')
and3 = Node('AndGate_3')
and4 = Node('AndGate_4')
and5 = Node('AndGate_5')
not1 = Node('Inverter_1')
not2 = Node('Inverter_2')
not3 = Node('Inverter_3')
constF = Node('ConstFalse_1')
pi1 = Node('Input_PI1')
pi2 = Node('Input_PI2')

g = Graph()

g.addNode(o)
g.defineOutput(o)

g.addNode(l1)
g.addNode(l2)

g.addNode(and1)
g.addNode(and2)
g.addNode(and3)
g.addNode(and4)
g.addNode(and5)

g.addNode(not1)
g.addNode(not2)
g.addNode(not3)

g.addNode(constF)

g.addNode(pi1)
g.defineInput(pi1)
g.addNode(pi2)
g.defineInput(pi2)

g.addEdge(Edge(and1,o))
g.addEdge(Edge(and2,and1))
g.addEdge(Edge(not3,and1))
g.addEdge(Edge(constF,not3))
g.addEdge(Edge(and3,and2))
g.addEdge(Edge(not2,and2))
g.addEdge(Edge(pi2,not2))
g.addEdge(Edge(l1,and3))
g.addEdge(Edge(l2,and3))
g.addEdge(Edge(and4,l1))
g.addEdge(Edge(and5,l2))
g.addEdge(Edge(pi1,and4))
g.addEdge(Edge(l2,and4))
g.addEdge(Edge(l1,and5))
g.addEdge(Edge(not1,and5))
g.addEdge(Edge(pi1,not1))

outAtom = GraphSplitter.graphToAig(g)
print(outAtom)
domTup = ('LatchIn_1','LatchIn_2')
cutG = GraphSplitter.splitGraph(g, domTup)

exit()






l_ci1,l_ci2,pi = aiger.atoms('L_CI','L_CI','PI')

l_ci1 = l_ci1.with_output('O')
andExpr = l_ci2 & pi
andExpr = andExpr.with_output('L_CO')
fullAig = l_ci1.aig | andExpr.aig
fullAig = fullAig.feedback(['L_CI'],['L_CO'])

print(fullAig)
exit()




PI1,PI2 = aiger.atoms('PI1','PI2')
CI1,CI2 = aiger.atoms('CI1','CI2')
PI1  = PI1.with_output('PI1')
PI2  = PI2.with_output('PI2')
andExpr  = CI1 & CI2
andExpr  = andExpr.with_output('CO')
andAig   = andExpr.aig
fullAig = andAig | PI1.aig | PI2.aig
fullAig = fullAig.feedback(['CI1'],['PI1'])
fullAig = fullAig.feedback(['CI2'],['PI2'])
#fullAig = andAig 
#print(fullAig.loopback({"input": "b", "output": "a","init":True}))
print(fullAig)
exit()





in1,out1 = aiger.atoms('in1','out1')
in2,in3  = aiger.atoms('in2','in3')
expr1 = out1.with_output('out1')
expr2 = in2 & in3
aig1 = in1.aig | expr1.aig
aig2 = aig1.feedback(['in1'],['out1'])
aig3 = aig2 | expr2.aig
expr4 = aiger.BoolExpr(aig3)
in4,in5 = aiger.atoms('in4','in5')
expr5 = in4 & expr4
print(expr5.aig)
exit()


outAtom = GraphSplitter.graphToAig(g,o)
print(outAtom)
exit()

w,x,y,z,o = aiger.atoms('w','x','y','z','o')
expr1 = x & y
expr2 = expr1.with_output('and1')
expr3 = z & w
expr4 = expr3.with_output('and2')
aig1 = expr2.aig | expr4.aig
aig2 = aig1.feedback(['z'],['and1'])

print(aig2)
exit()

expr1 = x.with_output('x')
aig1 = expr1.aig.loopback({"input": "l1", "output": "x","init":True})
expr2 = z.with_output('sadfsd')
aig2 = expr2.aig.loopback({"input": "l2", "output": "sadfsd","init":True})
print(aiger.BoolExpr(aig2).with_output('sdf'))

expr3 = x & z
# print(expr3)
# expr2 = y & w
# expr3 = expr1 & expr2
expr4 = expr3.with_output('o')
#expr3 = expr1.aig | expr2.aig
#expr3 = expr1.aig >> expr2.aig
aig2 = expr4.aig.loopback({"input": "l1", "output": "o",})
aig3 = aig2.with_output('l1')


# print(expr1)
# print(expr2)
print(aig2)
exit()


# outAtom = GraphSplitter.graphToAig(g,o)
# print(outAtom)
exit()



x, y, z = aiger.atoms('x', 'y', 'z')
expr1 = x & y  # circuit with inputs 'x', 'y' and 1 output computing x AND y.
expr2 = x | y  # logical or.
expr3 = x ^ y  # logical xor.
expr4 = x == y  # logical ==, xnor.
expr5 = x.implies(y)
expr6 = ~x  # logical negation.
expr7 = aiger.ite(x, y, z)  # if x then y else z.

# Atoms can be constants.
expr8 = x & True  # Equivalent to just x.
expr9 = x & False # Equivalent to const False.

# Specifying output name of boolean expression.
# - Output is a long uuid otherwise.
expr10 = expr5.with_output('x_implies_y')
print(expr10)
assert expr10.output == 'x_implies_y'

# And you can inspect the AIG if needed.
circ = x.aig

# And of course, you can get a BoolExpr from a single output aig.
expr10 = aiger.BoolExpr(circ)
exit()
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