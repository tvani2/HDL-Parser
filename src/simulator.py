"""
Chip Simulator

This module provides functionality to simulate chip behavior based on
HDL definitions and input values.
"""

from typing import Dict
from .hdl_parser import HDLParser, Chip, ChipInstance


class ChipSimulator:
    """
    Simulator for chips defined in HDL.
    
    This class can simulate the behavior of both built-in chips
    and composite chips built from other chips.
    """
    
    def __init__(self, parser: HDLParser):
        """
        Initialize the simulator with a parser.
        
        Args:
            parser: HDLParser instance to use for chip definitions
        """
        self.parser = parser
        self._setup_builtin_logic()
    
    def _setup_builtin_logic(self):
        """Setup logic functions for built-in chips"""
        self.builtin_logic = {
            'Nand': self._nand_logic,
            'Not': self._not_logic,
            'And': self._and_logic,
            'Or': self._or_logic
        }
    
    def simulate_chip(self, chip_name: str, inputs: Dict[str, int]) -> Dict[str, int]:
        """
        Simulate a chip with given inputs.
        
        Args:
            chip_name: Name of the chip to simulate
            inputs: Dictionary mapping input pin names to values (0 or 1)
            
        Returns:
            Dictionary mapping output pin names to values
        """
        chip = self.parser.get_chip(chip_name)
        if not chip:
            raise ValueError(f"Unknown chip: {chip_name}")
        
        # Create signal dictionary starting with inputs
        signals = inputs.copy()
        
        if chip.is_builtin:
            return self._simulate_builtin(chip, signals)
        else:
            return self._simulate_composite(chip, signals)
    
    def _simulate_builtin(self, chip: Chip, signals: Dict[str, int]) -> Dict[str, int]:
        """Simulate a built-in chip"""
        if chip.name not in self.builtin_logic:
            raise ValueError(f"No logic defined for built-in chip: {chip.name}")
        
        logic_func = self.builtin_logic[chip.name]
        return logic_func(signals)
    
    def _simulate_composite(self, chip: Chip, signals: Dict[str, int]) -> Dict[str, int]:
        """Simulate a composite chip by simulating all its parts"""
        # Process all parts in order
        for part in chip.parts:
            self._simulate_part(part, signals)
        
        # Return only the output signals
        return {output: signals.get(output, 0) for output in chip.outputs}
    
    def _simulate_part(self, part: ChipInstance, signals: Dict[str, int]):
        """Simulate a single part/instance within a chip"""
        # Get the chip definition to know its inputs and outputs
        chip_def = self.parser.get_chip(part.chip_name)
        if not chip_def:
            raise ValueError(f"Unknown chip: {part.chip_name}")
        
        # Prepare inputs for this part
        part_inputs = {}
        for connection in part.connections:
            if connection.to_pin in chip_def.inputs:  # Input pin
                part_inputs[connection.to_pin] = signals.get(connection.from_pin, 0)
        
        # Simulate the part
        part_outputs = self.simulate_chip(part.chip_name, part_inputs)
        
        # Update signals with outputs from this part
        for connection in part.connections:
            if connection.to_pin in chip_def.outputs:  # Output pin
                signals[connection.from_pin] = part_outputs.get(connection.to_pin, 0)
    
    def _nand_logic(self, signals: Dict[str, int]) -> Dict[str, int]:
        """Logic for NAND gate"""
        a = signals.get('a', 0)
        b = signals.get('b', 0)
        result = 0 if (a == 1 and b == 1) else 1
        return {'out': result}
    
    def _not_logic(self, signals: Dict[str, int]) -> Dict[str, int]:
        """Logic for NOT gate"""
        in_val = signals.get('in', 0)
        result = 1 if in_val == 0 else 0
        return {'out': result}
    
    def _and_logic(self, signals: Dict[str, int]) -> Dict[str, int]:
        """Logic for AND gate"""
        a = signals.get('a', 0)
        b = signals.get('b', 0)
        result = 1 if (a == 1 and b == 1) else 0
        return {'out': result}
    
    def _or_logic(self, signals: Dict[str, int]) -> Dict[str, int]:
        """Logic for OR gate"""
        a = signals.get('a', 0)
        b = signals.get('b', 0)
        result = 1 if (a == 1 or b == 1) else 0
        return {'out': result} 