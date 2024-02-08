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