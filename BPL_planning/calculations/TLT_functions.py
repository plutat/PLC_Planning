import numpy


def calculate_impedance_transformation(z_w, z_L, gamma, length):  # impedance transformation formula

    return numpy.multiply(z_w, numpy.divide((z_L + numpy.multiply(z_w, numpy.tanh(gamma * length))), (z_w + numpy.multiply(z_L, numpy.tanh(gamma * length)))))

def calculate_r_i_plus_one(load_impedance, wave_impedance):  # reflection factor at the load side
    return (load_impedance - wave_impedance) / (load_impedance + wave_impedance)


def calculate_h_i(r_i_plus_one, gamma_i, length_i):

    return (1 + r_i_plus_one) / (numpy.exp(gamma_i * length_i) + r_i_plus_one*numpy.exp(-gamma_i * length_i))