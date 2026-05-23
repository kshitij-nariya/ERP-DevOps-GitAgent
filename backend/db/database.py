from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(os.environ.get("REVIEW_DB_PATH", "reviews.db"))


def create_db_and_tables() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                repo TEXT NOT NULL,
                pr_number INTEGER NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )


def save_review(report: dict[str, Any]) -> int:
    create_db_and_tables()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO reviews (created_at, repo, pr_number, payload) VALUES (?, ?, ?, ?)",
            (
                report.get("created_at", ""),
                report["repo"],
                report["pr_number"],
                json.dumps(report, default=str),
            ),
        )
        review_id = int(cursor.lastrowid)
        conn.commit()
    report["id"] = review_id
    return review_id


def list_reviews(limit: int = 20) -> list[dict[str, Any]]:
    create_db_and_tables()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, payload FROM reviews ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    reviews = []
    for review_id, payload in rows:
        data = json.loads(payload)
        data["id"] = review_id
        reviews.append(data)
    return reviews


def get_review(review_id: int) -> dict[str, Any] | None:
    create_db_and_tables()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT payload FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if not row:
        return None
    data = json.loads(row[0])
    data["id"] = review_id
    return data
