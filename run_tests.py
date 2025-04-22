#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Test Runner

This script runs all the unit tests for the gas fee prediction project.

Author: SRUJANJAINI
Date: April 2025
"""

import unittest
import os
import sys

def run_tests():
    """Run all tests in the tests directory."""
    # Add the project root to the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return success/failure
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    exit(run_tests())
