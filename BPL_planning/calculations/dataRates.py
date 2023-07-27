import math
import numpy as np
#from graphs.RoutingGraph import RoutingGraph
from graphs import RoutingEdge

def ofdmDataRate(snrs):

    """
    Adopting Effective SNR Mapping from our Data rate predictions in
    "Data Rate Prediction of Broadband Powerline Communication Based on Machine Learning", Lutat et al, PowerTech2023
    """
    datarate = 0
    num_carriers_meas  = 647

    for snr in snrs:
        snr = 10*np.log10(snr)
        if snr < 0:
            datarate += 0
        elif snr > 26:
            datarate += (2.97 * 26 + (17.42 - 3 * 2.97)) / num_carriers_meas # Y-Achsenabschnitt at 17.42dB -> assuming that 3dB difference to modem SNR in datarate paper
        else:
            datarate += (2.97 * snr + (17.42 - 3 * 2.97)) / num_carriers_meas

    return datarate

