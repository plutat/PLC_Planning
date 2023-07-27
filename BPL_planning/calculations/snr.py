import numpy

def calculateSNR(ctfList: list, noisefloor: float, txPsd: float) -> list:
    rxPsd = txPsd * (numpy.abs(ctfList) ** 2)
    snrList = numpy.array(rxPsd) / numpy.array(noisefloor)
    return snrList