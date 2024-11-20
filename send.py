import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Connect to the SQLite database
db_path = "movie_watchers.db"  # Replace with your database path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the current date
# current_date = datetime.now().strftime("%Y-%m-%d")
current_date = datetime.now().day

# Query the movie for today's date
cursor.execute("SELECT movie_name FROM movies WHERE date_using = ?", (current_date,))
movie = cursor.fetchone()

if movie:
    movie_name = movie[0]
    message_body = f"""
1. Did you watch? ('1 Y' for yes, '1 N' for no).

2. '2 [rating]' (1 through 10).

3. '3 [word]' (Describe in 1 word).

Thanks!
"""

    # Query all watchers
    cursor.execute("SELECT name, phone_number FROM watchers WHERE name = 'Reed'")
    watchers = cursor.fetchall()

    # Set up the SMTP server (use your email provider's settings)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_address = "reedwrogers@gmail.com"  # Replace with your email
    email_password = "pwd"  # Replace with your email password

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)

        # Send messages to all watchers
        for watcher in watchers:
            name, phone_number = watcher
            to_address = f"{phone_number}@txt.att.net"  # For AT&T; adjust for other carriers
            
            msg = MIMEText(message_body)
            msg['Subject'] = f"Today's Movie: {movie_name}"
            msg['From'] = email_address
            msg['To'] = to_address

            server.sendmail(email_address, to_address, msg.as_string())
            print(f"Message sent to {name} at {phone_number}")
else:
    print("No movie scheduled for today.")

# Close the database connection
conn.close()

