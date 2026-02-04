"""Store and load trending topics in Excel."""
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import TOPICS_EXCEL, ensure_dirs


def save_topics_to_excel(topics: List[Dict[str, Any]]) -> Path:
    """Save topics to Excel. Creates data dir and file if needed."""
    ensure_dirs()
    df = pd.DataFrame(topics)
    if "index" not in df.columns and df.shape[0] > 0:
        df.insert(0, "index", range(1, len(df) + 1))
    df.to_excel(TOPICS_EXCEL, index=False, sheet_name="Trending Topics")
    return TOPICS_EXCEL


def load_topics_from_excel() -> List[Dict[str, Any]]:
    """Load topics from Excel. Returns empty list if file missing."""
    if not TOPICS_EXCEL.exists():
        return []
    df = pd.read_excel(TOPICS_EXCEL, sheet_name="Trending Topics")
    df = df.astype(str).where(df.notna(), "")
    return df.to_dict("records")
