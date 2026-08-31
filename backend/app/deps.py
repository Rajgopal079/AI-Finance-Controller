import sys
import math
from pathlib import Path
import pandas as pd

# Ensure root workspace directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.ai.controller import FinanceController

_controller_instance = None

def get_controller() -> FinanceController:
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = FinanceController()
    return _controller_instance

def clean_val(val):
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

def df_to_records(df: pd.DataFrame):
    if df is None or df.empty:
        return []
    records = df.to_dict(orient="records")
    return [
        {k: clean_val(v) for k, v in row.items()}
        for row in records
    ]
