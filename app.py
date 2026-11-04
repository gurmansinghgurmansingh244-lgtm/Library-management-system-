import streamlit as st
import random

# App Title
st.title("Library Management Web App")

# Temporary Database (Session State for web stability)
if "books_db" not in st.session_state:
    st.session_state.books_db = [
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "status": "Available"},
        {"title": "Python Programming", "author": "John Smith", "genre": "Tech", "status": "Available"},
        {"title": "Sherlock Holmes", "author": "Arthur Conan Doyle", "genre": "Mystery", "status": "Issued"},
        {"title": "Da Vinci Code", "author": "Dan Brown", "genre": "Thriller", "status": "Available"}
    ]

# Navigation Tabs (Website ki tarah menu)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Home", "Add Book", "Search Book", "Issue Book", "Return Book", "AI Recommendation"])

# ---------------- 1. HOME PAGE ----------------
with tab1:
    st.header("Welcome to Library Manager")
    total = len(st.session_state.books_db)
    available = sum(1 for b in st.session_state.books_db if b["status"] == "Available")
    issued = total - available
    
    st.metric(label="Total Books", value=total)
    st.metric(label="Available Books", value=available)
    st.metric(label="Issued Books", value=issued)

# ---------------- 2. ADD NEW BOOK ----------------
with tab2:
    st.header("Add New Book")
    new_title = st.text_input("Book Title", key="add_t")
    new_author = st.text_input("Author", key="add_a")
    new_genre = st.selectbox("Genre", ["Fantasy", "Tech", "Mystery", "Thriller"], key="add_g")
    
    if st.button("Save Book"):
        if new_title.strip() and new_author.strip():
            st.session_state.books_db.append({"title": new_title.strip(), "author": new_author.strip(), "genre": new_genre, "status": "Available"})
            st.success(f"'{new_title}' has been added successfully!")
        else:
            st.warning("Please fill all fields!")

# ---------------- 3. SEARCH BOOK ----------------
with tab3:
    st.header("Search Books")
    query = st.text_input("Enter Title, Author or Genre to search").lower()
    
    if query:
        found = False
        for b in st.session_state.books_db:
            if query in b["title"].lower() or query in b["author"].lower() or query in b["genre"].lower():
                st.write(f"**Title:** {b['title']} | **Author:** {b['author']} | **Genre:** {b['genre']} | **Status:** {b['status']}")
                st.write("---")
                found = True
        if not found:
            st.error("No books found.")

# ---------------- 4. ISSUE BOOK ----------------
with tab4:
    st.header("Issue a Book")
    issue_title = st.text_input("Enter Book Title to Issue").strip().lower()
    
    if st.button("Confirm Issue"):
        updated = False
        for b in st.session_state.books_db:
            if b["title"].lower() == issue_title:
                if b["status"] == "Available":
                    b["status"] = "Issued"
                    st.success(f"'{b['title']}' has been issued successfully!")
                else:
                    st.warning("Book is already issued to someone else.")
                updated = True
                break
        if not updated:
            st.error("Book not found.")

# ---------------- 5. RETURN BOOK ----------------
with tab5:
    st.header("Return a Book")
    return_title = st.text_input("Enter Book Title to Return").strip().lower()
    
    if st.button("Confirm Return"):
        updated = False
        for b in st.session_state.books_db:
            if b["title"].lower() == return_title:
                if b["status"] == "Issued":
                    b["status"] = "Available"
                    st.success(f"'{b['title']}' has been returned successfully!")
                else:
                    st.info("Book is already available in the library.")
                updated = True
                break
        if not updated:
            st.error("Book not found.")

# ---------------- 6. AI BOOK RECOMMENDATION ----------------
with tab6:
    st.header("AI Book Recommendation")
    selected_genre = st.selectbox("Select your favourite Genre/Mood", ["Fantasy", "Tech", "Mystery", "Thriller"])
    
    if st.button("Get AI Recommendation"):
        matching_books = [b for b in st.session_state.books_db if b["genre"].lower() == selected_genre.lower()]
        if matching_books:
            rec_book = random.choice(matching_books)
            st.info(f"AI Suggestion for you:\n\nTitle: '{rec_book['title']}'\nAuthor: {rec_book['author']}")
        else:
            st.warning(f"No books available 
