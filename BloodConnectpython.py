from tkinter import *
from tkinter import ttk, messagebox as msg
from PIL import Image, ImageTk
import sqlite3
from datetime import date

# ---------------------------- DATABASE INIT ----------------------------
def init_db():
    conn = sqlite3.connect("blood_bank.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reco (
            name TEXT NOT NULL,
            age INT NOT NULL,
            sex TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            address TEXT NOT NULL,
            contact_no TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ---------------------------- ADD DONOR ----------------------------
def open_add_donor():
    win = Toplevel(root)
    win.title("Add Donor")
    win.geometry("700x600")
    win.configure(bg="white")

    Label(win, text="🩸 Add Donor Details", font=("Helvetica", 20, "bold"), fg="red", bg="white").pack(pady=20)

    fields = ["Name", "Age", "Sex", "Blood Group", "Address", "Contact No"]
    entries = {}

    frame = Frame(win, bg="white")
    frame.pack(pady=10)

    for i, field in enumerate(fields):
        Label(frame, text=field + ":", font=("Helvetica", 12), bg="white").grid(row=i, column=0, pady=10, padx=20, sticky=W)
        e = Entry(frame, width=35, font=("Helvetica", 12))
        e.grid(row=i, column=1, pady=10)
        entries[field] = e

    # Date entry
    Label(frame, text="Date:", font=("Helvetica", 12), bg="white").grid(row=len(fields), column=0, pady=10, padx=20, sticky=W)
    date_entry = Entry(frame, width=35, font=("Helvetica", 12))
    date_entry.grid(row=len(fields), column=1, pady=10)
    date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

    def save():
        data = {f: e.get() for f, e in entries.items()}
        data["Date"] = date_entry.get()
        if any(v.strip() == "" for v in data.values()):
            msg.showwarning("Error", "Please fill all fields!")
            return
        conn = sqlite3.connect("blood_bank.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO reco VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (data["Name"], data["Age"], data["Sex"], data["Blood Group"],
                     data["Address"], data["Contact No"], data["Date"]))
        conn.commit()
        conn.close()
        msg.showinfo("Success", "Donor added successfully!")
        win.destroy()

    Button(win, text="Save Donor", command=save, bg="#e63946", fg="white",
           font=("Helvetica", 12, "bold"), width=18, height=2, bd=0).pack(pady=20)

# ---------------------------- VIEW DONORS ----------------------------
def open_view_donors():
    win = Toplevel(root)
    win.title("View Donors")
    win.geometry("800x500")
    win.configure(bg="white")
    Label(win, text="👥 All Registered Donors", font=("Helvetica", 18, "bold"), fg="red", bg="white").pack(pady=20)
    
    cols = ("Name", "Age", "Sex", "Blood Group", "Address", "Contact No", "Date")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=BOTH, expand=True, padx=20, pady=10)

    conn = sqlite3.connect("blood_bank.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM reco")
    for row in cur.fetchall():
        tree.insert("", END, values=row)
    conn.close()

# ---------------------------- SEARCH DONOR ----------------------------
def open_search_donor():
    win = Toplevel(root)
    win.title("Search Donor")
    win.geometry("600x500")
    win.configure(bg="white")

    Label(win, text="🔍 Search Donor by Blood Group", font=("Helvetica", 18, "bold"), fg="red", bg="white").pack(pady=20)
    search_var = StringVar(master=win)
    Entry(win, textvariable=search_var, font=("Helvetica", 12), width=25).pack(pady=10)
    
    cols = ("Name", "Age", "Sex", "Blood Group", "Address", "Contact No", "Date")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=10)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=BOTH, expand=True, padx=20, pady=10)

    def search():
        bg = search_var.get().strip()
        if bg == "":
            msg.showwarning("Error", "Please enter a blood group!")
            return
        conn = sqlite3.connect("blood_bank.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM reco WHERE blood_group LIKE ?", ('%' + bg + '%',))
        rows = cur.fetchall()
        conn.close()
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", END, values=row)
        if not rows:
            msg.showinfo("No Result", "No donors found for that blood group!")

    Button(win, text="Search", command=search, bg="#457b9d", fg="white",
           font=("Helvetica", 12, "bold"), width=12, bd=0).pack(pady=10)

# ---------------------------- BLOOD STOCK ----------------------------
def open_blood_stock():
    win = Toplevel(root)
    win.title("Blood Stock")
    win.geometry("400x400")
    win.configure(bg="white")
    Label(win, text="🩸 Blood Stock Summary", font=("Helvetica", 18, "bold"), fg="red", bg="white").pack(pady=20)

    conn = sqlite3.connect("blood_bank.db")
    cur = conn.cursor()
    cur.execute("SELECT blood_group, COUNT(*) FROM reco GROUP BY blood_group")
    data = cur.fetchall()
    conn.close()

    if not data:
        Label(win, text="No stock data available.", font=("Helvetica", 12), bg="white", fg="gray").pack(pady=20)
    else:
        for bg, count in data:
            Label(win, text=f"{bg} → {count} Units", font=("Helvetica", 14, "bold"),
                  bg="white", fg="#1d3557").pack(pady=5)

# ---------------------------- MAIN APP ----------------------------
root = Tk()
root.title("Blood Bank Management System")
root.geometry("1000x650")
root.resizable(False, False)

init_db()

# Load background image properly
try:
    bg = Image.open("background.jpg").resize((1000, 650))
    bg_photo = ImageTk.PhotoImage(bg)
    bg_label = Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    root.configure(bg="#f1f1f1")

# Overlay for readability (solid white)
overlay = Frame(root, bg="#ffffff")
overlay.place(x=0, y=0, relwidth=1, relheight=1)

# Navigation Bar
nav = Frame(root, bg="#e63946", height=60)
nav.pack(fill=X)
Label(nav, text="Blood Bank Management System", bg="#e63946", fg="white",
      font=("Helvetica", 18, "bold")).pack(side=LEFT, padx=30)

# Hero Section
Label(root, text="Welcome to the Blood Bank System", font=("Helvetica", 22, "bold"),
      bg="#ffffff", fg="#1d3557").place(relx=0.5, rely=0.25, anchor="center")
Label(root, text=("Manage blood donors, stock, and search data easily.\n"
                  "A modern, efficient way to keep your blood bank organized."),
      font=("Helvetica", 12), bg="#ffffff", fg="#333333", justify="center").place(relx=0.5, rely=0.33, anchor="center")

# Action Cards
card_frame = Frame(root, bg="#ffffff")
card_frame.place(relx=0.5, rely=0.6, anchor="center")

buttons = [
    ("➕ Add Donor", open_add_donor, "#e63946"),
    ("👥 View Donors", open_view_donors, "#457b9d"),
    ("🔍 Search Donor", open_search_donor, "#2a9d8f"),
    ("📦 Blood Stock", open_blood_stock, "#f4a261"),
]

for i, (text, cmd, color) in enumerate(buttons):
    btn = Button(card_frame, text=text, command=cmd,
                 font=("Helvetica", 13, "bold"), bg=color, fg="white",
                 activebackground=color, activeforeground="white",
                 width=18, height=2, bd=0, relief="flat", cursor="hand2")
    btn.grid(row=i//2, column=i%2, padx=30, pady=15)

# Footer
Label(root, text="Developed by Team Keerthi © 2025", font=("Helvetica", 9, "italic"),
      bg="#ffffff", fg="#444").place(relx=0.5, rely=0.96, anchor="center")

root.mainloop()

