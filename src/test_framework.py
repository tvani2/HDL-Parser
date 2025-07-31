"""
Test Framework for HDL Chips

This module provides functionality to read test vectors and run tests
against chip simulators.
"""

from typing import Dict, List, Any
from .simulator import ChipSimulator


class TestFramework:
    """
    Framework for testing chips using test vectors.
    
    This class can read test vectors from files and run tests
    against chip simulators, producing detailed reports.
    """
    
    def __init__(self, simulator: ChipSimulator):
        """
        Initialize the test framework.
        
        Args:
            simulator: ChipSimulator instance to use for testing
        """
        self.simulator = simulator
    
    def run_tests_from_file(self, chip_name: str, test_file_path: str) -> Dict[str, Any]:
        """
        Run tests for a chip using test vectors from a file.
        
        Args:
            chip_name: Name of the chip to test
            test_file_path: Path to the test vector file
            
        Returns:
            Dictionary containing test results and summary
        """
        test_vectors = self._read_test_vectors(test_file_path)
        return self._run_tests(chip_name, test_vectors)
    
    def _read_test_vectors(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Read test vectors from a CSV-style file.
        
        Expected format:
        a,b; out
        0,0; 0
        0,1; 0
        1,0; 0
        1,1; 1
        
        Args:
            file_path: Path to the test vector file
            
        Returns:
            List of test vectors as dictionaries
        """
        test_vectors = []
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        if len(lines) < 2:
            raise ValueError("Test file must have at least a header and one test case")
        
        # Parse header line
        header_line = lines[0].strip()
        input_output_parts = header_line.split(';')
        
        if len(input_output_parts) != 2:
            raise ValueError("Header must be in format 'inputs; outputs'")
        
        input_names = [name.strip() for name in input_output_parts[0].split(',')]
        output_names = [name.strip() for name in input_output_parts[1].split(',')]
        
        # Parse test cases
        for line_num, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(';')
            if len(parts) != 2:
                raise ValueError(f"Invalid test case format at line {line_num}: {line}")
            
            # Parse inputs
            input_values = [int(val.strip()) for val in parts[0].split(',')]
            if len(input_values) != len(input_names):
                raise ValueError(f"Mismatch in input count at line {line_num}")
            
            # Parse expected outputs
            expected_outputs = [int(val.strip()) for val in parts[1].split(',')]
            if len(expected_outputs) != len(output_names):
                raise ValueError(f"Mismatch in output count at line {line_num}")
            
            # Create test vector
            test_vector = {
                'inputs': dict(zip(input_names, input_values)),
                'expected_outputs': dict(zip(output_names, expected_outputs)),
                'line_number': line_num
            }
            test_vectors.append(test_vector)
        
        return test_vectors
    
    def _run_tests(self, chip_name: str, test_vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run tests for a chip using the provided test vectors.
        
        Args:
            chip_name: Name of the chip to test
            test_vectors: List of test vectors
            
        Returns:
            Dictionary containing test results and summary
        """
        results = []
        passed = 0
        failed = 0
        
        for test_vector in test_vectors:
            test_result = self._run_single_test(chip_name, test_vector)
            results.append(test_result)
            
            if test_result['passed']:
                passed += 1
            else:
                failed += 1
        
        return {
            'chip_name': chip_name,
            'total_tests': len(test_vectors),
            'passed': passed,
            'failed': failed,
            'results': results
        }
    
    def _run_single_test(self, chip_name: str, test_vector: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            chip_name: Name of the chip to test
            test_vector: Test vector containing inputs and expected outputs
            
        Returns:
            Dictionary containing test result details
        """
        inputs = test_vector['inputs']
        expected_outputs = test_vector['expected_outputs']
        
        try:
            actual_outputs = self.simulator.simulate_chip(chip_name, inputs)
            
            # Compare actual vs expected outputs
            passed = True
            mismatches = []
            
            for output_name, expected_value in expected_outputs.items():
                actual_value = actual_outputs.get(output_name, 0)
                if actual_value != expected_value:
                    passed = False
                    mismatches.append({
                        'output': output_name,
                        'expected': expected_value,
                        'actual': actual_value
                    })
            
            return {
                'line_number': test_vector['line_number'],
                'inputs': inputs,
                'expected_outputs': expected_outputs,
                'actual_outputs': actual_outputs,
                'passed': passed,
                'mismatches': mismatches
            }
            
        except Exception as e:
            return {
                'line_number': test_vector['line_number'],
                'inputs': inputs,
                'expected_outputs': expected_outputs,
                'actual_outputs': None,
                'passed': False,
                'error': str(e)
            }
    
    def print_test_report(self, test_results: Dict[str, Any]):
        """
        Print a detailed test report.
        
        Args:
            test_results: Results from run_tests or run_tests_from_file
        """
        print(f"\n=== Test Report for {test_results['chip_name']} ===")
        print(f"Total Tests: {test_results['total_tests']}")
        print(f"Passed: {test_results['passed']}")
        print(f"Failed: {test_results['failed']}")
        print(f"Success Rate: {(test_results['passed'] / test_results['total_tests'] * 100):.1f}%")
        
        if test_results['failed'] > 0:
            print("\n=== Failed Tests ===")
            for result in test_results['results']:
                if not result['passed']:
                    print(f"\nTest Case (Line {result['line_number']}):")
                    print(f"  Inputs: {result['inputs']}")
                    print(f"  Expected: {result['expected_outputs']}")
                    
                    if 'error' in result:
                        print(f"  Error: {result['error']}")
                    else:
                        print(f"  Actual: {result['actual_outputs']}")
                        if result['mismatches']:
                            print("  Mismatches:")
                            for mismatch in result['mismatches']:
                                print(f"    {mismatch['output']}: expected {mismatch['expected']}, got {mismatch['actual']}")
        
        print("\n=== Summary ===")
        print(f"{test_results['passed']} out of {test_results['total_tests']} tests passed")
        
        if test_results['failed'] == 0:
            print("🎉 All tests passed!")
        else:
            print(f"❌ {test_results['failed']} test(s) failed") 