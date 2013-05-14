"""
Bindings to the Apple System Log facility.
"""
from __future__ import absolute_import

__version__ = "0.9"

from ._asl import *
from ._constants import *

asl_open = aslclient
asl_new = aslmsg

def ASL_FILTER_MASK(level):
    return 1 << level

def ASL_FILTER_MASK_UPTO(level):
    return (1 << (level+1)) - 1
