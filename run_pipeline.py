import sys
from clean_data import main as clean_main
from analyze import main as analyze_main

def run():
    print("=" * 40)
    print("Starting pipeline run...")
    print("=" * 40)

    # step 1
    print("\n--- Running step 1: Cleaning Data ---")
    clean_main()

    # step 2 
    print("\n--- Running step 2: Generating Analytics ---")
    analyze_main()

    print("\nAll done! Processed files are ready.")

if __name__ == "__main__":
    run()
