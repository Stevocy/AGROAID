import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'agroaid.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            icon TEXT DEFAULT 'fa-seedling'
        );

        CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            severity TEXT DEFAULT 'Moderate',
            FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER NOT NULL,
            treatment_type TEXT NOT NULL,
            description TEXT NOT NULL,
            priority INTEGER DEFAULT 1,
            FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER NOT NULL,
            confidence_score REAL DEFAULT 1.0,
            FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS rule_symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id INTEGER NOT NULL,
            symptom_id INTEGER NOT NULL,
            FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE,
            FOREIGN KEY (symptom_id) REFERENCES symptoms(id) ON DELETE CASCADE
        );
    ''')

    conn.commit()
    conn.close()

# ─── Crops ────────────────────────────────────────────────────────────────────

def get_all_crops():
    conn = get_db()
    crops = conn.execute('SELECT * FROM crops ORDER BY name').fetchall()
    conn.close()
    return crops

def get_crop(crop_id):
    conn = get_db()
    crop = conn.execute('SELECT * FROM crops WHERE id=?', (crop_id,)).fetchone()
    conn.close()
    return crop

def add_crop(name, description, icon):
    conn = get_db()
    conn.execute('INSERT INTO crops (name, description, icon) VALUES (?,?,?)', (name, description, icon))
    conn.commit()
    conn.close()

def update_crop(crop_id, name, description, icon):
    conn = get_db()
    conn.execute('UPDATE crops SET name=?, description=?, icon=? WHERE id=?', (name, description, icon, crop_id))
    conn.commit()
    conn.close()

def delete_crop(crop_id):
    conn = get_db()
    conn.execute('DELETE FROM crops WHERE id=?', (crop_id,))
    conn.commit()
    conn.close()

# ─── Symptoms ─────────────────────────────────────────────────────────────────

def get_symptoms_for_crop(crop_id):
    conn = get_db()
    symptoms = conn.execute('SELECT * FROM symptoms WHERE crop_id=? ORDER BY name', (crop_id,)).fetchall()
    conn.close()
    return symptoms

def get_all_symptoms():
    conn = get_db()
    rows = conn.execute('''
        SELECT s.*, c.name as crop_name
        FROM symptoms s JOIN crops c ON s.crop_id=c.id
        ORDER BY c.name, s.name
    ''').fetchall()
    conn.close()
    return rows

def get_symptom(symptom_id):
    conn = get_db()
    s = conn.execute('SELECT * FROM symptoms WHERE id=?', (symptom_id,)).fetchone()
    conn.close()
    return s

def add_symptom(crop_id, name, description):
    conn = get_db()
    conn.execute('INSERT INTO symptoms (crop_id, name, description) VALUES (?,?,?)', (crop_id, name, description))
    conn.commit()
    conn.close()

def update_symptom(symptom_id, crop_id, name, description):
    conn = get_db()
    conn.execute('UPDATE symptoms SET crop_id=?, name=?, description=? WHERE id=?', (crop_id, name, description, symptom_id))
    conn.commit()
    conn.close()

def delete_symptom(symptom_id):
    conn = get_db()
    conn.execute('DELETE FROM symptoms WHERE id=?', (symptom_id,))
    conn.commit()
    conn.close()

# ─── Diseases ─────────────────────────────────────────────────────────────────

def get_diseases_for_crop(crop_id):
    conn = get_db()
    diseases = conn.execute('SELECT * FROM diseases WHERE crop_id=? ORDER BY name', (crop_id,)).fetchall()
    conn.close()
    return diseases

def get_all_diseases():
    conn = get_db()
    rows = conn.execute('''
        SELECT d.*, c.name as crop_name
        FROM diseases d JOIN crops c ON d.crop_id=c.id
        ORDER BY c.name, d.name
    ''').fetchall()
    conn.close()
    return rows

def get_disease(disease_id):
    conn = get_db()
    d = conn.execute('SELECT * FROM diseases WHERE id=?', (disease_id,)).fetchone()
    conn.close()
    return d

def add_disease(crop_id, name, description, severity):
    conn = get_db()
    conn.execute('INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)', (crop_id, name, description, severity))
    conn.commit()
    conn.close()

def update_disease(disease_id, crop_id, name, description, severity):
    conn = get_db()
    conn.execute('UPDATE diseases SET crop_id=?, name=?, description=?, severity=? WHERE id=?', (crop_id, name, description, severity, disease_id))
    conn.commit()
    conn.close()

def delete_disease(disease_id):
    conn = get_db()
    conn.execute('DELETE FROM diseases WHERE id=?', (disease_id,))
    conn.commit()
    conn.close()

# ─── Treatments ───────────────────────────────────────────────────────────────

def get_treatments_for_disease(disease_id):
    conn = get_db()
    treatments = conn.execute('SELECT * FROM treatments WHERE disease_id=? ORDER BY priority', (disease_id,)).fetchall()
    conn.close()
    return treatments

def get_all_treatments():
    conn = get_db()
    rows = conn.execute('''
        SELECT t.*, d.name as disease_name
        FROM treatments t JOIN diseases d ON t.disease_id=d.id
        ORDER BY d.name, t.priority
    ''').fetchall()
    conn.close()
    return rows

def add_treatment(disease_id, treatment_type, description, priority):
    conn = get_db()
    conn.execute('INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)', (disease_id, treatment_type, description, priority))
    conn.commit()
    conn.close()

def delete_treatment(treatment_id):
    conn = get_db()
    conn.execute('DELETE FROM treatments WHERE id=?', (treatment_id,))
    conn.commit()
    conn.close()

# ─── Rules ────────────────────────────────────────────────────────────────────

def get_all_rules():
    conn = get_db()
    rows = conn.execute('''
        SELECT r.id, r.confidence_score, d.name as disease_name, c.name as crop_name
        FROM rules r
        JOIN diseases d ON r.disease_id=d.id
        JOIN crops c ON d.crop_id=c.id
        ORDER BY c.name, d.name
    ''').fetchall()
    conn.close()
    return rows

def get_rules_for_crop(crop_id):
    """Return rules with their symptom lists for a given crop."""
    conn = get_db()
    rules = conn.execute('''
        SELECT r.id, r.disease_id, r.confidence_score
        FROM rules r
        JOIN diseases d ON r.disease_id=d.id
        WHERE d.crop_id=?
    ''', (crop_id,)).fetchall()

    result = []
    for rule in rules:
        symptom_ids = [row['symptom_id'] for row in conn.execute(
            'SELECT symptom_id FROM rule_symptoms WHERE rule_id=?', (rule['id'],)
        ).fetchall()]
        result.append({
            'id': rule['id'],
            'disease_id': rule['disease_id'],
            'confidence_score': rule['confidence_score'],
            'symptom_ids': symptom_ids
        })
    conn.close()
    return result

def add_rule(disease_id, confidence_score, symptom_ids):
    conn = get_db()
    cur = conn.execute('INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)', (disease_id, confidence_score))
    rule_id = cur.lastrowid
    for sid in symptom_ids:
        conn.execute('INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)', (rule_id, sid))
    conn.commit()
    conn.close()

def delete_rule(rule_id):
    conn = get_db()
    conn.execute('DELETE FROM rules WHERE id=?', (rule_id,))
    conn.commit()
    conn.close()

def get_rule_symptoms(rule_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT s.name FROM rule_symptoms rs
        JOIN symptoms s ON rs.symptom_id=s.id
        WHERE rs.rule_id=?
    ''', (rule_id,)).fetchall()
    conn.close()
    return [r['name'] for r in rows]
