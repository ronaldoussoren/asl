"""
Bindings to the Apple System Log facility.
"""
from __future__ import absolute_import

from ._asl import *  # noqa: F403
from ._constants import *  # noqa: F403

__version__ = "1.0"


asl_open = aslclient  # noqa: F405
asl_new = aslmsg  # noqa: F405


def ASL_FILTER_MASK(level):
    return 1 << level


def ASL_FILTER_MASK_UPTO(level):
    return (1 << (level + 1)) - 1


LEVEL2STRING = {
    ASL_LEVEL_EMERG: ASL_STRING_EMERG,  # noqa: F405
    ASL_LEVEL_ALERT: ASL_STRING_ALERT,  # noqa: F405
    ASL_LEVEL_CRIT: ASL_STRING_CRIT,  # noqa: F405
    ASL_LEVEL_ERR: ASL_STRING_ERR,  # noqa: F405
    ASL_LEVEL_WARNING: ASL_STRING_WARNING,  # noqa: F405
    ASL_LEVEL_NOTICE: ASL_STRING_NOTICE,  # noqa: F405
    ASL_LEVEL_INFO: ASL_STRING_INFO,  # noqa: F405
    ASL_LEVEL_DEBUG: ASL_STRING_DEBUG,  # noqa: F405
}

STRING2LEVEL = {
    ASL_STRING_EMERG: ASL_LEVEL_EMERG,  # noqa: F405
    ASL_STRING_ALERT: ASL_LEVEL_ALERT,  # noqa: F405
    ASL_STRING_CRIT: ASL_LEVEL_CRIT,  # noqa: F405
    ASL_STRING_ERR: ASL_LEVEL_ERR,  # noqa: F405
    ASL_STRING_WARNING: ASL_LEVEL_WARNING,  # noqa: F405
    ASL_STRING_NOTICE: ASL_LEVEL_NOTICE,  # noqa: F405
    ASL_STRING_INFO: ASL_LEVEL_INFO,  # noqa: F405
    ASL_STRING_DEBUG: ASL_LEVEL_DEBUG,  # noqa: F405
}
