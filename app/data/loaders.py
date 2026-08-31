import json
from pathlib import Path
from typing import Dict, List
import pandas as pd
from app.data.generators import SyntheticDataGenerator
from app.database.db import DatabaseManager

class DataLoader:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    def generate_and_load(self, count: int = 100, seed: int = 42) -> Dict[str, List[dict]]:
        generator = SyntheticDataGenerator(seed=seed)
        data = generator.generate(count=count)
        self.db_manager.load_dataset(data)
        return data

    def load_from_json(self, file_path: str) -> Dict[str, List[dict]]:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.db_manager.load_dataset(data)
        return data

    def save_to_json(self, data: Dict[str, List[dict]], file_path: str):
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
