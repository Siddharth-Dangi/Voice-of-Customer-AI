import sqlite3
import os
import json
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voc_ai.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Uploaded Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        status TEXT NOT NULL,
        summary_json TEXT
    );
    """)
    
    # 2. Customer Feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        feedback_text TEXT NOT NULL,
        customer_id TEXT,
        created_at TEXT,
        FOREIGN KEY (report_id) REFERENCES uploaded_reports (id) ON DELETE CASCADE
    );
    """)
    
    # 3. Analysis Results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_results (
        feedback_id INTEGER PRIMARY KEY,
        sentiment TEXT NOT NULL,
        sentiment_score REAL NOT NULL,
        category TEXT NOT NULL,
        pain_points_json TEXT,
        feature_requests_json TEXT,
        opportunity_score REAL DEFAULT 0.0,
        business_impact_score REAL DEFAULT 0.0,
        FOREIGN KEY (feedback_id) REFERENCES customer_feedback (id) ON DELETE CASCADE
    );
    """)
    
    # 4. Generated Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        generated_at TEXT NOT NULL,
        pdf_path TEXT NOT NULL,
        FOREIGN KEY (report_id) REFERENCES uploaded_reports (id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

def create_uploaded_report(filename):
    """Creates a new uploaded report record and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO uploaded_reports (filename, uploaded_at, status) VALUES (?, ?, ?);",
        (filename, now_str, "processing")
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id

def update_report_status(report_id, status, summary_json=None):
    """Updates the status and summary JSON of a report."""
    conn = get_connection()
    cursor = conn.cursor()
    if summary_json:
        cursor.execute(
            "UPDATE uploaded_reports SET status = ?, summary_json = ? WHERE id = ?;",
            (status, json.dumps(summary_json), report_id)
        )
    else:
        cursor.execute(
            "UPDATE uploaded_reports SET status = ? WHERE id = ?;",
            (status, report_id)
        )
    conn.commit()
    conn.close()

def insert_customer_feedback(report_id, feedback_text, customer_id=None, created_at=None):
    """Inserts a single customer feedback item and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customer_feedback (report_id, feedback_text, customer_id, created_at) VALUES (?, ?, ?, ?);",
        (report_id, feedback_text, customer_id, created_at)
    )
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id

def insert_analysis_result(feedback_id, analysis):
    """Inserts analysis results for a feedback item.
    
    analysis can be a dict or a Pydantic model with fields:
    sentiment, sentiment_score, category, pain_points, feature_requests, opportunity_score, business_impact_score
    """
    if not isinstance(analysis, dict):
        analysis_dict = analysis.model_dump()
    else:
        analysis_dict = analysis

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO analysis_results 
        (feedback_id, sentiment, sentiment_score, category, pain_points_json, feature_requests_json, opportunity_score, business_impact_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            feedback_id,
            analysis_dict["sentiment"],
            analysis_dict["sentiment_score"],
            analysis_dict["category"],
            json.dumps(analysis_dict.get("pain_points", [])),
            json.dumps(analysis_dict.get("feature_requests", [])),
            analysis_dict.get("opportunity_score", 0.0),
            analysis_dict.get("business_impact_score", 0.0)
        )
    )
    conn.commit()
    conn.close()

def get_uploaded_reports():
    """Gets all uploaded reports sorted by date descending."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM uploaded_reports ORDER BY id DESC;", conn)
    conn.close()
    return df

def get_report_details(report_id):
    """Returns the details of a single report."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, uploaded_at, status, summary_json FROM uploaded_reports WHERE id = ?;", (report_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "filename": row[0],
            "uploaded_at": row[1],
            "status": row[2],
            "summary_json": json.loads(row[3]) if row[3] else None
        }
    return None

def get_feedback_and_analysis(report_id):
    """Gets all feedback and analysis results for a report as a DataFrame."""
    conn = get_connection()
    query = """
        SELECT 
            cf.id as feedback_id,
            cf.customer_id,
            cf.created_at as feedback_date,
            cf.feedback_text,
            ar.sentiment,
            ar.sentiment_score,
            ar.category,
            ar.pain_points_json,
            ar.feature_requests_json,
            ar.opportunity_score,
            ar.business_impact_score
        FROM customer_feedback cf
        LEFT JOIN analysis_results ar ON cf.id = ar.feedback_id
        WHERE cf.report_id = ?;
    """
    df = pd.read_sql_query(query, conn, params=(report_id,))
    conn.close()
    
    # Parse JSON columns back to Python objects
    if not df.empty:
        df["pain_points"] = df["pain_points_json"].apply(lambda x: json.loads(x) if x else [])
        df["feature_requests"] = df["feature_requests_json"].apply(lambda x: json.loads(x) if x else [])
    else:
        df["pain_points"] = []
        df["feature_requests"] = []
        
    return df

def save_generated_report(report_id, pdf_path):
    """Saves the path of a generated PDF report."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO generated_reports (report_id, generated_at, pdf_path) VALUES (?, ?, ?);",
        (report_id, now_str, pdf_path)
    )
    conn.commit()
    conn.close()

def get_generated_reports(report_id):
    """Gets all generated report PDF paths for a report."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, generated_at, pdf_path FROM generated_reports WHERE report_id = ? ORDER BY id DESC;", (report_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "generated_at": r[1], "pdf_path": r[2]} for r in rows]

def delete_uploaded_report(report_id):
    """Deletes a report and all its associated feedback, analysis, and report paths (cascading)."""
    # First get generated report files to delete them from disk if needed
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pdf_path FROM generated_reports WHERE report_id = ?;", (report_id,))
    pdf_paths = [r[0] for r in cursor.fetchall()]
    
    # Delete database record
    cursor.execute("DELETE FROM uploaded_reports WHERE id = ?;", (report_id,))
    conn.commit()
    conn.close()
    
    # Delete files from disk
    for path in pdf_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error removing file {path}: {e}")

# Initialize database on import
init_db()
