# 🧾 PAN Card Upload & Viewer – Flask Web App

This is a Flask-based web application that allows users to upload, view, and download images of PAN (Permanent Account Number) cards. It's designed with secure file handling, sanitized uploads, and a simple, extensible architecture.

---

## 🚀 Features

- ✅ Upload PAN card images (`.jpg`, `.jpeg`, `.png`)
- ✅ View uploaded PAN card images in the browser
- ✅ Download images through secure routes
- ✅ Automatic filename sanitization (removes special characters)
- ✅ Secure file storage in a dedicated directory
- ✅ Easily extensible with OCR (using pytesseract) and authentication modules

---

## 📂 Folder Structure

pan-card-app/ │ ├── static/ │ └── uploads/ # Stores uploaded PAN card images │ ├── templates/ # (Optional) HTML templates for frontend │ ├── app.py # Main Flask application ├── requirements.txt # Project dependencies └── README.md # Project documentation

markdown
Copy
Edit

---

## 🛠 Tech Stack

- **Backend**: Python, Flask
- **Image Handling**: Pillow (`PIL`), `pytesseract` (optional for OCR)
- **Security**: `werkzeug.security`, regular expressions (`re`)
- **Data Handling**: SQLite (can be added for login/user features)
- **File I/O**: `os`, `io`, Flask’s `send_from_directory` & `send_file`

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pan-card-flask-app.git
cd pan-card-flask-app
2. Create Virtual Environment (Recommended)
bash
Copy
Edit
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
Note: If requirements.txt is missing, install manually:

bash
Copy
Edit
pip install flask pillow pytesseract
4. Run the App
bash
Copy
Edit
python app.py
The app will be available at: http://127.0.0.1:5000/

📌 API Routes

Method	Route	Description
POST	/upload-pan	Upload a PAN card image
GET	/view-pan/<filename>	View a PAN image in browser
GET	/download-pan/<filename>	Download a PAN image
🧠 How It Works
User uploads an image via /upload-pan.

The filename is sanitized to remove any special characters.

The image is saved to the /static/uploads directory.

It can be viewed or downloaded securely via routes using the filename.

🔒 Security Notes
Filenames are cleaned using a regex to prevent directory traversal or invalid characters.

You can extend this with login/auth using Flask-Login for user-based uploads.

Use HTTPS in production to ensure secure transmission.

🎯 Future Enhancements
📝 OCR Integration: Auto-read PAN number from image using pytesseract

👤 User Authentication: Add login/registration with hashed passwords

🗃️ Database Storage: Link uploaded files to user records

🌐 Frontend UI: Use HTML templates (Jinja2) or a frontend framework

🧪 Unit Testing: Add test coverage for routes and security

📸 Sample Upload Flow
Upload File:
POST /upload-pan with a file named pan_image.

View File:
Navigate to /view-pan/your_filename.jpg

Download File:
Navigate to /download-pan/your_filename.jpg

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

📄 License
This project is open source and available under the MIT License.

🙌 Acknowledgements
Flask

Pillow (PIL)

pytesseract
