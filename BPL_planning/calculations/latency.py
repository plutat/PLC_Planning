import math
from graphs.Edge import Edge
from graphs.RoutingEdge import RoutingEdge
from graphs.Node import Node
import numpy as np
import decimal

def hochn(base, n):
    basen = base
    #base = decimal.Decimal(base)
    #for i in range(n):
    #    basen = basen * base
    return basen**n

def calculateLatenciesEdge(sendingNode: Node, currentEdge: RoutingEdge, arrivalRate: float, buffersize: int, packetsizeByte: int):

    epsilon_r = 3.1  # variabel 2.7 - 3.1
    t_slot = 0.00003584  # in sec
    ifg = 0.00009  # inter frame gap in sec
    alpha = 500
    beta = 12           #variabel [3, 6, 12]
    c_0 = 299792458
    pcf = 25 * (10 ** 6)

    packetsizeBits = packetsizeByte * 8
    serviceRate = currentEdge.physDataRate  # in MBits/sec
    trafficIntensity = decimal.Decimal(arrivalRate) / decimal.Decimal(serviceRate)
    if(trafficIntensity == 1):
        trafficIntensity = decimal.Decimal(1.0000000001)
    arrivalRatePackets = decimal.Decimal(arrivalRate * (10 ** 6)) / decimal.Decimal(packetsizeBits)  # 0.00111111  # 1 Paket/15 min
    t_send = packetsizeBits / (serviceRate * (10 ** 6))     # in sec
    numbOfTimeslots = math.ceil(t_send / t_slot)

    incomingEdges = sendingNode.routingEdgesIn  # numb of incoming edges
    numbIncEdges = len(incomingEdges)
    senderTDMA = 0

    if (numbIncEdges < 1):
        senderTDMA = 1
    else:
        for edge in incomingEdges:
            currentNode = edge.startNode
            if(currentNode.isSending):
                senderTDMA += 1

    energyEdgesTransm = currentEdge.energyEdges  # energy edges on which transmission takes place
    wire_length = 0
    for i in energyEdgesTransm:
        wire_length += i.length

    dprop = wire_length * math.sqrt(epsilon_r) / c_0

    #using data type decimal because the numbers get too large for float
    dqueue1_1 = trafficIntensity * (1 - hochn(trafficIntensity, (buffersize + 1)))
    dqueue1_2 = - (buffersize + 1) * hochn(trafficIntensity, (buffersize + 1)) * (1 - trafficIntensity)
    dqueueNenner = (arrivalRatePackets * (1 - trafficIntensity) * (1 - hochn(trafficIntensity, buffersize)))
    dqueueZaehler = dqueue1_1 + dqueue1_2

    dqueue_decimal = decimal.Decimal(dqueueZaehler) / decimal.Decimal(dqueueNenner)
    dqueue = float(dqueue_decimal)


    # asynchr. tdma
    dtransm = t_slot * (senderTDMA - 1) * (numbOfTimeslots - 0.5) + ifg * (senderTDMA * (numbOfTimeslots - 0.5)
                                                                              - 0.5) + t_send

    dproc = (alpha + packetsizeByte * beta) / pcf

    dend2end = dqueue + dtransm + dprop + dproc

    delays = np.array([dqueue, dtransm, dprop, dproc, dend2end])

    return delays


# path with RoutingEdges
def calcLatenciesPath(routingPath: list, sendingRate: float, buffersize: int, packetsize : int):
    delays_ges = np.array([0, 0, 0, 0, 0])

    arrivalRate = sendingRate

    for edge in routingPath:

        currNode = edge.startNode
        currDestNode = edge.endNode

        delays_ges = np.add(delays_ges, calculateLatenciesEdge(currNode, edge, arrivalRate, buffersize, packetsize))

        if edge.physDataRate < arrivalRate:
            arrivalRate = edge.physDataRate

        for parallelEdge in currDestNode.routingEdgesIn:
            if parallelEdge.startNode == currNode:
                continue
            if (parallelEdge.startNode).isSending:
                if parallelEdge.physDataRate < sendingRate:
                    arrivalRate += parallelEdge.physDataRate
                else:
                    arrivalRate += sendingRate



    #print(delays_ges)
    return delays_ges
