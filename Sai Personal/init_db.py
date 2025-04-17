from app import app, db  # Import the Flask app and database

with app.app_context():  # Ensure we are in an application context
    db.create_all()  # Create all database tables
    print("Database initialized successfully!")