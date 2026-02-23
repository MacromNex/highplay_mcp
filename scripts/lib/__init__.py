"""
Shared library for cyclic peptide MCP scripts.

This module contains common utilities extracted and simplified from the HighPlay repository
to minimize dependencies and provide self-contained functionality for MCP tools.
"""

from .molecules import *
from .io import *
from .validation import *
from .utils import *

__version__ = "1.0.0"
__author__ = "Extracted from HighPlay repository"