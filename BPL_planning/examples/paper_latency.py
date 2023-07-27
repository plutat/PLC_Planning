import pandas as pd

from calculations import latency
from graphs.EnergyGraph import EnergyGraph
from graphs.RoutingGraph import RoutingGraph
from graphs.RoutingEdge import RoutingEdge
from graphs.Node import Node
from graphs.EnergyEdge import EnergyEdge
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


#Initializing an exemplary network
eGraph = EnergyGraph()
rGraph = RoutingGraph(eGraph, 0, 0)

n0 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node0", None)
n1 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node1", None)
n2 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node2", None)
n2.isSending = False
n3 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node3", None)
n3.isSending = False
n4 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node4", None)
n4.isSending = False
n5 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node5", None)
n6 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node6", None)
n6.isSending = False
n7 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node7", None)
n7.isSending = False
n8 = Node(eGraph.getUniqueId(), 0, 0, 0, "Node8", None)
n8.isSending = False

e1 = EnergyEdge(eGraph.getUniqueId(), n1, n5, 0, 0, 100, "Edge1")
e2 = EnergyEdge(eGraph.getUniqueId(), n2, n5, 0, 0, 80, "Edge2")
e3 = EnergyEdge(eGraph.getUniqueId(), n3, n5, 0, 0, 90, "Edge3")
e4 = EnergyEdge(eGraph.getUniqueId(), n4, n5, 0, 0, 70, "Edge4")
e5 = EnergyEdge(eGraph.getUniqueId(), n5, n0, 0, 0, 500, "Edge5")
e6 = EnergyEdge(eGraph.getUniqueId(), n6, n0, 0, 0, 300, "Edge6")
e7 = EnergyEdge(eGraph.getUniqueId(), n7, n0, 0, 0, 500, "Edge7")
e8 = EnergyEdge(eGraph.getUniqueId(), n8, n0, 0, 0, 700, "Edge8")

n5.addEnergyEdgeIn(e1)
n5.addEnergyEdgeIn(e2)
n5.addEnergyEdgeIn(e3)
n5.addEnergyEdgeIn(e4)

n0.addEnergyEdgeIn(e5)
n0.addEnergyEdgeIn(e6)
n0.addEnergyEdgeIn(e7)
n0.addEnergyEdgeIn(e8)

n1.addEnergyEdgeOut(e1)
n2.addEnergyEdgeOut(e2)
n3.addEnergyEdgeOut(e3)
n4.addEnergyEdgeOut(e4)
n5.addEnergyEdgeOut(e5)
n6.addEnergyEdgeOut(e6)
n7.addEnergyEdgeOut(e7)
n8.addEnergyEdgeOut(e8)

r1 = RoutingEdge(rGraph.getUniqueId(), n1, n5, [e1])
r1.setphysDataRate(10)
r2 = RoutingEdge(rGraph.getUniqueId(), n2, n5, [e2])
r2.setphysDataRate(20)
r3 = RoutingEdge(rGraph.getUniqueId(), n3, n5, [e3])
r3.setphysDataRate(50)
r4 = RoutingEdge(rGraph.getUniqueId(), n4, n5, [e4])
r4.setphysDataRate(0.5)
r5 = RoutingEdge(rGraph.getUniqueId(), n5, n0, [e5])
r5.setphysDataRate(100)
r6 = RoutingEdge(rGraph.getUniqueId(), n6, n0, [e6])
r6.setphysDataRate(30)
r7 = RoutingEdge(rGraph.getUniqueId(), n7, n0, [e7])
r7.setphysDataRate(300)
r8 = RoutingEdge(rGraph.getUniqueId(), n8, n0, [e8])
r8.setphysDataRate(5)


mycolors = ['#021F72', '#00549f', '#407fb7', '#8ebae5', ]      #multiple colors for plotting

#setting parameters
data = pd.DataFrame()
delay_tdma = []
datarate_list = []
packetsize = 150
buffersizes = range(1, 1000)
buffersize = 1000
arrivalRates = [1, 3, 5, 8]
arrivalRate = 8
path = [r1, r5]

plt.close('all')


#Examining queuing delay depending on arrival rate and buffer size

fig, (ax) = plt.subplots(1, 1)

for rate in arrivalRates:
    for i in buffersizes:
        delay = latency.calcLatenciesPath(path, rate, i, packetsize)
        datanew = pd.DataFrame.from_dict(
            {'Arrival rate': [rate], 'QueuingDelay': [delay[0] * (10 ** 3)], 'bufferSize': [i]})
        data = pd.concat([data, datanew], ignore_index=True)

ax = sns.lineplot(data=data, x='bufferSize', y='QueuingDelay', hue='Arrival rate', ax=ax, palette=mycolors, alpha=0.5)

ax.set_xlabel("Buffer size in number of packets")
ax.set_ylabel("Queuing delay in milliseconds")

ax.set_xscale('log')    #for better visibillity of initial behavior
ax.grid(True)

plt.show()


#Examining the transmission delay depending on data rate between node 5 and 0

datarate_r5 = np.arange(0.01, 500, 0.005)   #varying the link capacity between node 5 and 0

for datarate in datarate_r5:
    r5.setphysDataRate(datarate)
    delay_tdma.append(latency.calcLatenciesPath(path, arrivalRate, buffersize, packetsize)[1])
    datarate_list.append(datarate)

plt.plot(datarate_list, delay_tdma)
plt.xscale("log")   #for better visibillity of initial behavior

plt.xlabel("Data rate of the link in Mbit/s")
plt.ylabel("Transmission delay in seconds")
plt.grid(True)

plt.show()
