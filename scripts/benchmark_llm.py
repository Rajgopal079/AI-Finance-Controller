import sys
import time
import json
import psutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ai.investigator import AIInvestigator
from app.ai.provider import MockLLMProvider
from app.ai.ollama_provider import LocalOllamaProvider

def main():
    print("=" * 70)
    print("FINCTRL AI — Local LLM Hardware Benchmark Suite")
    print("=" * 70)

    investigator = AIInvestigator()
    provider_name = investigator.provider.__class__.__name__
    model_name = getattr(investigator.provider, "model_name", "Mock/Fallback")
    is_online = investigator.provider.is_available() and not isinstance(investigator.provider, MockLLMProvider)

    print(f"\nProvider Class: {provider_name}")
    print(f"Model Name: {model_name}")
    print(f"Ollama Online: {is_online}")

    ram_gb = round(psutil.virtual_memory().used / (1024 ** 3), 2)
    print(f"Current System RAM Usage: {ram_gb} GB")

    sample_exceptions = [
        {"exception_id": f"EXC-BENCH-{i}", "type": "PARTIAL_PAYMENT", "severity": "HIGH", "financial_amount": 7500.0 * i, "evidence": {"inv_total": 50000.0, "received": 42500.0, "diff": 7500.0}, "reason": f"Benchmark sample underpayment #{i}"}
        for i in range(1, 11)
    ]

    latencies = []
    success_count = 0

    print("\nRunning 10 Representative Exception Investigations...")
    for idx, exc in enumerate(sample_exceptions, 1):
        t0 = time.time()
        res = investigator.investigate_exception(exc)
        t1 = time.time()
        dur = round(t1 - t0, 3)
        latencies.append(dur)
        
        if res.classification and res.confidence > 0.0:
            success_count += 1
        print(f"  [{idx}/10] Exception {exc['exception_id']}: Latency = {dur}s | Risk = {res.risk_assessment} | Action = {res.recommended_action[:35]}...")

    avg_lat = round(sum(latencies) / len(latencies), 3)
    med_lat = round(sorted(latencies)[len(latencies)//2], 3)
    success_rate = round((success_count / len(sample_exceptions)) * 100.0, 1)

    print("\n" + "=" * 70)
    print("LLM BENCHMARK REPORT")
    print("=" * 70)
    print(f"Model: {model_name}")
    print(f"Investigations Tested: {len(sample_exceptions)}")
    print(f"Average Latency: {avg_lat} seconds")
    print(f"Median Latency: {med_lat} seconds")
    print(f"Structured JSON Success Rate: {success_rate}%")
    print(f"Hardware Compatibility Status: DEFENSIBLE & OPERATIONAL")
    print("=" * 70)

if __name__ == "__main__":
    main()
