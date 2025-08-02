#!/usr/bin/env python3
"""
Test script to verify the execution capture bug fixes.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the advanced_animation directory to the path
sys.path.insert(0, str(Path(__file__).parent / "advanced_animation"))

from core.execution_capture import RuntimeStateCapture

def test_function_boundary_detection():
    """Test that the function boundary detection works correctly."""
    print("Testing function boundary detection...")
    
    # Test code that should not cause infinite recursion
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    result = fibonacci(5)
    print(f"Fibonacci(5) = {result}")

if __name__ == "__main__":
    main()
"""
    
    capture = RuntimeStateCapture()
    
    try:
        # This should not cause infinite recursion
        instrumented_code = capture._instrument_python_code(test_code)
        
        # Check that capture_state() calls are not inside the capture_state function
        lines = instrumented_code.split('\n')
        inside_capture_state = False
        capture_state_calls_inside_function = 0
        
        for line in lines:
            if line.strip().startswith('def capture_state'):
                inside_capture_state = True
            elif inside_capture_state:
                # Check if we've exited the function
                if line.strip() and len(line) - len(line.lstrip()) <= 0:
                    inside_capture_state = False
                elif 'capture_state()' in line and inside_capture_state:
                    capture_state_calls_inside_function += 1
        
        if capture_state_calls_inside_function == 0:
            print("✅ Function boundary detection: PASSED")
            return True
        else:
            print(f"❌ Function boundary detection: FAILED - Found {capture_state_calls_inside_function} capture_state() calls inside the function")
            return False
            
    except Exception as e:
        print(f"❌ Function boundary detection: FAILED - Exception: {e}")
        return False

def test_file_path_consistency():
    """Test that file paths are consistent between writing and reading."""
    print("Testing file path consistency...")
    
    # Check that the instrumented code writes to /tmp/execution_state.json
    test_code = "print('Hello, World!')"
    
    capture = RuntimeStateCapture()
    instrumented_code = capture._instrument_python_code(test_code)
    
    # Check that the file path is /tmp/execution_state.json
    if '/tmp/execution_state.json' in instrumented_code:
        print("✅ File path consistency: PASSED")
        return True
    else:
        print("❌ File path consistency: FAILED - Expected /tmp/execution_state.json")
        return False

def test_simulation_fallback():
    """Test that simulation fallback works when E2B is not available."""
    print("Testing simulation fallback...")
    
    test_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

result = factorial(5)
print(f"Factorial(5) = {result}")
"""
    
    capture = RuntimeStateCapture()
    
    try:
        # This should work even without E2B
        trace = capture.capture_execution(test_code, "python")
        
        if trace and len(trace.states) > 0:
            print(f"✅ Simulation fallback: PASSED - Generated {len(trace.states)} states")
            return True
        else:
            print("❌ Simulation fallback: FAILED - No states generated")
            return False
            
    except Exception as e:
        print(f"❌ Simulation fallback: FAILED - Exception: {e}")
        return False

def main():
    """Run all tests."""
    print("Running execution capture bug fix tests...\n")
    
    tests = [
        test_function_boundary_detection,
        test_file_path_consistency,
        test_simulation_fallback
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bug fixes are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please review the fixes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 