"""
Unit tests for HDL Parser and Simulator

This module contains comprehensive unit tests for all components
of the HDL parser and simulator system.
"""

import unittest
import tempfile
import os

# Import the modules to test
from src.hdl_parser import HDLParser
from src.simulator import ChipSimulator
from src.test_framework import TestFramework


class TestHDLParser(unittest.TestCase):
    """Test cases for the HDL Parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = HDLParser()
    
    def test_builtin_chips_loaded(self):
        """Test that built-in chips are properly loaded"""
        builtin_chips = ['Nand', 'Not', 'And', 'Or']
        for chip_name in builtin_chips:
            chip = self.parser.get_chip(chip_name)
            self.assertIsNotNone(chip)
            self.assertTrue(chip.is_builtin)
            self.assertEqual(chip.name, chip_name)
    
    def test_parse_simple_chip(self):
        """Test parsing a simple chip definition"""
        hdl_content = """
        CHIP TestChip {
            IN a, b;
            OUT out;
            
            PARTS:
            And(a=a, b=b, out=out);
        }
        """
        
        chip = self.parser.parse_content(hdl_content)
        self.assertEqual(chip.name, "TestChip")
        self.assertEqual(chip.inputs, ["a", "b"])
        self.assertEqual(chip.outputs, ["out"])
        self.assertEqual(len(chip.parts), 1)
        self.assertFalse(chip.is_builtin)
        
        part = chip.parts[0]
        self.assertEqual(part.chip_name, "And")
        self.assertEqual(part.instance_name, "And")
        self.assertEqual(len(part.connections), 3)
    
    def test_parse_chip_with_multiple_parts(self):
        """Test parsing a chip with multiple parts"""
        hdl_content = """
        CHIP ComplexChip {
            IN a, b, c;
            OUT out1, out2;
            
            PARTS:
            And(a=a, b=b, out=temp1);
            Or(a=temp1, b=c, out=out1);
            Not(in=a, out=out2);
        }
        """
        
        chip = self.parser.parse_content(hdl_content)
        self.assertEqual(chip.name, "ComplexChip")
        self.assertEqual(chip.inputs, ["a", "b", "c"])
        self.assertEqual(chip.outputs, ["out1", "out2"])
        self.assertEqual(len(chip.parts), 3)
    
    def test_parse_connections(self):
        """Test parsing chip connections"""
        connection_str = "a=input1, b=input2, out=output1"
        connections = self.parser._parse_connections(connection_str)
        
        self.assertEqual(len(connections), 3)
        
        # Check specific connections
        connection_dict = {conn.to_pin: conn.from_pin for conn in connections}
        self.assertEqual(connection_dict['a'], 'input1')
        self.assertEqual(connection_dict['b'], 'input2')
        self.assertEqual(connection_dict['out'], 'output1')
    
    def test_is_builtin(self):
        """Test built-in chip detection"""
        self.assertTrue(self.parser.is_builtin('And'))
        self.assertTrue(self.parser.is_builtin('Or'))
        self.assertTrue(self.parser.is_builtin('Not'))
        self.assertTrue(self.parser.is_builtin('Nand'))
        self.assertFalse(self.parser.is_builtin('UnknownChip'))


class TestChipSimulator(unittest.TestCase):
    """Test cases for the Chip Simulator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = HDLParser()
        self.simulator = ChipSimulator(self.parser)
    
    def test_builtin_and_logic(self):
        """Test AND gate logic"""
        inputs = {'a': 0, 'b': 0}
        outputs = self.simulator.simulate_chip('And', inputs)
        self.assertEqual(outputs['out'], 0)
        
        inputs = {'a': 1, 'b': 1}
        outputs = self.simulator.simulate_chip('And', inputs)
        self.assertEqual(outputs['out'], 1)
        
        inputs = {'a': 1, 'b': 0}
        outputs = self.simulator.simulate_chip('And', inputs)
        self.assertEqual(outputs['out'], 0)
    
    def test_builtin_or_logic(self):
        """Test OR gate logic"""
        inputs = {'a': 0, 'b': 0}
        outputs = self.simulator.simulate_chip('Or', inputs)
        self.assertEqual(outputs['out'], 0)
        
        inputs = {'a': 1, 'b': 0}
        outputs = self.simulator.simulate_chip('Or', inputs)
        self.assertEqual(outputs['out'], 1)
        
        inputs = {'a': 1, 'b': 1}
        outputs = self.simulator.simulate_chip('Or', inputs)
        self.assertEqual(outputs['out'], 1)
    
    def test_builtin_not_logic(self):
        """Test NOT gate logic"""
        inputs = {'in': 0}
        outputs = self.simulator.simulate_chip('Not', inputs)
        self.assertEqual(outputs['out'], 1)
        
        inputs = {'in': 1}
        outputs = self.simulator.simulate_chip('Not', inputs)
        self.assertEqual(outputs['out'], 0)
    
    def test_builtin_nand_logic(self):
        """Test NAND gate logic"""
        inputs = {'a': 0, 'b': 0}
        outputs = self.simulator.simulate_chip('Nand', inputs)
        self.assertEqual(outputs['out'], 1)
        
        inputs = {'a': 1, 'b': 1}
        outputs = self.simulator.simulate_chip('Nand', inputs)
        self.assertEqual(outputs['out'], 0)
    
    def test_composite_chip_simulation(self):
        """Test simulation of a composite chip"""
        # Create a simple composite chip
        hdl_content = """
        CHIP TestChip {
            IN a, b;
            OUT out;
            
            PARTS:
            And(a=a, b=b, out=temp);
            Not(in=temp, out=out);
        }
        """
        
        # Parse the chip (stored for potential future use)
        _ = self.parser.parse_content(hdl_content)
        
        # Test NAND behavior (AND followed by NOT)
        inputs = {'a': 0, 'b': 0}
        outputs = self.simulator.simulate_chip('TestChip', inputs)
        self.assertEqual(outputs['out'], 1)  # NAND of 0,0 = 1
        
        inputs = {'a': 1, 'b': 1}
        outputs = self.simulator.simulate_chip('TestChip', inputs)
        self.assertEqual(outputs['out'], 0)  # NAND of 1,1 = 0


class TestTestFramework(unittest.TestCase):
    """Test cases for the Test Framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = HDLParser()
        self.simulator = ChipSimulator(self.parser)
        self.test_framework = TestFramework(self.simulator)
    
    def test_read_test_vectors(self):
        """Test reading test vectors from a file"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("a,b; out\n")
            f.write("0,0; 0\n")
            f.write("0,1; 0\n")
            f.write("1,0; 0\n")
            f.write("1,1; 1\n")
            test_file = f.name
        
        try:
            test_vectors = self.test_framework._read_test_vectors(test_file)
            self.assertEqual(len(test_vectors), 4)
            
            # Check first test vector
            first_vector = test_vectors[0]
            self.assertEqual(first_vector['inputs'], {'a': 0, 'b': 0})
            self.assertEqual(first_vector['expected_outputs'], {'out': 0})
            
            # Check last test vector
            last_vector = test_vectors[3]
            self.assertEqual(last_vector['inputs'], {'a': 1, 'b': 1})
            self.assertEqual(last_vector['expected_outputs'], {'out': 1})
            
        finally:
            os.unlink(test_file)
    
    def test_run_tests(self):
        """Test running tests with test vectors"""
        test_vectors = [
            {
                'inputs': {'a': 0, 'b': 0},
                'expected_outputs': {'out': 0},
                'line_number': 2
            },
            {
                'inputs': {'a': 1, 'b': 1},
                'expected_outputs': {'out': 1},
                'line_number': 5
            }
        ]
        
        results = self.test_framework._run_tests('And', test_vectors)
        self.assertEqual(results['chip_name'], 'And')
        self.assertEqual(results['total_tests'], 2)
        self.assertEqual(results['passed'], 2)
        self.assertEqual(results['failed'], 0)
    
    def test_run_tests_with_failures(self):
        """Test running tests that include failures"""
        test_vectors = [
            {
                'inputs': {'a': 0, 'b': 0},
                'expected_outputs': {'out': 0},
                'line_number': 2
            },
            {
                'inputs': {'a': 1, 'b': 1},
                'expected_outputs': {'out': 0},  # Wrong expectation
                'line_number': 5
            }
        ]
        
        results = self.test_framework._run_tests('And', test_vectors)
        self.assertEqual(results['total_tests'], 2)
        self.assertEqual(results['passed'], 1)
        self.assertEqual(results['failed'], 1)
        
        # Check that the failure is properly recorded
        failed_result = results['results'][1]
        self.assertFalse(failed_result['passed'])
        self.assertEqual(len(failed_result['mismatches']), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = HDLParser()
        self.simulator = ChipSimulator(self.parser)
        self.test_framework = TestFramework(self.simulator)
    
    def test_complete_workflow(self):
        """Test the complete workflow from HDL parsing to testing"""
        # Create a test chip HDL file
        hdl_content = """
        CHIP TestChip {
            IN a, b;
            OUT out;
            
            PARTS:
            And(a=a, b=b, out=out);
        }
        """
        
        # Parse the chip
        chip = self.parser.parse_content(hdl_content)
        self.assertEqual(chip.name, "TestChip")
        
        # Test the chip directly
        inputs = {'a': 1, 'b': 1}
        outputs = self.simulator.simulate_chip('TestChip', inputs)
        self.assertEqual(outputs['out'], 1)
        
        # Create test vectors
        test_vectors = [
            {
                'inputs': {'a': 0, 'b': 0},
                'expected_outputs': {'out': 0},
                'line_number': 2
            },
            {
                'inputs': {'a': 1, 'b': 1},
                'expected_outputs': {'out': 1},
                'line_number': 3
            }
        ]
        
        # Run tests
        results = self.test_framework._run_tests('TestChip', test_vectors)
        self.assertEqual(results['passed'], 2)
        self.assertEqual(results['failed'], 0)


if __name__ == '__main__':
    unittest.main() 