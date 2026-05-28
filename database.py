import sqlite3
from datetime import datetime
from pathlib import Path
import json

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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cotizaciones_magnex (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                empresa TEXT NOT NULL,
                contacto TEXT NOT NULL,
                email TEXT NOT NULL,
                pais TEXT NOT NULL,
                producto TEXT NOT NULL,
                cantidad REAL NOT NULL,
                unidad TEXT NOT NULL,
                precio_fob REAL NOT NULL,
                incoterm TEXT NOT NULL,
                pago TEXT NOT NULL,
                comision_pct REAL NOT NULL,
                valor_total REAL NOT NULL,
                comision_estimada REAL NOT NULL,
                notas TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                nombre TEXT,
                empresa TEXT,
                cargo TEXT,
                email TEXT,
                pais TEXT,
                producto TEXT,
                fuente TEXT DEFAULT 'Apollo',
                estado TEXT DEFAULT 'nuevo',
                notas TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emails_enviados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                lead_id INTEGER,
                destinatario TEXT NOT NULL,
                asunto TEXT NOT NULL,
                estado TEXT DEFAULT 'enviado',
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        conn.commit()


# ── Furniture Cleans ────────────────────────────────────────────────────────

def guardar_cotizacion(cliente, whatsapp, items, subtotal, descuento_pct, descuento_monto, total):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO cotizaciones
               (fecha, cliente, whatsapp, items, subtotal, descuento_pct, descuento_monto, total)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), cliente, whatsapp,
             json.dumps(items, ensure_ascii=False), subtotal, descuento_pct, descuento_monto, total),
        )
        conn.commit()


def obtener_cotizaciones(limit=200):
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


# ── MAGNEX B2B ───────────────────────────────────────────────────────────────

def guardar_cotizacion_magnex(data: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO cotizaciones_magnex
               (fecha, empresa, contacto, email, pais, producto, cantidad, unidad,
                precio_fob, incoterm, pago, comision_pct, valor_total, comision_estimada, notas)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now().strftime("%Y-%m-%d %H:%M"),
             data["empresa"], data["contacto"], data["email"], data["pais"],
             data["producto"], data["cantidad"], data["unidad"],
             data["precio_fob"], data["incoterm"], data["pago"],
             data["comision_pct"], data["valor_total"], data["comision_estimada"],
             data.get("notas", "")),
        )
        conn.commit()


def obtener_cotizaciones_magnex(limit=200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM cotizaciones_magnex ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def stats_magnex():
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as total_cot, SUM(comision_estimada) as total_comisiones FROM cotizaciones_magnex"
        ).fetchone()
    return dict(row) if row else {"total_cot": 0, "total_comisiones": 0}


# ── Leads ────────────────────────────────────────────────────────────────────

def guardar_lead(nombre, empresa, cargo, email, pais, producto, fuente="Apollo", notas=""):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO leads (fecha, nombre, empresa, cargo, email, pais, producto, fuente, notas)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (datetime.now().strftime("%Y-%m-%d %H:%M"),
             nombre, empresa, cargo, email, pais, producto, fuente, notas),
        )
        conn.commit()


def obtener_leads(estado=None, limit=500):
    with get_conn() as conn:
        if estado:
            rows = conn.execute(
                "SELECT * FROM leads WHERE estado=? ORDER BY id DESC LIMIT ?", (estado, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
    return [dict(r) for r in rows]


def actualizar_estado_lead(lead_id, estado):
    with get_conn() as conn:
        conn.execute("UPDATE leads SET estado=? WHERE id=?", (estado, lead_id))
        conn.commit()


def registrar_email_enviado(lead_id, destinatario, asunto, estado="enviado"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO emails_enviados (fecha, lead_id, destinatario, asunto, estado) VALUES (?,?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), lead_id, destinatario, asunto, estado),
        )
        conn.commit()


def stats_leads():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        por_estado = conn.execute(
            "SELECT estado, COUNT(*) as n FROM leads GROUP BY estado"
        ).fetchall()
        emails = conn.execute("SELECT COUNT(*) FROM emails_enviados").fetchone()[0]
    return {"total": total, "por_estado": {r[0]: r[1] for r in por_estado}, "emails": emails}


init_db()
