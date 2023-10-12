__all__ = (
    "EXPONENTIAL",
    "LINEAR",
    "OSCILLATE",
)

import numpy as np

from .midi import *


def EXPONENTIAL(fac, t) -> float:
    """
    Exponential decay with factor ``fac`` (in units per second).
    """
    return np.exp(-fac * t)

def LINEAR(fac, t) -> float:
    """
    Linear decay with factor ``fac`` (in units per second).
    """
    return 1 - fac*t

def OSCILLATE(period, t) -> float:
    """
    Oscillate between -1 and 1 with period ``period`` (in seconds).
    When t=0, returns 1.
    """
    return np.cos(2*np.pi * t / period)
