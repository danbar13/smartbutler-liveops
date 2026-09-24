"""
SmartButler LiveOps Digest - Persistence Layer (db.py)
Stores report metadata, department summaries, and ticket line items in SQLite.
Default database path: ./data/smartbutler_history.db
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "smartbutler_history.db")

def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Creates directory if needed and returns SQLite connection with dictionary row access."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Reports metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_title TEXT NOT NULL,
        site_name TEXT NOT NULL,
        date_range TEXT NOT NULL,
        raw_filename TEXT NOT NULL,
        file_format TEXT NOT NULL,
        total_tickets INTEGER NOT NULL DEFAULT 0,
        overall_success_rate REAL NOT NULL DEFAULT 0.0,
        avg_duration_str TEXT NOT NULL DEFAULT '00:00',
        avg_duration_minutes INTEGER NOT NULL DEFAULT 0,
        total_time_str TEXT NOT NULL DEFAULT '00:00',
        total_time_minutes INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Individual tickets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        department TEXT NOT NULL,
        task_category TEXT NOT NULL,
        received_at TEXT NOT NULL,
        creator TEXT NOT NULL,
        location TEXT NOT NULL,
        description TEXT NOT NULL,
        provided_at TEXT NOT NULL,
        duration_str TEXT NOT NULL,
        duration_minutes INTEGER,
        resolver TEXT NOT NULL,
        standard_str TEXT NOT NULL,
        standard_minutes INTEGER,
        sla_met INTEGER NOT NULL DEFAULT 0,
        sla_breach_ratio REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
    );
    """)

    # 3. Department summaries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS department_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        department TEXT NOT NULL,
        total_tickets INTEGER NOT NULL DEFAULT 0,
        avg_duration_str TEXT NOT NULL DEFAULT '00:00',
        avg_duration_minutes INTEGER NOT NULL DEFAULT 0,
        total_time_str TEXT NOT NULL DEFAULT '00:00',
        total_time_minutes INTEGER NOT NULL DEFAULT 0,
        success_rate REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def save_report(report_data: Dict[str, Any],
                tickets: List[Dict[str, Any]],
                dept_summaries: List[Dict[str, Any]],
                db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Saves a parsed report along with its tickets and department summaries into SQLite.
    Returns the newly created report_id.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO reports (
        report_title, site_name, date_range, raw_filename, file_format,
        total_tickets, overall_success_rate, avg_duration_str, avg_duration_minutes,
        total_time_str, total_time_minutes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_data.get("report_title", "Log Report - Providers"),
        report_data.get("site_name", "Grand Hotel"),
        report_data.get("date_range", "Current Period"),
        report_data.get("raw_filename", "report.pdf"),
        report_data.get("file_format", "PDF"),
        report_data.get("total_tickets", len(tickets)),
        report_data.get("overall_success_rate", 0.0),
        report_data.get("avg_duration_str", "00:00"),
        report_data.get("avg_duration_minutes", 0),
        report_data.get("total_time_str", "00:00"),
        report_data.get("total_time_minutes", 0)
    ))
    report_id = cursor.lastrowid

    # Insert tickets
    for t in tickets:
        cursor.execute("""
        INSERT INTO tickets (
            report_id, department, task_category, received_at, creator,
            location, description, provided_at, duration_str, duration_minutes,
            resolver, standard_str, standard_minutes, sla_met, sla_breach_ratio
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            t.get("department", "General"),
            t.get("task_category", ""),
            t.get("received_at", ""),
            t.get("creator", ""),
            t.get("location", ""),
            t.get("description", ""),
            t.get("provided_at", "N/A"),
            t.get("duration_str", "N/A"),
            t.get("duration_minutes"),
            t.get("resolver", "-"),
            t.get("standard_str", "00:15"),
            t.get("standard_minutes", 15),
            1 if t.get("sla_met") else 0,
            t.get("sla_breach_ratio", 0.0)
        ))

    # Insert department summaries
    for d in dept_summaries:
        cursor.execute("""
        INSERT INTO department_summaries (
            report_id, department, total_tickets, avg_duration_str,
            avg_duration_minutes, total_time_str, total_time_minutes, success_rate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            d.get("department", "General"),
            d.get("total_tickets", 0),
            d.get("avg_duration_str", "00:00"),
            d.get("avg_duration_minutes", 0),
            d.get("total_time_str", "00:00"),
            d.get("total_time_minutes", 0),
            d.get("success_rate", 0.0)
        ))

    conn.commit()
    conn.close()
    return report_id

def list_reports(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Lists all historical reports ordered by upload time descending."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, report_title, site_name, date_range, raw_filename, file_format,
           total_tickets, overall_success_rate, avg_duration_str, total_time_str, created_at
    FROM reports
    ORDER BY id DESC;
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_report(report_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves full report details including tickets and department summaries."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    report_row = cursor.fetchone()
    if not report_row:
        conn.close()
        return None

    report = dict(report_row)

    cursor.execute("SELECT * FROM department_summaries WHERE report_id = ?", (report_id,))
    report["departments"] = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM tickets WHERE report_id = ? ORDER BY id ASC", (report_id,))
    report["tickets"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return report

def get_latest_report(db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves the most recently uploaded report."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM reports ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return get_report(row["id"], db_path)
    return None

def delete_report(report_id: int, db_path: str = DEFAULT_DB_PATH):
    """Deletes a report and cascades tickets and department summaries."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
