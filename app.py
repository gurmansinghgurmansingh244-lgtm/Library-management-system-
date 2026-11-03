import streamlit as st
import streamlit as st
import sqlite3

st.set_page_config(page_title="Smart Library", page_icon="📚")

conn = sqlite3.connect("library.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    author TEXT,
    category TEXT,
    status TEXT DEFAULT 'Available'
)
""")
conn.commit()

st.title("📚 Smart Library Management System")
st.write("Welcome to your digital library!")

menu = st.sidebar.selectbox(
    "Choose Option",
    ["Home", "Add Book", "View Books", "Search Book", "Issue Book", "Return Book"]
)

if menu == "Home":
    st.subheader("Library Dashboard")
    st.write("Manage your books easily with this system.")
    st.info("Use the sidebar to manage your library.")

elif menu == "Add Book":
    st.subheader("Add New Book")

    name = st.text_input("Book Name")
    author = st.text_input("Author Name")
    category = st.selectbox(
        "Category",
        ["Science", "Computer", "Biology", "Chemistry", "Other"]
    )

    if st.button("Add Book"):
        if name and author:
            cursor.execute(
                "INSERT INTO books (name, author, category) VALUES (?, ?, ?)",
                (name, author, category)
            )
            conn.commit()
            st.success("Book added successfully!")
        else:
            st.warning("Please enter book name and author.")

elif menu == "View Books":
    st.subheader("All Library Books")
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    if books:
        st.table(books)
    else:
        st.info("No books available.")

elif menu == "Search Book":
    st.subheader("Search a Book")
    search = st.text_input("Enter book name")

    if search:
        cursor.execute(
            "SELECT * FROM books WHERE name LIKE ?",
            ('%' + search + '%',)
        )
        results = cursor.fetchall()

        if results:
            st.table(results)
        else:
            st.warning("Book not found.")

elif menu == "Issue Book":
    st.subheader("Issue a Book")
    book_id = st.number_input("Enter Book ID", min_value=1, step=1)

    if st.button("Issue"):
        cursor.execute(
            "UPDATE books SET status='Issued' WHERE id=? AND status='Available'",
            (book_id,)
        )
        conn.commit()

        if cursor.rowcount > 0:
            st.success("Book issued successfully!")
        else:
            st.warning("Book not available or invalid ID.")

elif menu == "Return Book":
    st.subheader("Return a Book")
    book_id = st.number_input("Enter Book ID", min_value=1, step=1)

    if st.button("Return"):
        cursor.execute(
            "UPDATE books SET status='Available' WHERE id=? AND status='Issued'",
            (book_id,)
        )
        conn.commit()

        if cursor.rowcount > 0:
            st.success("Book returned successfully!")
        else:
            st.warning("Invalid Book ID or book is not issued.")
