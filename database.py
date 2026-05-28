import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "cotizaciones.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                cliente TEXT NOT NULL,
                whatsapp TEXT NOT NULL,
                items TEXT NOT NULL,
                subtotal REAL NOT NULL,
                descuento_pct INTEGER NOT NULL DEFAULT 0,
                descuento_monto REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL
            )
        """)
        conn.commit()


def guardar_cotizacion(cliente, whatsapp, items, subtotal, descuento_pct, descuento_monto, total):
    import json
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO cotizaciones
               (fecha, cliente, whatsapp, items, subtotal, descuento_pct, descuento_monto, total)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                cliente,
                whatsapp,
                json.dumps(items, ensure_ascii=False),
                subtotal,
                descuento_pct,
                descuento_monto,
                total,
            ),
        )
        conn.commit()


def obtener_cotizaciones(limit=200):
    import json
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM cotizaciones ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["items"] = json.loads(d["items"])
        result.append(d)
    return result


def stats_totales():
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as total_cot, SUM(total) as total_ventas FROM cotizaciones"
        ).fetchone()
    return dict(row) if row else {"total_cot": 0, "total_ventas": 0}


init_db()
