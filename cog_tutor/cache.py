import hashlib
import sqlite3
from pathlib import Path
from typing import Optional

_DB = Path(__file__).with_name('cog_cache.sqlite')

def _conn():
    con = sqlite3.connect(str(_DB))
    con.execute('CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)')
    return con

def make_key(*parts) -> str:
    raw = '\u241f'.join(str(p) for p in parts)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def get(key: str) -> Optional[str]:
    with _conn() as con:
        cur = con.execute('SELECT v FROM kv WHERE k=?', (key,))
        row = cur.fetchone()
        return row[0] if row else None

def set(key: str, value: str) -> None:
    with _conn() as con:
        con.execute('REPLACE INTO kv (k, v) VALUES (?, ?)', (key, value))
