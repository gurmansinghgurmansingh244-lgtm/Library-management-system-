
import streamlit as st
import mysql.connector
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
from datetime import date, timedelta
from io import BytesIO

st.set_page_config(
    page_title="Smart Library",
    layout="wide"
)

# ---------------- DATABASE CONNECTION ----------------

def get_db():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        ssl_disabled=False
    )

def init_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Books (
        book_id VARCHAR(50) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        author VARCHAR(255),
        subject VARCHAR(150),
        tags TEXT,
        description TEXT,
        pdf_data LONGBLOB,
        total_copies INT DEFAULT 1,
        available_copies INT DEFAULT 1,
        popularity INT DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        roll_no VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Issues (
        issue_id INT AUTO_INCREMENT PRIMARY KEY,
        roll_no VARCHAR(50),
        book_id VARCHAR(50),
        issue_date DATE,
        due_date DATE,
        return_date DATE NULL,
        status VARCHAR(30) DEFAULT 'Issued'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ReminderLogs (
        log_id INT AUTO_INCREMENT PRIMARY KEY,
        issue_id INT,
        reminder_date DATE,
        UNIQUE KEY unique_reminder (issue_id, reminder_date)
    )
    """)

    db.commit()
    cur.close()
    db.close()

# ---------------- DATABASE HELPERS ----------------

def query(sql, values=None, fetch=True):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, values or ())
    result = cur.fetchall() if fetch else None
    if not fetch:
        db.commit()
    cur.close()
    db.close()
    return result

def execute(sql, values=None):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, values or ())
    db.commit()
    cur.close()
    db.close()

def get_stats():
    books = query("SELECT COUNT(*) AS n FROM Books")[0]["n"]
    available = query(
        "SELECT COALESCE(SUM(available_copies),0) AS n FROM Books"
    )[0]["n"]
    issued = query(
        "SELECT COUNT(*) AS n FROM Issues WHERE status='Issued'"
    )[0]["n"]
    students = query("SELECT COUNT(*) AS n FROM Students")[0]["n"]
    return books, available, issued, students

# ---------------- EMAIL REMINDER ----------------

def send_email(to_email, subject, body):
    cfg = st.secrets["gmail"]

    msg = EmailMessage()
    msg["From"] = cfg["sender"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, context=context
    ) as server:
        server.login(cfg["sender"], cfg["app_password"])
        server.send_message(msg)

# ---------------- START APPLICATION ----------------

st.title(" Smart Library Management System")
st.caption("Smart Book Management | Student Records | AI Recommendations")

try:
    init_db()
except Exception as e:
    st.error("Database connection failed. Check your database settings.")
    st.stop()

# ---------------- SIDEBAR ----------------

menu = st.sidebar.radio(
    "MAIN MENU",
    [
        "Home Dashboard",
        "Add New Book",
        "Register Student",
        "Search Books",
        "Issue Book",
        "Return Book",
        "Issue Records",
        "AI Recommendations",
        "Email Reminders"
    ]
)

# ---------------- HOME DASHBOARD ----------------

if menu == "Home Dashboard":
    st.header("Library Dashboard")

    try:
        b, a, i, s = get_stats()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Books", b)
        c2.metric("Available Copies", a)
        c3.metric("Issued Books", i)
        c4.metric("Total Students", s)

        st.subheader("Recent Issue Records")

        records = query("""
            SELECT I.issue_id, I.roll_no, S.name,
                   I.book_id, B.title, I.issue_date,
                   I.due_date, I.status
            FROM Issues I
            LEFT JOIN Students S ON I.roll_no=S.roll_no
            LEFT JOIN Books B ON I.book_id=B.book_id
            ORDER BY I.issue_id DESC LIMIT 10
        """)

        if records:
            st.dataframe(pd.DataFrame(records), use_container_width=True)
        else:
            st.info("No issue records available yet.")

    except Exception:
        st.error("Unable to load dashboard.")

# ---------------- ADD NEW BOOK ----------------

elif menu == "Add New Book":
    st.header("Add New Book")

    with st.form("book_form"):
        book_id = st.text_input("Book ID")
        title = st.text_input("Book Title")
        author = st.text_input("Author Name")
        subject = st.text_input("Subject / Category")
        tags = st.text_input("Tags (comma separated)")
        description = st.text_area("Book Description")
        copies = st.number_input("Total Copies", min_value=1, value=1)
        pdf = st.file_uploader("Upload Book PDF", type=["pdf"])

        submit = st.form_submit_button("Save Book")

    if submit:
        if not book_id.strip() or not title.strip():
            st.error("Book ID and Title are required.")
        else:
            try:
                pdf_data = pdf.getvalue() if pdf else None

                execute("""
                    INSERT INTO Books
                    (book_id,title,author,subject,tags,description,
                    pdf_data,total_copies,available_copies)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    book_id.strip(), title.strip(), author,
                    subject, tags, description, pdf_data,
                    copies, copies
                ))

                st.success("Book saved successfully!")

            except mysql.connector.IntegrityError:
                st.error("This Book ID already exists.")
            except Exception:
                st.error("Unable to save book. Check database connection.")

# ---------------- REGISTER STUDENT ----------------

elif menu == "Register Student":
    st.header(" Student Registration")

    with st.form("student_form"):
        name = st.text_input("Student Name")
        roll = st.text_input("University Roll Number")
        email = st.text_input("Student Email Address")

        submit = st.form_submit_button("Register Student")

    if submit:
        if not name.strip() or not roll.strip():
            st.error("Name and Roll Number are required.")
        else:
            try:
                execute("""
                    INSERT INTO Students (roll_no,name,email)
                    VALUES (%s,%s,%s)
                """, (roll.strip(), name.strip(), email.strip()))
                st.success("Student registered successfully!")
            except mysql.connector.IntegrityError:
                st.error("This Roll Number is already registered.")
            except Exception:
                st.error("Unable to register student.")

# ---------------- SEARCH BOOKS ----------------

elif menu == "Search Books":
    st.header(" Search Books")

    search = st.text_input("Enter Book ID, Title, Author or Subject")

    if search:
        pattern = "%" + search + "%"
        books = query("""
            SELECT book_id,title,author,subject,tags,
                   description,total_copies,available_copies
            FROM Books
            WHERE book_id LIKE %s OR title LIKE %s
            OR author LIKE %s OR subject LIKE %s
        """, (pattern, pattern, pattern, pattern))

    else:
        books = query("""
            SELECT book_id,title,author,subject,tags,
                   description,total_copies,available_copies
            FROM Books ORDER BY title
        """)

    if books:
        for book in books:
            with st.expander(
                f"{book['title']} | ID: {book['book_id']}"
            ):
                st.write("**Author:**", book["author"])
                st.write("**Subject:**", book["subject"])
                st.write("**Tags:**", book["tags"])
                st.write("**Description:**", book["description"])
                st.write("**Available Copies:**", book["available_copies"])

                pdf_result = query(
                    "SELECT pdf_data FROM Books WHERE book_id=%s",
                    (book["book_id"],)
                )

                if pdf_result and pdf_result[0]["pdf_data"]:
                    st.download_button(
                        " Download Book PDF",
                        data=bytes(pdf_result[0]["pdf_data"]),
                        file_name=book["book_id"] + ".pdf",
                        mime="application/pdf",
                        key="pdf_" + book["book_id"]
                    )
    else:
        st.info("No books found.")

# ---------------- ISSUE BOOK ----------------

elif menu == "Issue Book":
    st.header(" Issue Book")

    students = query("SELECT roll_no,name FROM Students")
    books = query("""
        SELECT book_id,title FROM Books
        WHERE available_copies > 0
    """)

    if not students:
        st.warning("Register students first.")
    elif not books:
        st.warning("No available books.")
    else:
        student_options = {
            f"{x['roll_no']} - {x['name']}": x["roll_no"]
            for x in students
        }

        book_options = {
            f"{x['book_id']} - {x['title']}": x["book_id"]
            for x in books
        }

        with st.form("issue_form"):
            selected_student = st.selectbox(
                "Select Student", list(student_options.keys())
            )
            selected_book = st.selectbox(
                "Select Book", list(book_options.keys())
            )
            issue_date = st.date_input("Issue Date", value=date.today())
            due_date = st.date_input(
                "Due Date", value=date.today() + timedelta(days=14)
            )

            submit = st.form_submit_button("Issue Book")

        if submit:
            roll = student_options[selected_student]
            book_id = book_options[selected_book]

            if due_date < issue_date:
                st.error("Due Date cannot be before Issue Date.")
            else:
                try:
                    execute("""
                        INSERT INTO Issues
                        (roll_no,book_id,issue_date,due_date,status)
                        VALUES (%s,%s,%s,%s,'Issued')
                    """, (roll, book_id, issue_date, due_date))

                    execute("""
                        UPDATE Books
                        SET available_copies=available_copies-1,
                            popularity=popularity+1
                        WHERE book_id=%s AND available_copies>0
                    """, (book_id,))

                    st.success("Book issued successfully!")
                except Exception:
                    st.error("Unable to issue this book.")

# ---------------- RETURN BOOK ----------------

elif menu == "Return Book":
    st.header("Return Book")

    active = query("""
        SELECT I.issue_id,I.roll_no,S.name,I.book_id,
               B.title,I.issue_date,I.due_date
        FROM Issues I
        JOIN Students S ON I.roll_no=S.roll_no
        JOIN Books B ON I.book_id=B.book_id
        WHERE I.status='Issued'
        ORDER BY I.due_date
    """)

    if active:
        choices = {
            f"#{x['issue_id']} | {x['name']} | {x['title']}": x
            for x in active
        }

        selected = st.selectbox(
            "Select Issued Book", list(choices.keys())
        )
        return_date = st.date_input("Return Date", value=date.today())

        if st.button("Confirm Book Return"):
            record = choices[selected]

            try:
                execute("""
                    UPDATE Issues
                    SET status='Returned',return_date=%s
                    WHERE issue_id=%s AND status='Issued'
                """, (return_date, record["issue_id"]))

                execute("""
                    UPDATE Books
                    SET available_copies=available_copies+1
                    WHERE book_id=%s
                """, (record["book_id"],))

                st.success("Book returned successfully!")
            except Exception:
                st.error("Unable to return book.")
    else:
        st.info("No active issued books.")

# ---------------- ISSUE RECORDS ----------------

elif menu == "Issue Records":
    st.header(" Issue Records")

    records = query("""
        SELECT I.issue_id,I.roll_no,S.name,I.book_id,B.title,
               I.issue_date,I.due_date,I.return_date,I.status
        FROM Issues I
        LEFT JOIN Students S ON I.roll_no=S.roll_no
        LEFT JOIN Books B ON I.book_id=B.book_id
        ORDER BY I.issue_id DESC
    """)

    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True)
        st.download_button(
            "Download Issue Records CSV",
            pd.DataFrame(records).to_csv(index=False),
            file_name="library_issue_records.csv",
            mime="text/csv"
        )
    else:
        st.info("No issue records found.")

# ---------------- AI RECOMMENDATIONS ----------------

elif menu == "AI Recommendations":
    st.header("AI Book Recommendations")
    st.write("Discover books based on subject, tags and popularity.")

    students = query("SELECT roll_no,name FROM Students")

    if students:
        selected = st.selectbox(
            "Select Student",
            students,
            format_func=lambda x: f"{x['roll_no']} - {x['name']}"
        )

        issued = query("""
            SELECT book_id FROM Issues
            WHERE roll_no=%s AND status='Issued'
        """, (selected["roll_no"],))

        issued_ids = [x["book_id"] for x in issued]

        books = query("""
            SELECT book_id,title,author,subject,tags,description,
                   available_copies,popularity
            FROM Books
            WHERE available_copies > 0
            ORDER BY popularity DESC
        """)

        recommendations = [
            b for b in books if b["book_id"] not in issued_ids
        ][:3]

        if recommendations:
            for number, book in enumerate(recommendations, 1):
                st.subheader(f"{number}. {book['title']}")
                st.write("**Author:**", book["author"])
                st.write("**Subject:**", book["subject"])
                st.write("**Tags:**", book["tags"])
                st.write("**Why recommended:** Based on availability, popularity and library catalogue.")
                st.divider()
        else:
            st.info("No recommendations available.")
    else:
        st.info("Register students to use recommendations.")

# ---------------- EMAIL REMINDERS ----------------

elif menu == "Email Reminders":
    st.header("Due Date Email Reminders")

    st.write("Send reminders for books due today or already overdue.")

    if st.button("Check and Send Email Reminders"):
        try:
            records = query("""
                SELECT I.issue_id,I.roll_no,S.name,S.email,
                       B.title,I.due_date,I.status
                FROM Issues I
                JOIN Students S ON I.roll_no=S.roll_no
                JOIN Books B ON I.book_id=B.book_id
                WHERE I.status='Issued'
                AND I.due_date <= %s
                AND S.email IS NOT NULL
                AND S.email <> ''
            """, (date.today(),))

            sent = 0
            skipped = 0

            for r in records:
                already = query("""
                    SELECT log_id FROM ReminderLogs
                    WHERE issue_id=%s AND reminder_date=%s
                """, (r["issue_id"], date.today()))

                if already:
                    skipped += 1
                    continue

                late = date.today() > r["due_date"]

                subject = (
                    "Overdue Library Book Reminder"
                    if late else "Library Book Due Today"
                )

                body = f"""
Hello {r['name']},

This is a reminder from Smart Library.

Book Title: {r['title']}
Book ID: {r['issue_id']}
Due Date: {r['due_date']}

{"Your book is overdue. Please return it as soon as possible." if late else "Your book is due today. Please return it on time."}

Thank you,
Smart Library Management System
"""

                send_email(r["email"], subject, body)

                execute("""
                    INSERT INTO ReminderLogs(issue_id,reminder_date)
                    VALUES (%s,%s)
                """, (r["issue_id"], date.today()))

                sent += 1

            st.success(f"Emails sent successfully: {sent}")
            if skipped:
                st.info(f"Already reminded today: {skipped}")

            if not records:
                st.info("No books are due today or overdue.")

        except Exception:
            st.error(
                "Email sending failed. Check Gmail settings and student email addresses."
            )

st.sidebar.divider()
st.sidebar.caption("Smart Library Management System")
st.sidebar.caption("BCA Project")

