from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask import send_from_directory
import sqlite3
import io
from flask import send_file
import pytesseract
import pandas as pd
from PIL import Image
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re  # Import the 're' module

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Define UPLOAD_FOLDER before using it
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ Ensure the directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Function to clean filenames (remove spaces and special characters)
def clean_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.]', '_', filename)

@app.route('/upload-pan', methods=['POST'])
def upload_pan():
    if 'pan_image' not in request.files:
        return "No file part"

    file = request.files['pan_image']
    if file.filename == '':
        return "No selected file"

    # ✅ Secure filename
    secure_filename = clean_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename)
    file.save(file_path)

    return f"Uploaded successfully: {secure_filename}"

@app.route('/view-pan/<filename>')
def view_pan_by_filename(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download-pan/<filename>')
def download_pan(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Initialize Database
def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS vendors (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    firm_name TEXT, father_name TEXT, dob TEXT,
                                    gender TEXT, nationality TEXT, mobile TEXT,
                                    email TEXT, legal_status TEXT, gstin TEXT,
                                    pan_number TEXT, pf_number TEXT, pan_image TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT UNIQUE, password TEXT)''')
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                           ('admin', generate_password_hash('admin123')))
        conn.commit()

init_db()

# Home Route
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT firm_name, pan_number FROM vendors")
        vendors = cursor.fetchall()
    return render_template("home.html", vendors=vendors)

# User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                flash("User registered successfully!", "success")
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")
    return render_template("register.html")

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):
                session['user'] = username
                return redirect(url_for('home'))
            else:
                flash("Invalid Credentials", "danger")
    return render_template("login.html")

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Vendor Registration
@app.route('/vendor_registration', methods=['GET', 'POST'])
def vendor_registration():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        firm_name = request.form['firm_name']
        father_name = request.form['father_name']
        dob = request.form['dob']
        gender = request.form['gender']
        nationality = request.form['nationality']
        mobile = request.form['mobile']
        email = request.form['email']
        legal_status = request.form['legal_status']
        gstin = request.form['gstin']
        pan_number = request.form['pan_number']
        pf_number = request.form['pf_number']

        # Handle PAN Image Upload
        pan_image = request.files['pan_image']
        if pan_image:
            pan_image_filename = clean_filename(pan_image.filename)
            pan_image_path = os.path.join(UPLOAD_FOLDER, pan_image_filename)
            pan_image.save(pan_image_path)
        else:
            pan_image_path = None

        # Save Data to Database
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vendors (firm_name, father_name, dob, gender, nationality, mobile, email, legal_status, gstin, pan_number, pf_number, pan_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (firm_name, father_name, dob, gender, nationality, mobile, email, legal_status, gstin, pan_number, pf_number, pan_image_path))
            conn.commit()

        flash("Registered Successfully!", "success")
        return redirect(url_for('vendor_registration'))
    return render_template('vendor_registration.html')

# Data Management System
@app.route('/data_management')
def data_management():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, firm_name, pan_number FROM vendors")
        vendors = cursor.fetchall()
    return render_template("data_management.html", vendors=vendors)

# PAN Verification Route
@app.route('/pan_verification')
def pan_verification():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, firm_name, pan_number, pan_image FROM vendors")
        vendors = cursor.fetchall()
    return render_template("pan_verification.html", vendors=vendors)

# AJAX PAN Verification Endpoint
@app.route('/verify_pan_ajax', methods=['POST'])
def verify_pan_ajax():
    data = request.get_json()
    vendor_id = data.get('vendor_id')
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pan_number, pan_image FROM vendors WHERE id=?", (vendor_id,))
        vendor = cursor.fetchone()

    if vendor:
        stored_pan, pan_image_path = vendor
        if pan_image_path and os.path.exists(pan_image_path):
            try:
                extracted_text = pytesseract.image_to_string(Image.open(pan_image_path)).strip().upper()
                print("extracted Text")
                stored_pan = stored_pan.strip().upper()
                verification_status = "Matched" if stored_pan in extracted_text else "Not Matched"
                return jsonify({"status": verification_status})
            except Exception as e:
                return jsonify({"status": f"Error processing image: {str(e)}"})
        else:
            return jsonify({"status": "Error: PAN image not found"})

    return jsonify({"status": "Error: Vendor not found"})

@app.route('/view_pan/<int:vendor_id>')
def view_pan(vendor_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pan_image FROM vendors WHERE id=?", (vendor_id,))
        vendor_data = cursor.fetchone()
        if vendor_data and vendor_data[0]:
            image_path = vendor_data[0]
            # Assuming images are stored directly in the UPLOAD_FOLDER
            return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(image_path))
        else:
            return "Image not found.", 404

# Route to display all registered vendors
@app.route('/all_vendors')
def all_vendors():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors")
        vendors = cursor.fetchall()
    return render_template('all_vendors.html', vendors=vendors)

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/vendor-list')
def vendor_list():
    return render_template('vendor_list.html')  # Create vendor_list.html for the UI

# Sample data (replace with database query)
vendors = [
    {"name": "John Doe", "email": "john@example.com", "phone": "9876543210", "firm": "ABC Ltd", "gstin": "22AAAAA0000A1Z5"},
    {"name": "Jane Smith", "email": "jane@example.com", "phone": "9123456789", "firm": "XYZ Pvt Ltd", "gstin": "33BBBBB0000B1Z6"},
]

@app.route('/download-report')
def download_report():
    df = pd.DataFrame(vendors)

    # Save as CSV
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name="vendors.csv")

@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html exists

@app.route('/extract-data', methods=['GET', 'POST'])
def extract_data():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Save and extract text
        filename = clean_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            extracted_text = pytesseract.image_to_string(Image.open(file_path))
            return render_template('extract.html', extracted_text=extracted_text)
        except Exception as e:
            flash(f"Error processing image: {str(e)}", "error")
            return render_template('extract.html', extracted_text=None)

    return render_template('extract.html', extracted_text=None)

@app.route('/extract-father-name-page')
def extract_father_name_page():
    return render_template('extract_father_name.html')

@app.route('/extract-father-name', methods=['POST'])
def extract_father_name():
    if 'pan_image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['pan_image']
    image = Image.open(file)
    text = pytesseract.image_to_string(image)

    # Clean and split lines
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    # Try better logic to extract father's name (e.g., look for label)
    father_name = "Not Found"
    for i, line in enumerate(lines):
        if "Father" in line or "FATHER" in line:
            if i + 1 < len(lines):
                father_name = lines[i + 1]
            break
        elif i == 1:  # fallback to second line
            father_name = line

    return jsonify({'father_name': father_name})


if __name__ == "__main__":
    app.run(debug=True)