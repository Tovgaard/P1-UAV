# Graph test
#%%
import numpy as np, matplotlib.pylab as plt

def choose_particle(particles):

    """
    Takes an array of particles and returns an element according to weights distribution
    input:
        - particles: array of particles
    output:
        - chosen particle
    """

    prob_distribution = []

    # calculates sum of weights to normalize wheight vector in next step

    sum_weights = 0
    for p in particles:
        sum_weights += p['weight']

    for p in particles:
        prob_distribution.append(float(p['weight'] / sum_weights))

    # choose particle according to weights distribution

    a = np.random.choice(particles, 1, replace=False, p=prob_distribution)

    return a[0]['value'][0]

def particle_filter(signal, quant_particles, A=1, H=1, Q=1.6, R=6):

    """
    Implementation of Particles filter.
    Takes a signal and filter parameters and return the filtered signal.
    input:
        - signal: signal to be filtered
        - quant_particles: filter parameter - quantity of particles
        - A, H, Q, R: kalman filter parameters
    output:
        - filtered signal
    """


    predicted_signal = []

    rang = 10                                                  # variation range of particles for initial step

    x = signal[0]                                              # takes first value as first filter prediction
    P = 0                                                      # set first covariance state value to zero

    predicted_signal.append(x)

    min_weight_to_consider = 0.07                              # defines some needed constants in algorithm
    min_weight_to_split_particle = 5

    for j, s in enumerate(signal[1:]):                         # iterates on the entire signal, except the first element

        range_ = [predicted_signal[j-1] - rang,
                  predicted_signal[j-1] + rang]                # set variation range for first step sampling

        particles = []

        for particle in range(quant_particles):                # loop on all particles

            input = np.random.uniform(range_[0], range_[1])    # sample particle value from variation range
            weight = 1 / np.abs(input-x)                       # particle weight

            if weight > min_weight_to_consider:                # it only iterates on particles which weights
                                                               # are greater than _min_weight_to_consider_

                x_, P = kalman_block(input, P, s, A, H, Q, R)  # calculates next state prediction

                weight = 1 / np.abs(s - x_)                    # prediction weight
                particles.append({'value': x_, 'weight': weight})

                # for particles with greater weights, it creates other particles in the 'neighborhood'

                if weight > min_weight_to_split_particle:

                    input = input + np.random.uniform(0, 5)
                    x_, P = kalman_block(input, P, s, A, H, Q, R)

                    weight = 1 / np.abs(s - x_)
                    particles.append({'value': x_, 'weight': weight})

        x = choose_particle(particles)                         # choose a particle, according to weight distribution

        predicted_signal.append(x)                             # update predicted signal with this step calculation

    return predicted_signal

def kalman_block(x, P, s, A, H, Q, R):

    """
    Prediction and update in Kalman filter
    input:
        - signal: signal to be filtered
        - x: previous mean state
        - P: previous variance state
        - s: current observation
        - A, H, Q, R: kalman filter parameters
    output:
        - x: mean state prediction
        - P: variance state prediction
    """

    # check laaraiedh2209 for further understand these equations

    x_mean = A * x + np.random.normal(0, Q, 1)
    P_mean = A * P * A + Q

    K = P_mean * H * (1 / (H * P_mean * H + R))
    x = x_mean + K * (s - H * x_mean)
    P = (1 - K * H) * P_mean

    return x, P

def kalman_filter(signal, A, H, Q, R):



    """
    Implementation of Kalman filter.
    Takes a signal and filter parameters and returns the filtered signal.
    input:
        - signal: signal to be filtered
        - A, H, Q, R: kalman filter parameters
    output:
        - filtered signal
    """

    predicted_signal = []

    x = signal[0]                                 # takes first value as first filter prediction
    P = 0                                         # set first covariance state value to zero

    predicted_signal.append(x)
    for j, s in enumerate(signal[1:]):            # iterates on the entire signal, except the first element

        x, P = kalman_block(x, P, s, A, H, Q, R)  # calculates next state prediction

        predicted_signal.append(x)                # update predicted signal with this step calculation

    return predicted_signal

data = [-65, -65, -64, -66, -63, -66, -63, -66, -66, -67, -61, -64, -59, -59, -59, -62, -60, -63, -60, -61, -59, -59, -59, -62, -63, -62, -58, -62, -61, -60]

kalman_data = kalman_filter(data, 1, 1, 0.01, 1)

#%%

print(f'Kalman data: {sum(kalman_data)/len(kalman_data)}')
print(f'Data: {sum(data)/len(data)}')


x = range(1, len(data)+1)

plt.plot(x, data, label='RSSI data')
plt.plot(x, kalman_data, label='Filtered RSSI data')
#plt.ylim(-80, -45)
plt.grid(linestyle=':')
plt.legend()
plt.show
# %%
