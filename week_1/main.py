import sys
from pathlib import Path
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import run_data_profile

# Global Paths
SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR = Path("data/3_gold")
DB_NAME = "jobs.db"

def run_profiler():
    DB_PATH = GOLD_DIR / DB_NAME
    run_data_profile(DB_PATH)

def run_gold():
    input_dir = SILVER_DIR
    output_dir = GOLD_DIR
    load_all_jsons(input_dir, output_dir)

def run_silver():
    input_dir = BRONZE_DIR
    output_dir = SILVER_DIR
    process_all_html(input_dir, output_dir)


def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    ingest_all_mhtml(input_dir, output_dir)

def main():
    # Requirement: Show help if no argument provided
    if len(sys.argv) < 2:
        print("Usage: python main.py [ingest|process|load|profile|all]")
        print("\nCOMMAND SET")
        print("python main.py ingest")
        print("python main.py process")
        print("python main.py load")
        print("python main.py profile")
        print("python main.py all")
        return

    command = sys.argv[1].lower()

    match command:
        case "ingest":
            run_bronze()
        
        case "process":
            run_silver()
            
        case "load":
            run_gold()
            
        case "profile":
            run_profiler()
            
        case "all":
            # Orchestration: Full ETL pipeline execution
            print("🌊 RUNNING FULL PIPELINE...")
            run_bronze()
            run_silver()
            run_gold()
            run_profiler()
            print("\n✨ Pipeline Complete.")

        case _:
            print(f"❓ Unknown command: {command}")

if __name__ == "__main__":
    main()