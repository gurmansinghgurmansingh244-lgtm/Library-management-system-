import tkinter as tk
from tkinter import ttk, messagebox
import random

# App ka main window setup
root = tk.Tk()
root.title("Library Management App")
root.geometry("450x650")

# Custom Styling
style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 5])

# Temporary Database (Lists and Dicts)
books_db = [
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "status": "Available"},
    {"title": "Python Programming", "author": "John Smith", "genre": "Tech", "status": "Available"},
    {"title": "Sherlock Holmes", "author": "Arthur Conan Doyle", "genre": "Mystery", "status": "Issued"},
    {"title": "Da Vinci Code", "author": "Dan Brown", "genre": "Thriller", "status": "Available"}
]

# Tabs (Pages) Banane ke liye Notebook ka use
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Saare Frames (Pages) create karna
home_page = ttk.Frame(notebook)
add_page = ttk.Frame(notebook)
search_page = ttk.Frame(notebook)
issue_page = ttk.Frame(notebook)
return_page = ttk.Frame(notebook)
ai_page = ttk.Frame(notebook)

notebook.add(home_page, text="Home")
notebook.add(add_page, text="Add")
notebook.add(search_page, text="Search")
notebook.add(issue_page, text="Issue")
notebook.add(return_page, text="Return")
notebook.add(ai_page, text="AI Rec")

# ---------------- 1. HOME PAGE ----------------
ttk.Label(home_page, text="📚 Welcome to Library Manager", font=("Arial", 16, "bold")).pack(pady=20)
stats_label = ttk.Label(home_page, text="", font=("Arial", 12))
stats_label.pack(pady=20)

def update_home_stats():
    total = len(books_db)
    available = sum(1 for b in books_db if b["status"] == "Available")
    issued = total - available
    stats_label.config(text=f"Total Books: {total}\n\nAvailable Books: {available}\n\nIssued Books: {issued}")

update_home_stats()

# ---------------- 2. ADD NEW BOOK ----------------
ttk.Label(add_page, text="➕ Add New Book", font=("Arial", 14, "bold")).pack(pady=10)

ttk.Label(add_page, text="Book Title:").pack(pady=2)
title_entry = ttk.Entry(add_page, width=30)
title_entry.pack(pady=2)

ttk.Label(add_page, text="Author:").pack(pady=2)
author_entry = ttk.Entry(add_page, width=30)
author_entry.pack(pady=2)

ttk.Label(add_page, text="Genre (e.g., Tech, Fantasy, Mystery):").pack(pady=2)
genre_entry = ttk.Entry(add_page, width=30)
genre_entry.pack(pady=2)

def save_book():
    t = title_entry.get().strip()
    a = author_entry.get().strip()
    g = genre_entry.get().strip()
    if t and a and g:
        books_db.append({"title": t, "author": a, "genre": g, "status": "Available"})
        messagebox.showinfo("Success", f"'{t}' has been added successfully!")
        title_entry.delete(0, tk.END)
        author_entry.delete(0, tk.END)
        genre_entry.delete(0, tk.END)
        update_home_stats()
    else:
        messagebox.showwarning("Error", "Please fill all fields!")

ttk.Button(add_page, text="Save Book", command=save_book).pack(pady=15)

# ---------------- 3. SEARCH BOOK ----------------
ttk.Label(search_page, text="🔍 Search Books", font=("Arial", 14, "bold")).pack(pady=10)
search_entry = ttk.Entry(search_page, width=30)
search_entry.pack(pady=5)

search_result = tk.Text(search_page, height=15, width=45)
search_result.pack(pady=10)

def search_book():
    query = search_entry.get().lower()
    search_result.delete("1.0", tk.END)
    found = False
    for b in books_db:
        if query in b["title"].lower() or query in b["author"].lower() or query in b["genre"].lower():
            search_result.insert(tk.END, f"📖 Title: {b['title']}\n✍️ Author: {b['author']}\n🏷️ Genre: {b['genre']}\n📌 Status: {b['status']}\n{'-'*30}\n")
            found = True
    if not found:
        search_result.insert(tk.END, "No books found matching your search.")

ttk.Button(search_page, text="Search", command=search_book).pack(pady=5)

# ---------------- 4. ISSUE BOOK ----------------
ttk.Label(issue_page, text="📤 Issue a Book", font=("Arial", 14, "bold")).pack(pady=10)
ttk.Label(issue_page, text="Enter Book Title to Issue:").pack(pady=5)
issue_entry = ttk.Entry(issue_page, width=30)
issue_entry.pack(pady=5)

def issue_book():
    t = issue_entry.get().strip().lower()
    for b in books_db:
        if b["title"].lower() == t:
            if b["status"] == "Available":
                b["status"] = "Issued"
                messagebox.showinfo("Success", f"'{b['title']}' has been issued!")
                issue_entry.delete(0, tk.END)
                update_home_stats()
                return
            else:
                messagebox.showwarning("Unavailable", "Book is already issued to someone else.")
                return
    messagebox.showerror("Not Found", "Book not found in library.")

ttk.Button(issue_page, text="Issue Book", command=issue_book).pack(pady=10)

# ---------------- 5. RETURN BOOK ----------------
ttk.Label(return_page, text="📥 Return a Book", font=("Arial", 14, "bold")).pack(pady=10)
ttk.Label(return_page, text="Enter Book Title to Return:").pack(pady=5)
return_entry = ttk.Entry(return_page, width=30)
return_entry.pack(pady=5)

def return_book():
    t = return_entry.get().strip().lower()
    for b in books_db:
        if b["title"].lower() == t:
            if b["status"] == "Issued":
                b["status"] = "Available"
                messagebox.showinfo("Success", f"'{b['title']}' has been returned!")
                return_entry.delete(0, tk.END)
                update_home_stats()
                return
            else:
                messagebox.showinfo("Info", "Book is already available in the library.")
                return
    messagebox.showerror("Not Found", "Book not found.")

ttk.Button(return_page, text="Return Book", command=return_book).pack(pady=10)

# ---------------- 6. AI BOOK RECOMMENDATION ----------------
ttk.Label(ai_page, text="🤖 AI Book Recommendation", font=("Arial", 14, "bold")).pack(pady=10)
ttk.Label(ai_page, text="Select your favourite Genre/Mood:").pack(pady=5)

genre_combobox = ttk.Combobox(ai_page, values=["Fantasy", "Tech", "Mystery", "Thriller"])
genre_combobox.pack(pady=5)
genre_combobox.current(0)

ai_result_label = ttk.Label(ai_page, text="", font=("Arial", 11, "italic"), justify="center")
ai_result_label.pack(pady=20)

def ai_recommend():
    selected_genre = genre_combobox.get()
    # Filter books by genre
    matching_books = [b for b in books_db if b["genre"].lower() == selected_genre.lower()]
    
    if matching_books:
        rec_book = random.choice(matching_books)
        ai_result_label.config(text=f"💡 AI Suggestion for you:\n\n📖 '{rec_book['title']}'\n✍️ Written by {rec_book['author']}\n📌 Status: {rec_book['status']}")
    else:
        ai_result_label.config(text=f"AI could not find any books in the '{selected_genre}' genre right now.\nTry adding one in the 'Add' tab first!")

ttk.Button(ai_page, text="Get AI Recommendation", command=ai_recommend).pack(pady=10)

# App loop start karna
root.mainloop()
