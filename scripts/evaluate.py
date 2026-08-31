import sys
import time
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ai.controller import FinanceController
from app.data.loaders import DataLoader
from app.core.config import SYNTHETIC_DATA_DIR
from app.metrics.evaluation import SystemEvaluator

def main():
    print("=" * 70)
    print("FINCTRL AI — Ground-Truth System Evaluation & Benchmarking Suite")
    print("=" * 70)

    controller = FinanceController()
    loader = DataLoader(controller.db)

    # Test 1: 100 Record Batch
    print("\n[1/2] Benchmarking 100-Record Synthetic Dataset (With Ground Truth)...")
    demo_path = SYNTHETIC_DATA_DIR / "demo_100.json"
    if demo_path.exists():
        loader.load_from_json(str(demo_path))
    else:
        loader.generate_and_load(100, seed=42)

    t0 = time.time()
    res100 = controller.run_controller_pipeline()
    t1 = time.time()

    eval100 = SystemEvaluator.evaluate_recon(res100["recon_metrics"], controller.db, t0, t1)
    print(json.dumps(eval100, indent=2))

    # Test 2: 500 Record Batch
    print("\n[2/2] Benchmarking 500-Record Synthetic Dataset (With Ground Truth)...")
    test_path = SYNTHETIC_DATA_DIR / "test_500.json"
    if test_path.exists():
        loader.load_from_json(str(test_path))
    else:
        loader.generate_and_load(500, seed=101)

    t0 = time.time()
    res500 = controller.run_controller_pipeline()
    t1 = time.time()

    eval500 = SystemEvaluator.evaluate_recon(res500["recon_metrics"], controller.db, t0, t1)
    print(json.dumps(eval500, indent=2))

    print("\n" + "=" * 70)
    print("GROUND-TRUTH EVALUATION COMPLETE — DEFENSIBLE METRICS GENERATED")
    print("=" * 70)

if __name__ == "__main__":
    main()
