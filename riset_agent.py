#!/usr/bin/env python3
"""
LUMIRA Research Assistant v2.0 - Professional Entry Point
Enhanced entry point for seamless execution with optimal configurations
"""

import sys
import subprocess
from pathlib import Path

def main():
    """
    Professional entry point for LUMIRA Research Assistant.
    
    Executes the research assistant with optimized default parameters
    for mid-spec laptops (12GB RAM, 6-7GB usage target).
    """
    script_dir = Path(__file__).parent
    main_script = script_dir / "main.py"
    
    # Enhanced default arguments for professional execution
    if len(sys.argv) == 1:
        args = [
            "--topic", "akses pendidikan vokasi di Indonesia",
            "--tahun", "2021-2025", 
            "--output_folder", "Riset Vokasi Indonesia – LUMIRA",
            "--max_sources", "25",  # Increased for 12GB RAM
            "--lang", "id",
            "--summarize",
            "--extract_data",
            "--parallel",  # Enable parallel processing
            "--workers", "4"  # Optimal worker count
        ]
        
        print("LUMIRA Research Assistant v2.0")
        print("=" * 60)
        print("Executing with enhanced default configuration")
        print("Optimized for mid-spec laptops (12GB RAM)")
        print("Parallel processing: Enabled (4 workers)")
        print("Target sources: 25 high-quality sources")
        print("=" * 60)
        print("Use --help for additional configuration options")
        print()
        
    else:
        args = sys.argv[1:]
    
    # Execute main script with enhanced configuration
    cmd = [sys.executable, str(main_script)] + args
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
    except Exception as e:
        print(f"\nExecution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
