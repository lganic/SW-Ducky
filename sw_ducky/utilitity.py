from typing import List, Tuple

import math

def is_cord_valid(coord: Tuple[float, float]) -> bool:

    '''
    Determine if an X,Y coordinate contains NaNs or infs. 
    '''

    if math.isnan(coord[0]) or math.isinf(coord[0]):
        return False

    if math.isnan(coord[1]) or math.isinf(coord[1]):
        return False
    
    return True

def is_poly_valid(coords: List[Tuple[float, float]]) -> bool:

    '''
    Determine if a polygon of X,Y coordinates contains NaNs or infs. 
    '''

    for c in coords:

        if not is_cord_valid(c):
            return False
    
    return True

def line_from_quad(quad: Tuple[Tuple[float, float]]) -> List[Tuple[float, float]]:

    '''
    Given a quad, return two x, y coordinates which represent the line formed by that quad
    '''

    def avg_2_coords(coords):

        return ((coords[0][0] + coords[1][0]) / 2, (coords[0][1] + coords[1][1]) / 2)

    return [avg_2_coords(quad[0: 2]), avg_2_coords(quad[2: 4])]

def subtract(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:

    '''
    Subtract two points
    '''

    return (a[0] - b[0], a[1] - b[1])

def add(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:

    '''
    Add two points together
    '''

    return (a[0] + b[0], a[1] + b[1])

def dot(a: Tuple[float, float], b: Tuple[float, float]) -> float:

    '''
    Return the dot product of two points
    '''

    return a[0] * b[0] + a[1] * b[1]

def mag(a: Tuple[float, float]):

    '''
    Return the magnitude of a given point
    '''

    return math.sqrt(math.pow(a[0], 2), math.pow(a[1], 2))

def norm(a: Tuple[float, float]):

    '''
    Return the normalized representation of the vector
    '''

    vec_mag = mag(a)

    return (a[0] / vec_mag, a[1] / vec_mag)