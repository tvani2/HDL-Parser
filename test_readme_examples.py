#!/usr/bin/env python3
"""
Test script to verify all complex examples in README actually work
"""

import sys
sys.path.append('.')

from src.hdl_parser import HDLParser
from src.simulator import ChipSimulator
from src.test_framework import TestFramework


def test_example_1_multi_part_chip():
    """Test Example 1: Multi-Part Chip with Internal Signals"""
    print("Testing Example 1: Multi-Part Chip with Internal Signals...")
    
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    # Complex chip with multiple parts and internal signals
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
    
    # Parse the complex chip
    chip = parser.parse_content(hdl_content)
    print(f"  Chip: {chip.name}")
    print(f"  Inputs: {chip.inputs}")
    print(f"  Outputs: {chip.outputs}")
    print(f"  Parts: {len(chip.parts)}")
    
    # Simulate with complex inputs
    inputs = {'a': 1, 'b': 0, 'c': 1}
    outputs = simulator.simulate_chip('ComplexChip', inputs)
    print(f"  Outputs: {outputs}")
    
    # Verify expected behavior
    assert outputs['out1'] == 1, f"Expected out1=1, got {outputs['out1']}"
    assert outputs['out2'] == 0, f"Expected out2=0, got {outputs['out2']}"
    print("  ✅ Example 1 PASSED")


def test_example_2_composite_chip():
    """Test Example 2: Composite Chip Simulation (NAND from AND + NOT)"""
    print("Testing Example 2: Composite Chip Simulation...")
    
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    # Create NAND gate from AND + NOT
    hdl_content = """
    CHIP TestChip {
        IN a, b;
        OUT out;
        
        PARTS:
        And(a=a, b=b, out=temp);
        Not(in=temp, out=out);
    }
    """
    
    # Parse and test NAND behavior
    chip = parser.parse_content(hdl_content)
    
    # Test NAND logic
    inputs = {'a': 0, 'b': 0}
    outputs = simulator.simulate_chip('TestChip', inputs)
    assert outputs['out'] == 1, f"NAND(0,0) should be 1, got {outputs['out']}"
    print(f"  NAND(0,0) = {outputs['out']} ✅")
    
    inputs = {'a': 1, 'b': 1}
    outputs = simulator.simulate_chip('TestChip', inputs)
    assert outputs['out'] == 0, f"NAND(1,1) should be 0, got {outputs['out']}"
    print(f"  NAND(1,1) = {outputs['out']} ✅")
    
    print("  ✅ Example 2 PASSED")


def test_example_3_connection_parsing():
    """Test Example 3: Connection Parsing and Signal Propagation"""
    print("Testing Example 3: Connection Parsing...")
    
    parser = HDLParser()
    
    # Test complex connection parsing
    connection_str = "a=input1, b=input2, out=output1"
    connections = parser._parse_connections(connection_str)
    
    # Verify connections are correctly parsed
    connection_dict = {conn.to_pin: conn.from_pin for conn in connections}
    expected = {'a': 'input1', 'b': 'input2', 'out': 'output1'}
    
    for pin, signal in expected.items():
        assert connection_dict[pin] == signal, f"Expected {pin}={signal}, got {connection_dict[pin]}"
        print(f"  {signal} -> {pin} ✅")
    
    print("  ✅ Example 3 PASSED")


def test_example_4_real_hdl_files():
    """Test Example 4: Complete Workflow with Real HDL Files"""
    print("Testing Example 4: Real HDL Files...")
    
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    # Parse real Xor.hdl file
    with open('chips/Xor.hdl', 'r') as f:
        hdl_content = f.read()
    
    chip = parser.parse_content(hdl_content)
    print(f"  Parsed {chip.name} with {len(chip.parts)} parts")
    
    # Test all possible inputs
    test_cases = [
        ({'a': 0, 'b': 0}, 0),
        ({'a': 0, 'b': 1}, 1), 
        ({'a': 1, 'b': 0}, 1),
        ({'a': 1, 'b': 1}, 0)
    ]
    
    for inputs, expected in test_cases:
        outputs = simulator.simulate_chip('Xor', inputs)
        actual = outputs['out']
        status = "✅" if actual == expected else "❌"
        print(f"  {status} Xor{inputs}: expected {expected}, got {actual}")
        assert actual == expected, f"Xor{inputs}: expected {expected}, got {actual}"
    
    print("  ✅ Example 4 PASSED")


def test_example_5_advanced_testing():
    """Test Example 5: Advanced Testing Capabilities"""
    print("Testing Example 5: Advanced Testing...")
    
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    test_framework = TestFramework(simulator)
    
    # Test with incorrect expectations
    test_vectors = [
        {'inputs': {'a': 1, 'b': 1}, 'expected_outputs': {'out': 0}, 'line_number': 2}  # Wrong expectation
    ]
    
    results = test_framework._run_tests('And', test_vectors)
    print(f"  Tests: {results['total_tests']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    
    # Should have 1 failure (And(1,1) = 1, but expected 0 is wrong)
    assert results['total_tests'] == 1, f"Expected 1 test, got {results['total_tests']}"
    assert results['failed'] == 1, f"Expected 1 failure, got {results['failed']}"
    
    # Check detailed failure information
    failed_result = results['results'][0]
    print(f"  Mismatches: {failed_result['mismatches']}")
    
    print("  ✅ Example 5 PASSED")


def main():
    """Run all README example tests"""
    print("=== Testing README Examples ===\n")
    
    try:
        test_example_1_multi_part_chip()
        print()
        test_example_2_composite_chip()
        print()
        test_example_3_connection_parsing()
        print()
        test_example_4_real_hdl_files()
        print()
        test_example_5_advanced_testing()
        
        print("\n🎉 ALL README EXAMPLES WORK CORRECTLY!")
        print("✅ All complex parsing examples in README are verified and functional")
        
    except Exception as e:
        print(f"\n❌ README EXAMPLE FAILED: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main() 