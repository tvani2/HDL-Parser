import sys
import argparse
from pathlib import Path
from .hdl_parser import HDLParser
from .simulator import ChipSimulator
from .test_framework import TestFramework


def main():
    """
    Main entry point for the HDL Parser and Simulator application.
    
    Usage:
        python -m src.main <chip_name> <test_file>
        python -m src.main --list-chips
        python -m src.main --test-all
    """
    parser = argparse.ArgumentParser(
        description="HDL Parser and Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main And tests/and_test.txt
  python -m src.main --list-chips
  python -m src.main --test-all
        """
    )
    
    parser.add_argument(
        'chip_name',
        nargs='?',
        help='Name of the chip to test'
    )
    
    parser.add_argument(
        'test_file',
        nargs='?',
        help='Path to the test vector file'
    )
    
    parser.add_argument(
        '--list-chips',
        action='store_true',
        help='List all available chips'
    )
    
    parser.add_argument(
        '--test-all',
        action='store_true',
        help='Run tests for all available chips'
    )
    
    args = parser.parse_args()
    
    # Initialize components
    hdl_parser = HDLParser()
    simulator = ChipSimulator(hdl_parser)
    test_framework = TestFramework(simulator)
    
    try:
        if args.list_chips:
            list_available_chips(hdl_parser)
        elif args.test_all:
            test_all_chips(test_framework)
        elif args.chip_name and args.test_file:
            test_single_chip(test_framework, args.chip_name, args.test_file)
        else:
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_available_chips(parser: HDLParser):
    """List all available chips (built-in and from files)"""
    print("Available chips:")
    print("\nBuilt-in chips:")
    for chip_name in parser.BUILTIN_CHIPS.keys():
        print(f"  - {chip_name}")
    
    # Look for HDL files in chips directory
    chips_dir = Path("chips")
    if chips_dir.exists():
        hdl_files = list(chips_dir.glob("*.hdl"))
        if hdl_files:
            print("\nChips from files:")
            for hdl_file in hdl_files:
                chip_name = hdl_file.stem
                print(f"  - {chip_name}")
        else:
            print("\nNo chip files found in chips/ directory")
    else:
        print("\nNo chips/ directory found")


def test_all_chips(test_framework: TestFramework):
    """Run tests for all available chips"""
    print("Running tests for all available chips...")
    
    # Test built-in chips
    builtin_chips = ['And', 'Or', 'Not', 'Nand']
    test_results = []
    
    for chip_name in builtin_chips:
        test_file = f"tests/{chip_name.lower()}_test.tst"
        if Path(test_file).exists():
            print(f"\nTesting {chip_name}...")
            try:
                results = test_framework.run_tests_from_file(chip_name, test_file)
                test_framework.print_test_report(results)
                test_results.append(results)
            except Exception as e:
                print(f"Error testing {chip_name}: {e}")
    
    # Test composite chips
    chips_dir = Path("chips")
    if chips_dir.exists():
        for hdl_file in chips_dir.glob("*.hdl"):
            chip_name = hdl_file.stem
            test_file = f"tests/{chip_name.lower()}_test.tst"
            if Path(test_file).exists():
                print(f"\nTesting {chip_name}...")
                try:
                    results = test_framework.run_tests_from_file(chip_name, test_file)
                    test_framework.print_test_report(results)
                    test_results.append(results)
                except Exception as e:
                    print(f"Error testing {chip_name}: {e}")
    
    # Print overall summary
    if test_results:
        total_tests = sum(r['total_tests'] for r in test_results)
        total_passed = sum(r['passed'] for r in test_results)
        total_failed = sum(r['failed'] for r in test_results)
        
        print("\n=== Overall Summary ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Success Rate: {(total_passed / total_tests * 100):.1f}%")


def test_single_chip(test_framework: TestFramework, chip_name: str, test_file: str):
    """Test a single chip with the provided test file"""
    if not Path(test_file).exists():
        print(f"Error: Test file '{test_file}' not found")
        sys.exit(1)
    
    print(f"Testing {chip_name} with {test_file}...")
    results = test_framework.run_tests_from_file(chip_name, test_file)
    test_framework.print_test_report(results)


if __name__ == "__main__":
    main() 