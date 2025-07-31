"""
HDL Parser and Simulator

This module provides functionality to parse HDL (Hardware Description Language) files,
build internal representations of chips, and simulate their behavior.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PinType(Enum):
    """Enumeration for pin types (input/output)"""
    INPUT = "IN"
    OUTPUT = "OUT"


@dataclass
class Pin:
    """Represents a pin in a chip"""
    name: str
    pin_type: PinType


@dataclass
class Connection:
    """Represents a connection between pins"""
    from_pin: str
    to_pin: str


@dataclass
class ChipInstance:
    """Represents an instance of a chip within another chip"""
    chip_name: str
    instance_name: str
    connections: List[Connection]


@dataclass
class Chip:
    """Represents a complete chip definition"""
    name: str
    inputs: List[str]
    outputs: List[str]
    parts: List[ChipInstance]
    is_builtin: bool = False


class HDLParser:
    """
    Parser for HDL (Hardware Description Language) files.
    
    This class can parse HDL files and build internal representations
    of chips including their inputs, outputs, and internal structure.
    """
    
    # Built-in chips that don't need parsing
    BUILTIN_CHIPS = {
        'Nand': {'inputs': 2, 'outputs': 1},
        'Not': {'inputs': 1, 'outputs': 1},
        'And': {'inputs': 2, 'outputs': 1},
        'Or': {'inputs': 2, 'outputs': 1}
    }
    
    def __init__(self):
        """Initialize the HDL parser"""
        self.chips: Dict[str, Chip] = {}
        self._load_builtin_chips()
    
    def _load_builtin_chips(self):
        """Load built-in chip definitions"""
        # Define built-in chips with their actual input/output names
        builtin_definitions = {
            'Nand': {'inputs': ['a', 'b'], 'outputs': ['out']},
            'Not': {'inputs': ['in'], 'outputs': ['out']},
            'And': {'inputs': ['a', 'b'], 'outputs': ['out']},
            'Or': {'inputs': ['a', 'b'], 'outputs': ['out']}
        }
        
        for chip_name, specs in builtin_definitions.items():
            self.chips[chip_name] = Chip(
                name=chip_name,
                inputs=specs['inputs'],
                outputs=specs['outputs'],
                parts=[],
                is_builtin=True
            )
    
    def parse_file(self, file_path: str) -> Chip:
        """
        Parse an HDL file and return a Chip object.
        
        Args:
            file_path: Path to the HDL file to parse
            
        Returns:
            Chip object representing the parsed chip
        """
        with open(file_path, 'r') as file:
            content = file.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Chip:
        """
        Parse HDL content and return a Chip object.
        
        Args:
            content: HDL file content as string
            
        Returns:
            Chip object representing the parsed chip
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Filter out comment lines
        non_comment_lines = []
        for line in lines:
            if not line.startswith('/**') and not line.startswith(' *') and not line.startswith('*/') and not line.startswith('*'):
                non_comment_lines.append(line)
        
        # Extract chip name from first non-comment line
        chip_name = self._extract_chip_name(non_comment_lines[0])
        
        # Extract inputs and outputs
        inputs = self._extract_pins(non_comment_lines, PinType.INPUT)
        outputs = self._extract_pins(non_comment_lines, PinType.OUTPUT)
        
        # Extract parts
        parts = self._extract_parts(non_comment_lines)
        
        chip = Chip(
            name=chip_name,
            inputs=inputs,
            outputs=outputs,
            parts=parts,
            is_builtin=False
        )
        
        self.chips[chip_name] = chip
        return chip
    
    def _extract_chip_name(self, first_line: str) -> str:
        """Extract chip name from the first line"""
        # Expected format: "CHIP ChipName"
        match = re.match(r'CHIP\s+(\w+)', first_line)
        if not match:
            raise ValueError(f"Invalid chip declaration: {first_line}")
        return match.group(1)
    
    def _extract_pins(self, lines: List[str], pin_type: PinType) -> List[str]:
        """Extract pin names for a given pin type"""
        pins = []
        
        for line in lines:
            if line.startswith(pin_type.value):
                # Extract pin names from the same line (e.g., "IN a, b;")
                pin_line = line[len(pin_type.value):].strip()
                if pin_line.endswith(';'):
                    pin_line = pin_line[:-1]  # Remove semicolon
                
                # Parse pin names (comma-separated)
                pin_names = [pin.strip() for pin in pin_line.split(',')]
                pins.extend(pin_names)
                break  # Found the pin section, no need to continue
        
        return pins
    
    def _extract_parts(self, lines: List[str]) -> List[ChipInstance]:
        """Extract chip parts/instances"""
        parts = []
        in_parts_section = False
        
        for line in lines:
            if line.startswith('PARTS:'):
                in_parts_section = True
                continue
            elif line.startswith('IN') or line.startswith('OUT'):
                in_parts_section = False
                continue
            
            if in_parts_section and line:
                part = self._parse_part_line(line)
                if part:
                    parts.append(part)
        
        return parts
    
    def _parse_part_line(self, line: str) -> Optional[ChipInstance]:
        """Parse a single part line into a ChipInstance"""
        # Expected format: "ChipName (pin1=signal1, pin2=signal2, ...)" or "ChipName InstanceName (pin1=signal1, pin2=signal2, ...)"
        match = re.match(r'(\w+)(?:\s+(\w+))?\s*\((.*)\)', line)
        if not match:
            return None
        
        chip_name = match.group(1)
        instance_name = match.group(2) if match.group(2) else chip_name  # Use chip name as instance name if not provided
        connections_str = match.group(3)
        
        connections = self._parse_connections(connections_str)
        
        return ChipInstance(
            chip_name=chip_name,
            instance_name=instance_name,
            connections=connections
        )
    
    def _parse_connections(self, connections_str: str) -> List[Connection]:
        """Parse connection string into Connection objects"""
        connections = []
        
        # Split by comma, but be careful about nested parentheses
        parts = connections_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '=' in part:
                # Format: "pin=signal"
                pin, signal = part.split('=', 1)
                connections.append(Connection(
                    from_pin=signal.strip(),
                    to_pin=pin.strip()
                ))
        
        return connections
    
    def get_chip(self, chip_name: str) -> Optional[Chip]:
        """Get a chip by name, loading it if necessary"""
        if chip_name in self.chips:
            return self.chips[chip_name]
        
        # Try to load from file
        try:
            file_path = f"chips/{chip_name}.hdl"
            return self.parse_file(file_path)
        except FileNotFoundError:
            return None
    
    def is_builtin(self, chip_name: str) -> bool:
        """Check if a chip is a built-in chip"""
        return chip_name in self.BUILTIN_CHIPS 