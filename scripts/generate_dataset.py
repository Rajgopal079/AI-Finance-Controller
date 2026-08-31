import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data.loaders import DataLoader
from app.core.config import SYNTHETIC_DATA_DIR

def main():
    loader = DataLoader()
    print("Generating demo dataset (100 records)...")
    demo_100 = loader.generate_and_load(count=100, seed=42)
    demo_path = SYNTHETIC_DATA_DIR / "demo_100.json"
    loader.save_to_json(demo_100, str(demo_path))
    print(f"Saved demo dataset to {demo_path}")

    print("Generating test benchmark dataset (500 records)...")
    test_500 = loader.generate_and_load(count=500, seed=101)
    test_path = SYNTHETIC_DATA_DIR / "test_500.json"
    loader.save_to_json(test_500, str(test_path))
    print(f"Saved benchmark dataset to {test_path}")

    # Re-load demo_100 into DB by default
    loader.load_from_json(str(demo_path))
    print("Default demo_100 dataset loaded into SQLite database successfully!")

if __name__ == "__main__":
    main()
