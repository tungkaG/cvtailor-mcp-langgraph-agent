"""SQLite storage for application tracking.

This module contains:
- Database initialization
- Application record CRUD operations

Uses sqlite3 from the standard library for lightweight persistence.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from cvtailor_mcp.schemas import DATABASE_PATH


def _get_db_path(db_path: str | Path | None = None) -> Path:
    """Get the database path, using default if not provided."""
    if db_path is None:
        return DATABASE_PATH
    return Path(db_path)


def init_db(db_path: str | Path | None = None) -> None:
    """Initialize the SQLite database with the applications table.
    
    Creates the table if it doesn't exist.
    
    Args:
        db_path: Optional path to the database file. Uses default if not provided.
    """
    path = _get_db_path(db_path)
    
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                output_path TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def log_application(
    company: str,
    role: str,
    status: str,
    notes: str = "",
    output_path: str = "",
    db_path: str | Path | None = None
) -> dict:
    """Log a job application to the database.
    
    Args:
        company: Company name.
        role: Role/position name.
        status: Application status (e.g., 'drafted', 'submitted').
        notes: Optional notes about the application.
        output_path: Optional path to the generated application pack.
        db_path: Optional path to the database file.
        
    Returns:
        Dictionary with the logged application details including the new ID.
    """
    path = _get_db_path(db_path)
    
    # Initialize database if needed
    init_db(db_path)
    
    created_at = datetime.now().isoformat()
    
    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO applications (company, role, status, notes, output_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (company, role, status, notes, output_path, created_at)
        )
        conn.commit()
        application_id = cursor.lastrowid
    finally:
        conn.close()
    
    return {
        "id": application_id,
        "company": company,
        "role": role,
        "status": status,
        "notes": notes,
        "output_path": output_path,
        "created_at": created_at
    }


def list_applications(
    status: Optional[str] = None,
    db_path: str | Path | None = None
) -> list[dict]:
    """List job applications from the database.
    
    Args:
        status: Optional status filter. If provided, only returns applications
                with this status.
        db_path: Optional path to the database file.
        
    Returns:
        List of dictionaries, each representing an application record.
    """
    path = _get_db_path(db_path)
    
    # Initialize database if needed
    init_db(db_path)
    
    conn = sqlite3.connect(str(path))
    try:
        cursor = conn.cursor()
        
        if status is not None:
            cursor.execute(
                """
                SELECT id, company, role, status, notes, output_path, created_at
                FROM applications
                WHERE status = ?
                ORDER BY created_at DESC
                """,
                (status,)
            )
        else:
            cursor.execute(
                """
                SELECT id, company, role, status, notes, output_path, created_at
                FROM applications
                ORDER BY created_at DESC
                """
            )
        
        rows = cursor.fetchall()
    finally:
        conn.close()
    
    # Convert rows to dictionaries
    columns = ["id", "company", "role", "status", "notes", "output_path", "created_at"]
    return [dict(zip(columns, row)) for row in rows]
