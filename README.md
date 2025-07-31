# HDL-Parser

A comprehensive Hardware Description Language (HDL) parser and simulator for digital logic circuits.

## Features

- **HDL Parser**: Parse chip definitions with support for complex multi-part chips
- **Chip Simulator**: Simulate digital logic circuits with built-in and custom chips
- **Test Framework**: Comprehensive testing framework for validating chip behavior
- **Built-in Chips**: Support for fundamental logic gates (AND, OR, NOT, NAND)
- **Custom Chips**: Load and simulate custom HDL chip definitions

## Installation

```bash
git clone https://github.com/tvani2/HDL-Parser.git
cd HDL-Parser
```

## How to Run Your Program

### Basic Usage
```bash
python -m src.main <chip_name> <test_file>
```

Example:
```bash
python -m src.main Xor tests/xor_test.tst
```

### Other Commands
```bash
python -m src.main --list-chips      # List all available chips
python -m src.main --test-all        # Test all chips
python -m tests.full_test_suite      # Run comprehensive tests
```

## Description of Your Approach

The HDL-Parser implements a **hierarchical digital logic simulator** with these key components:

### **HDL Parser (`src/hdl_parser.py`)**
- Uses regex-based parsing to extract chip definitions
- Implements structured data classes (`Chip`, `ChipInstance`, `Connection`)
- Pre-loads fundamental gates (AND, OR, NOT, NAND) as built-in chips
- Supports hierarchical parsing of custom chips

### **Chip Simulator (`src/simulator.py`)**
- Recursive simulation that processes composite chips by simulating their parts
- Maintains signal dictionary updated as each part is simulated
- Implements direct logic functions for fundamental gates
- Supports multi-level chip designs with proper signal isolation

### **Test Framework (`src/test_framework.py`)**
- Reads CSV-style test files with input/output vectors
- Runs all test vectors and provides detailed failure reports
- Robust error detection for missing chips, invalid files, and logic mismatches

### **Main Interface (`src/main.py`)**
- Command-line interface for testing and listing chips
- Batch testing with `--test-all`
- Automatic chip discovery from files

## Example HDL and Test Vector Files

### Example HDL File - **Xor.hdl**
```hdl
CHIP Xor {
    IN a, b;
    OUT out;

    PARTS:
    Not(in=a, out=nota);
    Not(in=b, out=notb);
    And(a=a, b=notb, out=aandnotb);
    And(a=nota, b=b, out=notaandb);
    Or(a=aandnotb, b=notaandb, out=out);
}
```

### Example Test Vector File - **xor_test.tst**
```
a,b; out
0,0; 0
0,1; 1
1,0; 1
1,1; 0
```

### Test File Format
- **Header**: `input1,input2; output1,output2`
- **Test cases**: `value1,value2; expected1,expected2`
- **Values**: Only 0 or 1 (binary)
- **Separator**: Semicolon (`;`) between inputs and outputs

## Built-in Chips

- **And**: AND gate (a, b → out)
- **Or**: OR gate (a, b → out)  
- **Not**: NOT gate (in → out)
- **Nand**: NAND gate (a, b → out)

## Testing

Comprehensive testing includes unit, integration, functional, logic, parsing, and simulation tests.

```bash
python -m tests.full_test_suite
```