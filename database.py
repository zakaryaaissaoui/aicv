import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "talentflow.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create candidates table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        education TEXT, -- Store JSON list of education entries
        experience_years REAL DEFAULT 0,
        experience_details TEXT, -- Store JSON list of experience entries
        skills TEXT, -- Comma-separated list of skills
        languages TEXT, -- Comma-separated list of languages
        wilaya TEXT,
        ai_score INTEGER DEFAULT 0,
        ai_summary TEXT,
        strengths TEXT, -- Store JSON list of strengths
        weaknesses TEXT, -- Store JSON list of weaknesses
        pipeline_stage TEXT DEFAULT 'New', -- New, Reviewed, Interview, Test, Accepted, Rejected
        notes TEXT DEFAULT '',
        file_name TEXT,
        file_hash TEXT UNIQUE,
        file_content_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

def add_candidate(candidate_data):
    """
    candidate_data is a dictionary containing:
    name, phone, email, education (list/str), experience_years, experience_details (list/str),
    skills (list/str), languages (list/str), wilaya, ai_score, ai_summary, strengths (list),
    weaknesses (list), file_name, file_hash, file_content_text
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for exact hash duplicate
    cursor.execute("SELECT id FROM candidates WHERE file_hash = ?", (candidate_data.get("file_hash"),))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Duplicate detected: File hash already exists in database.")
    
    # Convert lists to JSON or comma-separated strings
    education = json.dumps(candidate_data.get("education", []))
    experience_details = json.dumps(candidate_data.get("experience_details", []))
    
    skills = candidate_data.get("skills", [])
    if isinstance(skills, list):
        skills = ", ".join(skills)
        
    languages = candidate_data.get("languages", [])
    if isinstance(languages, list):
        languages = ", ".join(languages)
        
    strengths = json.dumps(candidate_data.get("strengths", []))
    weaknesses = json.dumps(candidate_data.get("weaknesses", []))
    
    cursor.execute("""
    INSERT INTO candidates (
        name, phone, email, education, experience_years, experience_details,
        skills, languages, wilaya, ai_score, ai_summary, strengths, weaknesses,
        pipeline_stage, notes, file_name, file_hash, file_content_text
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        candidate_data.get("name"),
        candidate_data.get("phone"),
        candidate_data.get("email"),
        education,
        candidate_data.get("experience_years", 0),
        experience_details,
        skills,
        languages,
        candidate_data.get("wilaya"),
        candidate_data.get("ai_score", 0),
        candidate_data.get("ai_summary"),
        strengths,
        weaknesses,
        candidate_data.get("pipeline_stage", "New"),
        candidate_data.get("notes", ""),
        candidate_data.get("file_name"),
        candidate_data.get("file_hash"),
        candidate_data.get("file_content_text")
    ))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_candidate(candidate_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        candidate = dict(row)
        # Parse JSON fields back to lists
        candidate["education"] = json.loads(candidate["education"]) if candidate["education"] else []
        candidate["experience_details"] = json.loads(candidate["experience_details"]) if candidate["experience_details"] else []
        candidate["strengths"] = json.loads(candidate["strengths"]) if candidate["strengths"] else []
        candidate["weaknesses"] = json.loads(candidate["weaknesses"]) if candidate["weaknesses"] else []
        return candidate
    return None

def get_all_candidates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    candidates = []
    for row in rows:
        cand = dict(row)
        cand["education"] = json.loads(cand["education"]) if cand["education"] else []
        cand["experience_details"] = json.loads(cand["experience_details"]) if cand["experience_details"] else []
        cand["strengths"] = json.loads(cand["strengths"]) if cand["strengths"] else []
        cand["weaknesses"] = json.loads(cand["weaknesses"]) if cand["weaknesses"] else []
        candidates.append(cand)
    return candidates

def update_candidate_stage(candidate_id, new_stage):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET pipeline_stage = ? WHERE id = ?", (new_stage, candidate_id))
    conn.commit()
    conn.close()

def update_candidate_notes(candidate_id, notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET notes = ? WHERE id = ?", (notes, candidate_id))
    conn.commit()
    conn.close()

def delete_candidate(candidate_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()

def check_duplicate_by_hash(file_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM candidates WHERE file_hash = ?", (file_hash,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "name": row["name"]}
    return None

def check_duplicate_by_email_or_phone(email, phone):
    if not email and not phone:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if email and phone:
        cursor.execute("SELECT id, name, email, phone FROM candidates WHERE email = ? OR phone = ?", (email, phone))
    elif email:
        cursor.execute("SELECT id, name, email FROM candidates WHERE email = ?", (email,))
    else:
        cursor.execute("SELECT id, name, phone FROM candidates WHERE phone = ?", (phone,))
        
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "name": row["name"], "match_type": "email/phone"}
    return None

if __name__ == "__main__":
    init_db()
