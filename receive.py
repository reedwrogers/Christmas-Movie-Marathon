import sqlite3
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import re

# Database connection
db_path = "./movie_watchers.db"  # Replace with your database path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Email connection
imap_server = "imap.gmail.com"
email_address = "reedwrogers@gmail.com"  # Replace with your email
email_password = "tabq wbts lena trwu"  # Replace with your email password

with imaplib.IMAP4_SSL(imap_server) as mail:
    mail.login(email_address, email_password)
    mail.select("inbox")

    # Search for all unseen messages
    status, messages = mail.search(None, 'UNSEEN')

    for msg_id in messages[0].split():
        # Fetch the email
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header(msg["Subject"])[0][0]
                sender = msg["From"]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                # If the message has a plain text part
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                # Parse the response
                response_match = re.match(r"(\d+) (.+)", body.strip())
                if response_match:
                    response_type = int(response_match.group(1))
                    response = response_match.group(2).strip('\r')

                    # Lookup watcher ID and movie from the sender
                    phone_number = re.search(r"(\d+)@txt.att.net", sender).group(1)
                    cursor.execute("SELECT rowid FROM watchers WHERE phone_number = ?", (phone_number,))
                    watcher_id = cursor.fetchone()
                
                    if watcher_id:
                        watcher_id = watcher_id[0]
                        cursor.execute("SELECT movie_name FROM movies WHERE date_using = ?", (datetime.now().day - 1,)) # "1" here should be the current day
                        movie = cursor.fetchone()


                        if movie:
                            movie_name = subject.split(": ", 1)[-1]
                            print(movie_name)
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # Insert the response into the database
                            cursor.execute("""
                                INSERT INTO responses (watcher_id, response_type, response, timestamp, movie_name)
                                VALUES (?, ?, ?, ?, ?)
                            """, (watcher_id, response_type, response, timestamp, movie_name))
                            conn.commit()
                            print(f"Response saved: {response_type}, {response}")
                else:
                    print("Unrecognized response format.")

    mail.logout()

# Close the database connection
conn.close()
