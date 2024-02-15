import numpy
import math

def cartesian_distance(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance

def spherical_distance(point1, point2):
    r1, az1, el1 = point1
    r2, az2, el2 = point2

    delta_theta = az2 - az1

    d = math.sqrt(
        r1**2 + r2**2 - 2*r1*r2*(math.sin(el1)*math.sin(el2)*math.cos(delta_theta) + math.cos(el1)*math.cos(el2))
    )

    return d

rir_delay.spherical_distance(m1_coords, m2_coords)
m1_coords = [0.042, 45, 35]
m2_coords = [0.042, -45, -35]
m3_coords = [0.042, 135, -35]
m4_coords = [0.042, -135, 35]

mic_coords = [m1_coords, m2_coords, m3_coords, m4_coords]

def distance_to_seconds(distance):
    '''
    compute the time it takes sound to travel
    a distance in seconds
    '''
    #CODE HERE
    seconds = distance/330
    return seconds

def shift_ir(ir, delay):
    '''
    takes an IR and shifts it a certain number
    of samples based on argument 'delay'
    '''
    #CODE
    
     if delay < 0:
        raise ValueError("Delay should be a non-negative integer.")
    if not ir:
        raise ValueError("Input IR should not be empty.")
    shifted_ir = np.concatenate((np.zeros(delay), ir[:-delay]))
    return shifted_ir

def spatial_rir(mono_ir, sr, mic_positions, source_position):
    # Function to create a spatial RIR from a mono-channel IR

    # Number of microphones
    num_mics = len(mic_positions)

    # Compute distances between the source and each microphone
    distances = [cartesian_distance(source_position, mic_pos) for mic_pos in mic_positions]

    # Convert distances to delays (in samples)
    speed_of_sound = 343  # Speed of sound in meters per second
    delays = [int(np.round(dist / speed_of_sound * sr)) for dist in distances]

    # Apply delays to the mono-channel IR
    delayed_ir = [shift_ir(mono_ir, delay) for delay in delays]

    # Concatenate delayed IRs into a multi-channel signal
    spatial_rir = np.vstack(delayed_ir)

    return spatial_rir

# Load mono-channel IR and sample rate
mono_ir, sr = lr.load("mono_ir.wav")

# Define microphone positions and source position (example source - NOT SURE HOW TO EXTRACT THIS!)
#mic_positions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]])
source_position = np.array([2, 2, 2])

# Create spatial RIR
spatial_rir_result = spatial_rir(mono_ir, sr, mic_coords, source_position)

# Plot and listen to the spatial RIR
plt.figure(figsize=(10, 6))
plt.imshow(spatial_rir_result, aspect='auto', cmap='viridis')
plt.title('Spatial RIR')
plt.xlabel('Time (samples)')
plt.ylabel('Microphone Index')
plt.colorbar(label='Amplitude')
plt.show()

# Play the spatial RIR
Audio(data=np.sum(spatial_rir_result, axis=0), rate=sr)
