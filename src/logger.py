from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


CSV_COLUMNS = [
    "datetime",
    "mode",
    "loop",
    "display_count",
    "deleted_count",
    "result",
    "detail",
    "screenshot",
]


@dataclass(frozen=True)
class DeleteResult:
    mode: str
    loop: int
    display_count: int
    deleted_count: int
    result: str
    detail: str = ""
    screenshot: str = ""


def setup_logger(name: str = "skypiea") -> logging.Logger:
    Path("output/logs").mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_path = Path("output/logs") / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def append_delete_result(result: DeleteResult, csv_path: str | Path = "output/delete_results.csv") -> None:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()

    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mode": result.mode,
                "loop": result.loop,
                "display_count": result.display_count,
                "deleted_count": result.deleted_count,
                "result": result.result,
                "detail": result.detail,
                "screenshot": result.screenshot,
            }
        )
