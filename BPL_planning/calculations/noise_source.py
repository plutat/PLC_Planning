import numpy

def set_noise_sources(routing_graph, rx, noise_sources=[], noise_Tx=0, noise_Rx=0, noise_Repeater=0):
    superimposedNoise = 0
    noise_dic = {"": 0}
    noise_dic["Tx"] = noise_Tx
    noise_dic["Rx"] = noise_Rx
    noise_dic["Repeater"] = noise_Repeater
    tx_psd = routing_graph.noisefloor()
    ctf_dic = routing_graph.ctf()
    for noise_node in noise_sources:
        path_ctf = ctf_dic[(rx, noise_node)]
        NoiseCTF = numpy.abs(path_ctf) ** 2
        try:
            noiseSourcePSD = noise_dic[noise_node.__busTypes[0]]
        except ValueError:
            print("no noise PSD has been defined for :", noise_node)
        superimposedNoise += (noiseSourcePSD * NoiseCTF)

    return superimposedNoise