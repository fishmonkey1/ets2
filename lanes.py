from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

import traceback

import pprint
pp = pprint.PrettyPrinter(depth=6)

midpoint = 515 # verify this

def lane_persistence():
    """
    Keeps track of similiar lines over time to create lookback window for lane lines.
    Also can be used to verify for dashed lanes. 
    """
    pass


def most_likely_lane_lines():
    """Tracks the two longest lines closest to camera midpoint, and distances from them."""