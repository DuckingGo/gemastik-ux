#!/usr/bin/env python3
"""
LUMIRA Research Assistant v2.0 - Professional Demo
Enhanced demo version with improved performance for mid-spec laptops
"""

import sys
import subprocess
from pathlib import Path

def run_demo():
    """
    Execute professional demo with limited search for testing purposes.
    
    This demo will search for a maximum of 8 sources to demonstrate
    the enhanced functionality while keeping execution time reasonable.
    """
    print("LUMIRA Research Assistant v2.0 - DEMO MODE")
    print("=" * 65)
    print("Professional demo with enhanced performance capabilities")
    print("Target: 8 high-quality sources for comprehensive testing")
    print("Output: Demo_Output_Enhanced folder")
    print("Features: Parallel processing, enhanced data extraction")
    print("=" * 65)
    
    script_dir = Path(__file__).parent
    main_script = script_dir / "main.py"
    
    # Enhanced demo arguments with professional settings
    args = [
        "--topic", "pendidikan vokasi digital indonesia", 
        "--tahun", "2021-2025",
        "--output_folder", "Demo_Output_Enhanced",
        "--max_sources", "8",  # Reasonable limit for demo
        "--lang", "id",
        "--summarize",
        "--extract_data",
        "--parallel",
        "--workers", "3",  # Conservative worker count for demo
        "--verbose"  # Enable detailed logging for demo
    ]
    
    print("\nStarting enhanced demo execution...")
    print("Processing time: Approximately 3-5 minutes")
    print("Enhanced features: Parallel processing, comprehensive analysis")
    print()
    
    # Execute main script with enhanced parameters
    cmd = [sys.executable, str(main_script)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        print("EXECUTION OUTPUT:")
        print("-" * 50)
        print(result.stdout)
        
        if result.stderr:
            print("\nDETAILED LOGS:")
            print("-" * 50)
            print(result.stderr)
            
        if result.returncode == 0:
            print("\n" + "=" * 65)
            print("DEMO EXECUTION SUCCESSFUL")
            print("=" * 65)
            print("Results available in 'Demo_Output_Enhanced' folder")
            print("\nGenerated files:")
            print("- Laporan_Riset_Lengkap.md (Comprehensive report)")
            print("- Database_Sumber_Riset_Komprehensif.xlsx (Multi-sheet Excel)")
            print("- Database_Sumber_Riset.csv (Main data CSV)")
            print("- metadata_komprehensif.json (Detailed metadata)")
            print("- ringkasan_penelitian.txt (Research summary)")
        else:
            print(f"\nDEMO EXECUTION FAILED")
            print(f"Exit code: {result.returncode}")
            print("Check logs above for detailed error information")
            
    except subprocess.TimeoutExpired:
        print("\nDEMO TIMEOUT")
        print("Demo execution exceeded 10 minute limit")
        print("This may indicate network connectivity issues")
    except Exception as e:
        print(f"\nDEMO ERROR: {e}")
        print("Check system configuration and dependencies")

if __name__ == "__main__":
    run_demo()
