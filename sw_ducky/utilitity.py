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