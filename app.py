"""
AgroAid – Main Flask Application
"""
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import database as db
import inference_engine as ie

app = Flask(__name__)
app.secret_key = 'agroaid-secret-key-2026'

# ─── Initialize DB on startup ─────────────────────────────────────────────────
with app.app_context():
    db.init_db()

# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    crops = db.get_all_crops()
    return render_template('index.html', crops=crops)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/diagnose')
def diagnose_page():
    crop_id = request.args.get('crop_id', type=int)
    if not crop_id:
        return redirect(url_for('index'))
    crop = db.get_crop(crop_id)
    if not crop:
        flash('Crop not found.', 'error')
        return redirect(url_for('index'))
    symptoms = db.get_symptoms_for_crop(crop_id)
    return render_template('symptoms.html', crop=crop, symptoms=symptoms)

@app.route('/results', methods=['POST'])
def results():
    crop_id = request.form.get('crop_id', type=int)
    selected_ids = request.form.getlist('symptoms', type=int)

    if not crop_id:
        return redirect(url_for('index'))
    if not selected_ids:
        flash('Please select at least one symptom before proceeding.', 'warning')
        return redirect(url_for('diagnose_page', crop_id=crop_id))

    crop = db.get_crop(crop_id)
    symptoms = db.get_symptoms_for_crop(crop_id)
    selected_symptoms = [s for s in symptoms if s['id'] in selected_ids]
    diagnoses = ie.diagnose(crop_id, selected_ids)

    return render_template('results.html',
                           crop=crop,
                           selected_symptoms=selected_symptoms,
                           diagnoses=diagnoses)

# ─── JSON API endpoints ───────────────────────────────────────────────────────

@app.route('/api/crops')
def api_crops():
    crops = db.get_all_crops()
    return jsonify([dict(c) for c in crops])

@app.route('/api/symptoms/<int:crop_id>')
def api_symptoms(crop_id):
    symptoms = db.get_symptoms_for_crop(crop_id)
    return jsonify([dict(s) for s in symptoms])

@app.route('/api/diagnose', methods=['POST'])
def api_diagnose():
    data = request.get_json()
    crop_id = data.get('crop_id')
    symptom_ids = data.get('symptom_ids', [])
    if not crop_id or not symptom_ids:
        return jsonify({'error': 'crop_id and symptom_ids are required'}), 400
    results = ie.diagnose(crop_id, symptom_ids)
    return jsonify(results)

# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':  # Simple hardcoded admin check
            session['logged_in'] = True
            flash('Successfully logged in.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    crops = db.get_all_crops()
    diseases = db.get_all_diseases()
    symptoms = db.get_all_symptoms()
    rules = db.get_all_rules()
    treatments = db.get_all_treatments()
    return render_template('admin/dashboard.html',
                           crops=crops,
                           diseases=diseases,
                           symptoms=symptoms,
                           rules=rules,
                           treatments=treatments)

# ── Crops CRUD ──
@app.route('/admin/crops', methods=['GET', 'POST'])
@login_required
def admin_crops():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            db.add_crop(
                request.form['name'],
                request.form.get('description', ''),
                request.form.get('icon', 'fa-seedling')
            )
            flash(f"Crop '{request.form['name']}' added successfully.", 'success')
        elif action == 'edit':
            db.update_crop(
                int(request.form['crop_id']),
                request.form['name'],
                request.form.get('description', ''),
                request.form.get('icon', 'fa-seedling')
            )
            flash('Crop updated successfully.', 'success')
        elif action == 'delete':
            db.delete_crop(int(request.form['crop_id']))
            flash('Crop deleted.', 'success')
        return redirect(url_for('admin_crops'))
    crops = db.get_all_crops()
    return render_template('admin/crops.html', crops=crops)

# ── Symptoms CRUD ──
@app.route('/admin/symptoms', methods=['GET', 'POST'])
@login_required
def admin_symptoms():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            db.add_symptom(
                int(request.form['crop_id']),
                request.form['name'],
                request.form.get('description', '')
            )
            flash('Symptom added successfully.', 'success')
        elif action == 'edit':
            db.update_symptom(
                int(request.form['symptom_id']),
                int(request.form['crop_id']),
                request.form['name'],
                request.form.get('description', '')
            )
            flash('Symptom updated successfully.', 'success')
        elif action == 'delete':
            db.delete_symptom(int(request.form['symptom_id']))
            flash('Symptom deleted.', 'success')
        return redirect(url_for('admin_symptoms'))
    symptoms = db.get_all_symptoms()
    crops = db.get_all_crops()
    return render_template('admin/symptoms.html', symptoms=symptoms, crops=crops)

# ── Diseases CRUD ──
@app.route('/admin/diseases', methods=['GET', 'POST'])
@login_required
def admin_diseases():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            db.add_disease(
                int(request.form['crop_id']),
                request.form['name'],
                request.form.get('description', ''),
                request.form.get('severity', 'Moderate')
            )
            flash('Disease added successfully.', 'success')
        elif action == 'edit':
            db.update_disease(
                int(request.form['disease_id']),
                int(request.form['crop_id']),
                request.form['name'],
                request.form.get('description', ''),
                request.form.get('severity', 'Moderate')
            )
            flash('Disease updated successfully.', 'success')
        elif action == 'delete':
            db.delete_disease(int(request.form['disease_id']))
            flash('Disease deleted.', 'success')
        return redirect(url_for('admin_diseases'))
    diseases = db.get_all_diseases()
    crops = db.get_all_crops()
    return render_template('admin/diseases.html', diseases=diseases, crops=crops)

# ── Treatments CRUD ──
@app.route('/admin/treatments', methods=['GET', 'POST'])
@login_required
def admin_treatments():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            db.add_treatment(
                int(request.form['disease_id']),
                request.form['treatment_type'],
                request.form['description'],
                int(request.form.get('priority', 1))
            )
            flash('Treatment added successfully.', 'success')
        elif action == 'delete':
            db.delete_treatment(int(request.form['treatment_id']))
            flash('Treatment deleted.', 'success')
        return redirect(url_for('admin_treatments'))
    treatments = db.get_all_treatments()
    diseases = db.get_all_diseases()
    return render_template('admin/treatments.html', treatments=treatments, diseases=diseases)

# ── Rules CRUD ──
@app.route('/admin/rules', methods=['GET', 'POST'])
@login_required
def admin_rules():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            disease_id = int(request.form['disease_id'])
            confidence = float(request.form.get('confidence_score', 0.9))
            symptom_ids = request.form.getlist('symptom_ids', type=int)
            if not symptom_ids:
                flash('A rule must have at least one symptom condition.', 'error')
            else:
                db.add_rule(disease_id, confidence, symptom_ids)
                flash('Rule added successfully.', 'success')
        elif action == 'delete':
            db.delete_rule(int(request.form['rule_id']))
            flash('Rule deleted.', 'success')
        return redirect(url_for('admin_rules'))
    rules = db.get_all_rules()
    diseases = db.get_all_diseases()
    symptoms = db.get_all_symptoms()
    # Attach symptom names to each rule
    rules_with_symptoms = []
    for rule in rules:
        rule_sym_names = db.get_rule_symptoms(rule['id'])
        rules_with_symptoms.append({**dict(rule), 'symptom_names': rule_sym_names})
    return render_template('admin/rules.html',
                           rules=rules_with_symptoms,
                           diseases=diseases,
                           symptoms=symptoms)

# ─── API: get symptoms by crop (for admin rule form dynamic load) ──────────────
@app.route('/api/admin/symptoms_by_disease/<int:disease_id>')
@login_required
def api_symptoms_by_disease(disease_id):
    disease = db.get_disease(disease_id)
    if not disease:
        return jsonify([])
    symptoms = db.get_symptoms_for_crop(disease['crop_id'])
    return jsonify([dict(s) for s in symptoms])

if __name__ == '__main__':
    from seed_data import seed
    seed()
    app.run(debug=True, port=5000)
