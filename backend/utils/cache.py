"""SQLite-based caching layer for AlphaGenome API responses."""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path


class PredictionCache:
    """Simple SQLite cache for API predictions to minimize API calls."""

    def __init__(self, cache_path: str = "predictions_cache.db", ttl_hours: int = 24):
        self.cache_path = cache_path
        self.ttl = timedelta(hours=ttl_hours)
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                cache_key TEXT PRIMARY KEY,
                variant_hash TEXT NOT NULL,
                interval_hash TEXT NOT NULL,
                response_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_variant ON predictions(variant_hash)
        """)
        conn.commit()
        conn.close()

    def _generate_key(
        self, variant: Dict[str, Any], interval: Dict[str, Any], tissues: list
    ) -> str:
        """Generate a unique cache key from request parameters."""
        key_data = {
            "variant": variant,
            "interval": interval,
            "tissues": sorted(tissues) if tissues else [],
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(
        self, variant: Dict[str, Any], interval: Dict[str, Any], tissues: list
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached prediction if available and not expired."""
        cache_key = self._generate_key(variant, interval, tissues)

        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT response_data, created_at FROM predictions WHERE cache_key = ?",
            (cache_key,),
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            response_data, created_at = result
            created_time = datetime.fromisoformat(created_at)

            # Check if cache entry is still valid
            if datetime.now() - created_time < self.ttl:
                return json.loads(response_data)

        return None

    def set(
        self,
        variant: Dict[str, Any],
        interval: Dict[str, Any],
        tissues: list,
        response_data: Dict[str, Any],
    ):
        """Store prediction in cache."""
        cache_key = self._generate_key(variant, interval, tissues)
        variant_hash = hashlib.sha256(
            json.dumps(variant, sort_keys=True).encode()
        ).hexdigest()
        interval_hash = hashlib.sha256(
            json.dumps(interval, sort_keys=True).encode()
        ).hexdigest()

        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO predictions 
               (cache_key, variant_hash, interval_hash, response_data, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                cache_key,
                variant_hash,
                interval_hash,
                json.dumps(response_data),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    def clear_expired(self):
        """Remove expired cache entries."""
        cutoff = (datetime.now() - self.ttl).isoformat()

        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE created_at < ?", (cutoff,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*), MAX(created_at), MIN(created_at) FROM predictions"
        )
        result = cursor.fetchone()
        conn.close()

        return {
            "total_entries": result[0] if result[0] else 0,
            "newest_entry": result[1],
            "oldest_entry": result[2],
            "cache_path": self.cache_path,
            "ttl_hours": self.ttl.total_seconds() / 3600,
        }
