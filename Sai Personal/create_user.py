import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Check if 'admin' user already exists
cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
existing_user = cursor.fetchone()

if existing_user:
    print("User 'admin' already exists!")
else:
    # Insert user if not exists
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                   ("admin", "admin123", "admin"))
    conn.commit()
    print("User 'admin' created successfully!")

# Close the connection
conn.close()