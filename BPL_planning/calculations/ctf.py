import math
import cmath
import numpy
import pandas as pd
from graphs import Node

calcGammaResult = None


def interpolate_gamma(cable_type, frequency_spectrum):
    cable_data_path = ''
    cable_data = pd.read_csv(cable_data_path)

    calcGammaResult = cable_data
    #calcGammaResult = interpolate(frequency_spectrum, cable_type)

    return calcGammaResult


def calculateGamma(cable_type=None, frequency_spectrum=None):

    """
    loads and calculates values for the propagation constant
    Providing an example bottom-up calculation from literature

    :param cable_type:
    :param frequency_spectrum:
    :return:
    """

    global calcGammaResult
    if calcGammaResult is not None:
        return calcGammaResult

    if frequency_spectrum is None:
        f_low = 1000000.0
        f_high = 30000000.0
        # n_freq_bands = 100000
        n_freq_bands = 917

        freq_spectrum = list()
        resolution = (f_high - f_low) / n_freq_bands
        center_freq = resolution / 2
        for i in range(n_freq_bands):
            freq_spectrum.append(f_low + center_freq + resolution * i)
        freq_spectrum = numpy.array(
            freq_spectrum)  # convert the list to an array for easier mathematical operations with numpy

    else:

        freq_spectrum = frequency_spectrum

    if cable_type is 'NAYY150':

        calcGammaResult = interpolate_gamma('NAYY150', frequency_spectrum)

    elif cable_type is 'NAYY35':

        calcGammaResult = interpolate_gamma('NAYY35', frequency_spectrum)

    else:
        # pre calc spectrum model from literature

        # constants
        eps_0 = 8.854188e-12
        mu_0 = 12.566371e-7
        rho = 2.82e-8
        NAYY150SE_radius = 13.82e-3
        NAYY150SE_conductor_distance = 3.6e-3

        eps_r = list()
        tand = list()
        C = list()
        L = list()
        v_ph = list()
        R = list()
        G = list()
        z_w = list()
        gamma = list()

        use_freq_constant_parameters = True
        for i in range(len(freq_spectrum)):
            if use_freq_constant_parameters:
                eps_r.append(4)
                tand.append(0.01)
            else:
                eps_r.append(7.95 - ((0.9 / math.log10(20)) * math.log10(freq_spectrum[
                                                                             i])))
                tand.append(0.2345 - ((0.04 / math.log10(20)) * math.log10(freq_spectrum[i])))  # tan loss angle
            C.append(2 * eps_0 * eps_r[i] * NAYY150SE_radius / NAYY150SE_conductor_distance)  # frequency dependent
            L.append(mu_0 * NAYY150SE_conductor_distance / (2 * NAYY150SE_radius))  # constant
            v_ph.append(1 / math.sqrt(L[i] * C[i]))  # phasengeschwindigkeit
            R.append(math.sqrt(rho * math.pi * mu_0 * freq_spectrum[i] / NAYY150SE_radius ** 2))
            G.append(2 * math.pi * freq_spectrum[i] * C[i] * tand[i])
            z_w.append(cmath.sqrt(complex(R[i], 2 * math.pi * freq_spectrum[i] * L[i]) / complex(G[i], 2 * math.pi *
                                                                                                 freq_spectrum[i] * C[
                                                                                                     i])))

            gamma.append(cmath.sqrt(complex(R[i], 2 * math.pi * freq_spectrum[i] * L[i]) * complex(G[i], 2 * math.pi *
                                                                                                   freq_spectrum[i] * C[
                                                                                                       i])))

        z_w = numpy.array(z_w)
        gamma = numpy.array(gamma)

        #optional adjustments of gamma for sensitivity analyses
        calcGammaResult = [z_w * 1.0, gamma * 1]
        p = 1
        calcGammaResult[0] *= p
        calcGammaResult[1] *= p

    return calcGammaResult


def calculateZSubst(endnode: Node, zWave: complex, gamma: list, length: float) -> list:
    zL = numpy.divide(1, sum(map(lambda edge: numpy.divide(1, edge.getZSubst()), endnode.energyEdgesOut),
                             numpy.divide(1, endnode.zShunt)))
    return calculateImpedanceTransformation(zWave, zL, gamma, length)


def calculateImpedanceTransformation(z_w, z_L, gamma, length):  # impedance transformation formula
    return numpy.multiply(z_w, numpy.divide((z_L + numpy.multiply(z_w, numpy.tanh(numpy.multiply(gamma, length)))),
                                            (z_w + numpy.multiply(z_L, numpy.tanh(numpy.multiply(gamma, length))))))

"""
def calculateCTF4(path: list) -> list:
    partCtfList: list = []
    currEdgeIndex: int = len(path) - 1
    currEndnode: Node = path[currEdgeIndex].endNode
    zIn = numpy.divide(1, sum(map(lambda edge: numpy.divide(1, edge.getZSubst()), currEndnode.energyEdgesOut),
                              numpy.divide(1, currEndnode.zShunt)))

    while currEdgeIndex >= 0:
        rho = (zIn - path[currEdgeIndex].zWave) / (zIn + path[currEdgeIndex].zWave)
        # be aware, the list fills in reverse order
        partCtfList.append((1 + rho) / (
                    numpy.exp(numpy.multiply(path[currEdgeIndex].gamma, path[currEdgeIndex].length)) + numpy.multiply(
                rho,
                numpy.exp(numpy.multiply(numpy.multiply(-1, path[currEdgeIndex].gamma), path[currEdgeIndex].length)))))

        currEdgeIndex = currEdgeIndex - 1
        currEndnode = path[currEdgeIndex].endNode

        # calculate next zIn
        zShunt = numpy.divide(1, sum(map(lambda edge: 1 / edge.getZSubst(), currEndnode.energyEdgesOut),
                                     1 / currEndnode.zShunt))
        rhoTemp = numpy.multiply(rho, numpy.exp(
            numpy.multiply(numpy.multiply(-2, path[currEdgeIndex].gamma), path[currEdgeIndex].length)))
        zIn = numpy.divide(1, (numpy.divide(1, (
            numpy.multiply(path[currEdgeIndex].zWave, ((1 + rhoTemp) / (1 - rhoTemp))))) + numpy.divide(1, zShunt)))

    return numpy.prod(partCtfList, axis=0)
"""
"""
def calculateCTF3(path: list) -> list:  # Richtige Version
    # print("test")
    partCtfList: list = []
    currEdgeIndex: int = len(path) - 1
    currEndnode: Node = path[currEdgeIndex].endNode

    energyEdgesOut = currEndnode.energyEdgesOut
    if currEdgeIndex < len(path) - 1:
        energyEdgesOut.remove(path[currEdgeIndex + 1])

    if len(currEndnode.energyEdgesOut) != 1:
        zIn = numpy.divide(1, sum(map(lambda edge: numpy.divide(1, edge.getZSubst()), energyEdgesOut),
                                  numpy.divide(1, currEndnode.zShunt)))
    else:
        zIn = numpy.divide(1, sum(map(lambda edge: numpy.divide(1, edge.getZSubst()), energyEdgesOut), 0))

    while currEdgeIndex >= 0:
        rho = (zIn - path[currEdgeIndex].zWave) / (zIn + path[currEdgeIndex].zWave)
        # be aware, the list fills in reverse order
        partCtfList.append((1 + rho) / (
                    numpy.exp(numpy.multiply(path[currEdgeIndex].gamma, path[currEdgeIndex].length)) + numpy.multiply(
                rho,
                numpy.exp(numpy.multiply(numpy.multiply(-1, path[currEdgeIndex].gamma), path[currEdgeIndex].length)))))

        currEdgeIndex = currEdgeIndex - 1
        currEndnode = path[currEdgeIndex].endNode

        energyEdgesOut = currEndnode.energyEdgesOut
        # print("E: ", energyEdgesOut)
        # print("P: ", path)
        # print("End: ", currEndnode.name)
        if currEdgeIndex < len(path) - 1 and currEdgeIndex >= 0:
            # print("jo")
            energyEdgesOut.remove(path[currEdgeIndex + 1])

        # calculate next zIn
        if len(currEndnode.energyEdgesOut) != 1:
            zShunt = numpy.divide(1,
                                  sum(map(lambda edge: 1 / edge.getZSubst(), energyEdgesOut), 1 / currEndnode.zShunt))
        else:
            zShunt = numpy.divide(1, sum(map(lambda edge: 1 / edge.getZSubst(), energyEdgesOut), 0))
        # print("Shunt: ", zShunt)
        rhoTemp = numpy.multiply(rho, numpy.exp(
            numpy.multiply(numpy.multiply(-2, path[currEdgeIndex].gamma), path[currEdgeIndex].length)))
        zIn = numpy.divide(1, (numpy.divide(1, (
            numpy.multiply(path[currEdgeIndex].zWave, ((1 + rhoTemp) / (1 - rhoTemp))))) + numpy.divide(1, zShunt)))

    return numpy.prod(partCtfList, axis=0)
"""

def calculateCTF(path: list) -> list:  # Richtige Version
    partCtfList: list = []
    currEdgeIndex: int = len(path) - 1
    currEndnode: Node = path[currEdgeIndex].endNode

    energyEdgesOut = currEndnode.energyEdgesOut
    if currEdgeIndex < len(path) - 1:
        energyEdgesOut.remove(path[currEdgeIndex + 1])

    zIn = numpy.divide(1, sum(map(lambda edge: numpy.divide(1, edge.getZSubst()), energyEdgesOut),
                              numpy.divide(1, currEndnode.zShunt)))  # UNTERSCHIED: KEIN IF

    while currEdgeIndex >= 0:
        rho = (zIn - path[currEdgeIndex].zWave) / (zIn + path[currEdgeIndex].zWave)
        # be aware, the list fills in reverse order
        partCtfList.append((1 + rho) / (
                    numpy.exp(numpy.multiply(path[currEdgeIndex].gamma, path[currEdgeIndex].length)) + numpy.multiply(
                rho,
                numpy.exp(numpy.multiply(numpy.multiply(-1, path[currEdgeIndex].gamma), path[currEdgeIndex].length)))))

        currEdgeIndex = currEdgeIndex - 1
        currEndnode = path[currEdgeIndex].endNode

        energyEdgesOut = currEndnode.energyEdgesOut.copy()  # UNTERSCHIED: COPY
        # print("E: ", energyEdgesOut)
        # print("P: ", path)
        # print("End: ", currEndnode.name)
        if currEdgeIndex < len(path) - 1 and currEdgeIndex >= 0:
            # print("jo")
            energyEdgesOut.remove(path[currEdgeIndex + 1])

        # calculate next zIn

        zShunt = numpy.divide(1, sum(map(lambda edge: 1 / edge.getZSubst(), energyEdgesOut),
                                     1 / currEndnode.zShunt))  # UNTERSCHIED: KEIN IF
        # print("Shunt: ", zShunt)
        rhoTemp = numpy.multiply(rho, numpy.exp(
            numpy.multiply(numpy.multiply(-2, path[currEdgeIndex].gamma), path[currEdgeIndex].length)))
        zIn = numpy.divide(1, (numpy.divide(1, (
            numpy.multiply(path[currEdgeIndex].zWave, ((1 + rhoTemp) / (1 - rhoTemp))))) + numpy.divide(1, zShunt)))
        # print("In: ", zIn)
        ret = numpy.prod(partCtfList, axis=0)
    return ret