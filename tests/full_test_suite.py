"""
Comprehensive test suite for HDL Parser and Simulator

This module contains comprehensive tests for all components
of the HDL parser and simulator system using regular assert statements.
"""

import tempfile
import os

# Import the modules to test
from src.hdl_parser import HDLParser
from src.simulator import ChipSimulator
from src.test_framework import TestFramework


def test_builtin_chips_loaded():
    """Test that built-in chips are properly loaded"""
    parser = HDLParser()
    builtin_chips = ['Nand', 'Not', 'And', 'Or']
    for chip_name in builtin_chips:
        chip = parser.get_chip(chip_name)
        assert chip is not None
        assert chip.is_builtin
        assert chip.name == chip_name


def test_parse_simple_chip():
    """Test parsing a simple chip definition"""
    parser = HDLParser()
    hdl_content = """
    CHIP TestChip {
        IN a, b;
        OUT out;
        
        PARTS:
        And(a=a, b=b, out=out);
    }
    """
    
    chip = parser.parse_content(hdl_content)
    assert chip.name == "TestChip"
    assert chip.inputs == ["a", "b"]
    assert chip.outputs == ["out"]
    assert len(chip.parts) == 1
    assert not chip.is_builtin
    
    part = chip.parts[0]
    assert part.chip_name == "And"
    assert part.instance_name == "And"
    assert len(part.connections) == 3


def test_parse_chip_with_multiple_parts():
    """Test parsing a chip with multiple parts"""
    parser = HDLParser()
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
    
    chip = parser.parse_content(hdl_content)
    assert chip.name == "ComplexChip"
    assert chip.inputs == ["a", "b", "c"]
    assert chip.outputs == ["out1", "out2"]
    assert len(chip.parts) == 3


def test_parse_connections():
    """Test parsing chip connections"""
    parser = HDLParser()
    connection_str = "a=input1, b=input2, out=output1"
    connections = parser._parse_connections(connection_str)
    
    assert len(connections) == 3
    
    # Check specific connections
    connection_dict = {conn.to_pin: conn.from_pin for conn in connections}
    assert connection_dict['a'] == 'input1'
    assert connection_dict['b'] == 'input2'
    assert connection_dict['out'] == 'output1'


def test_is_builtin():
    """Test built-in chip detection"""
    parser = HDLParser()
    assert parser.is_builtin('And')
    assert parser.is_builtin('Or')
    assert parser.is_builtin('Not')
    assert parser.is_builtin('Nand')
    assert not parser.is_builtin('UnknownChip')


def test_builtin_and_logic():
    """Test AND gate logic"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    inputs = {'a': 0, 'b': 0}
    outputs = simulator.simulate_chip('And', inputs)
    assert outputs['out'] == 0
    
    inputs = {'a': 1, 'b': 1}
    outputs = simulator.simulate_chip('And', inputs)
    assert outputs['out'] == 1
    
    inputs = {'a': 1, 'b': 0}
    outputs = simulator.simulate_chip('And', inputs)
    assert outputs['out'] == 0


def test_builtin_or_logic():
    """Test OR gate logic"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    inputs = {'a': 0, 'b': 0}
    outputs = simulator.simulate_chip('Or', inputs)
    assert outputs['out'] == 0
    
    inputs = {'a': 1, 'b': 0}
    outputs = simulator.simulate_chip('Or', inputs)
    assert outputs['out'] == 1
    
    inputs = {'a': 1, 'b': 1}
    outputs = simulator.simulate_chip('Or', inputs)
    assert outputs['out'] == 1


def test_builtin_not_logic():
    """Test NOT gate logic"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    inputs = {'in': 0}
    outputs = simulator.simulate_chip('Not', inputs)
    assert outputs['out'] == 1
    
    inputs = {'in': 1}
    outputs = simulator.simulate_chip('Not', inputs)
    assert outputs['out'] == 0


def test_builtin_nand_logic():
    """Test NAND gate logic"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    inputs = {'a': 0, 'b': 0}
    outputs = simulator.simulate_chip('Nand', inputs)
    assert outputs['out'] == 1
    
    inputs = {'a': 1, 'b': 1}
    outputs = simulator.simulate_chip('Nand', inputs)
    assert outputs['out'] == 0


def test_composite_chip_simulation():
    """Test simulation of a composite chip"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
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
    _ = parser.parse_content(hdl_content)
    
    # Test NAND behavior (AND followed by NOT)
    inputs = {'a': 0, 'b': 0}
    outputs = simulator.simulate_chip('TestChip', inputs)
    assert outputs['out'] == 1  # NAND of 0,0 = 1
    
    inputs = {'a': 1, 'b': 1}
    outputs = simulator.simulate_chip('TestChip', inputs)
    assert outputs['out'] == 0  # NAND of 1,1 = 0


def test_read_test_vectors():
    """Test reading test vectors from a file"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    test_framework = TestFramework(simulator)
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("a,b; out\n")
        f.write("0,0; 0\n")
        f.write("0,1; 0\n")
        f.write("1,0; 0\n")
        f.write("1,1; 1\n")
        test_file = f.name
    
    try:
        test_vectors = test_framework._read_test_vectors(test_file)
        assert len(test_vectors) == 4
        
        # Check first test vector
        first_vector = test_vectors[0]
        assert first_vector['inputs'] == {'a': 0, 'b': 0}
        assert first_vector['expected_outputs'] == {'out': 0}
        
        # Check last test vector
        last_vector = test_vectors[3]
        assert last_vector['inputs'] == {'a': 1, 'b': 1}
        assert last_vector['expected_outputs'] == {'out': 1}
        
    finally:
        os.unlink(test_file)


def test_run_tests():
    """Test running tests with test vectors"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    test_framework = TestFramework(simulator)
    
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
    
    results = test_framework._run_tests('And', test_vectors)
    assert results['chip_name'] == 'And'
    assert results['total_tests'] == 2
    assert results['passed'] == 2
    assert results['failed'] == 0


def test_run_tests_with_failures():
    """Test running tests that include failures"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    test_framework = TestFramework(simulator)
    
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
    
    results = test_framework._run_tests('And', test_vectors)
    assert results['total_tests'] == 2
    assert results['passed'] == 1
    assert results['failed'] == 1
    
    # Check that the failure is properly recorded
    failed_result = results['results'][1]
    assert not failed_result['passed']
    assert len(failed_result['mismatches']) == 1


def test_complete_workflow():
    """Test the complete workflow from HDL parsing to testing"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    test_framework = TestFramework(simulator)
    
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
    chip = parser.parse_content(hdl_content)
    assert chip.name == "TestChip"
    
    # Test the chip directly
    inputs = {'a': 1, 'b': 1}
    outputs = simulator.simulate_chip('TestChip', inputs)
    assert outputs['out'] == 1
    
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
    results = test_framework._run_tests('TestChip', test_vectors)
    assert results['passed'] == 2
    assert results['failed'] == 0


def test_hierarchical_chip_composition():
    """Test a chip that instantiates another non-built-in chip that uses built-in gates"""
    parser = HDLParser()
    simulator = ChipSimulator(parser)
    
    # First, define a simple non-built-in chip (Xor-like using built-ins)
    xor_chip_hdl = """
    CHIP SimpleXor {
        IN a, b;
        OUT out;
        
        PARTS:
        Not(in=a, out=nota);
        Not(in=b, out=notb);
        And(a=a, b=notb, out=w1);
        And(a=nota, b=b, out=w2);
        Or(a=w1, b=w2, out=out);
    }
    """
    
    # Parse the SimpleXor chip
    xor_chip = parser.parse_content(xor_chip_hdl)
    assert xor_chip.name == "SimpleXor"
    assert len(xor_chip.parts) == 5  # 2 Not, 2 And, 1 Or
    assert not xor_chip.is_builtin
    
    # Test SimpleXor directly
    xor_inputs = {'a': 0, 'b': 1}
    xor_outputs = simulator.simulate_chip('SimpleXor', xor_inputs)
    assert xor_outputs['out'] == 1  # XOR(0,1) = 1
    
    # Now define a higher-level chip that uses SimpleXor
    complex_chip_hdl = """
    CHIP ComplexChip {
        IN x, y, z;
        OUT result;
        
        PARTS:
        SimpleXor(a=x, b=y, out=temp);
        And(a=temp, b=z, out=result);
    }
    """
    
    # Parse the ComplexChip
    complex_chip = parser.parse_content(complex_chip_hdl)
    assert complex_chip.name == "ComplexChip"
    assert len(complex_chip.parts) == 2  # SimpleXor + And
    assert not complex_chip.is_builtin
    
    # Test the hierarchical composition
    # ComplexChip: (XOR(x,y) AND z)
    test_cases = [
        ({'x': 0, 'y': 0, 'z': 1}, 0),  # XOR(0,0)=0, AND(0,1)=0
        ({'x': 0, 'y': 1, 'z': 1}, 1),  # XOR(0,1)=1, AND(1,1)=1
        ({'x': 1, 'y': 0, 'z': 0}, 0),  # XOR(1,0)=1, AND(1,0)=0
        ({'x': 1, 'y': 1, 'z': 1}, 0),  # XOR(1,1)=0, AND(0,1)=0
    ]
    
    for inputs, expected_output in test_cases:
        outputs = simulator.simulate_chip('ComplexChip', inputs)
        assert outputs['result'] == expected_output, \
            f"Failed for inputs {inputs}: expected {expected_output}, got {outputs['result']}"
    
    # Test that the internal signals are properly handled
    # This tests that the SimpleXor's internal signals (nota, notb, w1, w2) 
    # don't interfere with the ComplexChip's internal signal (temp)
    complex_inputs = {'x': 1, 'y': 0, 'z': 1}
    complex_outputs = simulator.simulate_chip('ComplexChip', complex_inputs)
    assert complex_outputs['result'] == 1  # XOR(1,0)=1, AND(1,1)=1
    
    # Verify that both chips are available in the parser
    assert parser.get_chip('SimpleXor') is not None
    assert parser.get_chip('ComplexChip') is not None
    
    # Verify that SimpleXor is not built-in but ComplexChip can use it
    assert not parser.is_builtin('SimpleXor')
    assert not parser.is_builtin('ComplexChip')


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_builtin_chips_loaded,
        test_parse_simple_chip,
        test_parse_chip_with_multiple_parts,
        test_parse_connections,
        test_is_builtin,
        test_builtin_and_logic,
        test_builtin_or_logic,
        test_builtin_not_logic,
        test_builtin_nand_logic,
        test_composite_chip_simulation,
        test_read_test_vectors,
        test_run_tests,
        test_run_tests_with_failures,
        test_complete_workflow,
        test_hierarchical_chip_composition,
    ]
    
    passed = 0
    failed = 0
    
    print("Running comprehensive test suite...")
    print("=" * 50)
    
    for test in tests:
        try:
            test()
            print(f" {test.__name__}")
            passed += 1
        except Exception as e:
            print(f" {test.__name__}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed / len(tests) * 100):.1f}%")
    
    if failed == 0:
        print(" All tests passed!")
    else:
        print(f"  {failed} test(s) failed")
    
    return failed == 0


if __name__ == '__main__':
    run_all_tests() 