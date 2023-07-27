import pandas as pd

from calculations import latency
from graphs.EnergyGraph import EnergyGraph
from graphs.RoutingGraph import RoutingGraph
from graphs.RoutingEdge import RoutingEdge
from graphs.Node import Node
from graphs.EnergyEdge import EnergyEdge
import matplotlib.pyplot as plt
import tikzplotlib

import math
import numpy as np

import seaborn as sns

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

arrivalRates = [20, 50, 80, 110]  # np.arange(0.5, 19, 0.5)
mycolorsr = ['#c7ddf2', '#8ebae5', '#407fb7', '#00549f', ]

mycolors = ['#00549f', '#407fb7', '#8ebae5', '#c7ddf2', ]

# mycolors = ['#cc071e','#407fb7', '#8ebae5', '#c7ddf2', ]
data = pd.DataFrame()
delay = []
delay2 = []
delay_tdma = []
buffer_list = []
packetsizes = range(1, 145888)
packetsize = 150
buffersizes = range(1, 1000)

path = [r1, r5]

arrivalRate = 8

buffersize = 1000
plt.close('all')

datarate_r5 = np.arange(0.01, 500, 0.01)
datarate_list = []

plt.close()

#for packetsize in packetsizes:
#    delay_tdma.append(latency.calcLatenciesPath(path, arrivalRate, buffersize, packetsize)[4])
#    datarate_list.append(packetsize)

#cm = 1/2.54
#fig = plt.figure(figsize=(14.8*cm, 6*cm))
#plt.plot(datarate_list, delay_tdma)






fig, (ax,ax2) = plt.subplots(1, 2)
fig, (ax) = plt.subplots(1, 1)

for Ankunftsrate in arrivalRates:
    for i in buffersizes:
        queue = latency.calcLatenciesPath(path, Ankunftsrate, i, packetsize)
        delay.append(queue[0])
        delay2.append(queue[4])
        buffer_list.append(i)
        datanew = pd.DataFrame.from_dict(
            {'Ankunftsrate': [Ankunftsrate], 'delay': [queue[0] * (10 ** 3)], 'delay2': [queue[4]* (10 ** 3)], 'buffer': [i]})
        data = pd.concat([data, datanew], ignore_index=True)

ax = sns.lineplot(data=data, x='buffer', y='delay', hue='Ankunftsrate', ax=ax, palette=mycolors, style='Ankunftsrate', alpha=0.5)


#ax.set_xscale('log')
# ax.set_yscale('log')

ax.set_xlabel("Buffer-Größe in Paketen")
ax.set_ylabel("Queuing Delay in ms")  # + u"\u03bcs" mikrosek

#ax2 = sns.lineplot(data=data, x='buffer', y='delay2', hue='Ankunftsrate', ax=ax2, palette=mycolors) #, style='Ankunftsrate', alpha=0.5)
#ax2.set_ylabel("End-to-end Delay in ms")  # + u"\u03bcs" mikrosek
#ax2.set_xlabel("Buffer-Größe in Pakete")
#ax2.set_xscale('log')


# plt.show()
plt.tight_layout()
#plt.savefig(f"")
# tikzplotlib.save(f"")
# plt.close()
fig2, ax2 = plt.subplots(1, 1)
# print(50*math.sqrt(3.1)/2.997992/(10**8))
# print(delay)

# plt.plot(buffer_list, delay)
# plt.plot(delay2, buffer_list)
#plt.xscale("log")
plt.xlabel("Paketgröße in Bytes")
plt.ylabel("Ende-zu-Ende-Latenz in Sekunden")       # + u"\u03bcs")

# plt.savefig(f"I:/j.girbig/plots/probe1.pdf")
# tikzplotlib.save(f"")
plt.savefig(f"")
#tikzplotlib.save(f"")
plt.show()
