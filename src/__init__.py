"""
HDL Parser and Simulator Package

This package provides functionality to parse HDL files, simulate chip behavior,
and run tests against chip implementations.
"""

from .hdl_parser import HDLParser, Chip, ChipInstance, Connection, Pin, PinType
from .simulator import ChipSimulator
from .test_framework import TestFramework

__version__ = "1.0.0"
__all__ = [
    "HDLParser",
    "Chip",
    "ChipInstance", 
    "Connection",
    "Pin",
    "PinType",
    "ChipSimulator",
    "TestFramework"
] 