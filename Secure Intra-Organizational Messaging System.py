""" 
mailserver_final.py

Single-file Tkinter + MySQL mailserver (SIMS) with fully structured DBMS schema.

Requirements:
- Python 3.12
- mysql-connector-python (import as mysql.connector)
- MySQL database 'mailserver1' (tables auto-created if missing)

Admin credentials (bypass DB):
    username: admin
    password: vulcans
    (display helper: AIR1)

Timestamp format: YYYY-MM-DD HH:MM:SS
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector as mysql
import re
import sys
import os

# -------------------- CONFIG --------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "passwd": "shreyas",
    "database": "mailserver1"
}

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "vulcans"
ADMIN_PASSWORD1 = "AIR1"  # shown as a hint on UI

USERNAME_REGEX = re.compile(r'^[A-Za-z0-9_]{3,30}$')  # safe usernames for DB
FEEDBACK_FILE = "admin.txt"
TS_FMT = "%Y-%m-%d %H:%M:%S"

# -------------------- DB HELPERS --------------------
def get_db_connection():
    try:
        conn = mysql.connect(**DB_CONFIG)
        return conn
    except mysql.Error as err:
        messagebox.showerror("DB Error", f"Unable to connect to MySQL:\n{err}")
        sys.exit(1)

def init_db():
    """
    Create normalized schema (structured):
    - users(user_id, username, password, nickname, created_on, sent, received)
    - messages(msg_id, sender_id, body, timestamp)
    - message_recipients(msg_id, recipient_id, status)

    Also creates indexes safely without using unsupported 'IF NOT EXISTS'.
    """
    conn = get_db_connection()
    
    cur = conn.cursor(dictionary=True)

    # --- Create main tables ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(69) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nickname VARCHAR(50),
            created_on DATETIME,
            sent INT DEFAULT 0,
            received INT DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            msg_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            body TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS message_recipients (
            msg_id BIGINT NOT NULL,
            recipient_id INT NOT NULL,
            status ENUM('SENT','DELIVERED','READ','DELETED') DEFAULT 'SENT',
            PRIMARY KEY (msg_id, recipient_id),
            FOREIGN KEY (msg_id) REFERENCES messages(msg_id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # --- Safe index creation ---
    def ensure_index(table, index_name, column):
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(f"SHOW INDEX FROM `{table}` WHERE Key_name=%s", (index_name,))
        row = cur.fetchone()

        # If row is None, index does NOT exist
        if row is None:
            cur.execute(f"CREATE INDEX `{index_name}` ON `{table}`(`{column}`)")
            conn.commit()

        cur.close()
        conn.close()



def get_user_id(username: str):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row[0] if row else None

def get_username(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username FROM users WHERE user_id=%s", (user_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row[0] if row else None

def get_all_usernames(exclude: str | None = None):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if exclude:
        cur.execute("SELECT username FROM users WHERE username <> %s", (exclude,))
    else:
        cur.execute("SELECT username FROM users")
    users = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return users

# -------------------- GLOBAL STATE --------------------
current_user = None  # stores currently logged-in username (str)

# -------------------- UI UTIL --------------------
def safe_destroy(win):
    try:
        win.destroy()
    except Exception:
        pass

# -------------------- AUTH WINDOWS --------------------
def login_window():
    win = tk.Tk()
    win.title("SIMS - Login")
    win.geometry("480x300")
    win.resizable(False, False)

    tk.Label(win, text="Secure Intra-Organizational Messaging System", font=("Arial", 12, "bold"), pady=8).pack()

    frm = tk.Frame(win)
    frm.pack(pady=6)

    tk.Label(frm, text="Username").grid(row=0, column=0, sticky="w")
    username_entry = tk.Entry(frm, width=36)
    username_entry.grid(row=0, column=1, pady=6)

    tk.Label(frm, text="Password").grid(row=1, column=0, sticky="w")
    password_entry = tk.Entry(frm, width=36, show="*")
    password_entry.grid(row=1, column=1, pady=6)

    show_var = tk.BooleanVar(value=False)
    def toggle_show():
        password_entry.config(show="" if show_var.get() else "*")
    tk.Checkbutton(frm, text="Show Password", variable=show_var, command=toggle_show).grid(row=2, column=1, sticky="w", pady=2)

    def do_login():
        uname = username_entry.get().strip().lower()
        pw = password_entry.get().strip()
        if not uname or not pw:
            messagebox.showwarning("Missing fields", "Enter username and password.")
            return

        # Admin bypass
        if uname == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
            safe_destroy(win)
            admin_panel()
            return

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (uname, pw))
        row = cur.fetchone()
        cur.close(); conn.close()

        if row:
            global current_user
            current_user = uname
            safe_destroy(win)
            user_home()
        else:
            messagebox.showerror("Auth Failed", "Invalid credentials.")

    def open_register():
        safe_destroy(win)
        register_window()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Login", width=14, command=do_login).grid(row=0, column=0, padx=6)
    tk.Button(btn_frame, text="Register", width=14, command=open_register).grid(row=0, column=1, padx=6)
    tk.Button(btn_frame, text="Forgot Password", width=14, command=lambda: [safe_destroy(win), forgot_password_window()]).grid(row=1, column=0, columnspan=2, pady=6)

    tk.Label(win, text=f"(Admin: {ADMIN_USERNAME}/{ADMIN_PASSWORD1})", font=("Arial", 8, "italic")).pack(side="bottom", pady=6)
    win.mainloop()

def register_window():
    win = tk.Tk()
    win.title("SIMS - Register")
    win.geometry("540x360")
    win.resizable(False, False)

    tk.Label(win, text="Register New User", font=("Arial", 13, "bold"), pady=8).pack()
    frm = tk.Frame(win)
    frm.pack(pady=6)

    tk.Label(frm, text="Full name (nickname)").grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(frm, width=40)
    name_entry.grid(row=0, column=1, pady=6)

    tk.Label(frm, text="Username (3-30, letters/numbers/_ )").grid(row=1, column=0, sticky="w")
    username_entry = tk.Entry(frm, width=40)
    username_entry.grid(row=1, column=1, pady=6)

    tk.Label(frm, text="Password").grid(row=2, column=0, sticky="w")
    password_entry = tk.Entry(frm, width=40, show="*")
    password_entry.grid(row=2, column=1, pady=6)

    def do_register():
        name = name_entry.get().strip()
        uname = username_entry.get().strip().lower()

        pw = password_entry.get().strip()
        if not name or not uname or not pw:
            messagebox.showwarning("Missing fields", "All fields required.")
            return
        if uname == ADMIN_USERNAME:
            messagebox.showerror("Reserved", "This username is reserved.")
            return
        if not USERNAME_REGEX.match(uname):
            messagebox.showerror("Invalid", "Username must be 3-30 chars: letters, numbers, underscore.")
            return

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT username FROM users WHERE username=%s", (uname,))
        if cur.fetchone():
            cur.close(); conn.close()
            messagebox.showerror("Exists", "Username already taken.")
            return

        now = datetime.now().strftime(TS_FMT)
        cur.execute(
            "INSERT INTO users (username, password, nickname, created_on, sent, received) VALUES (%s,%s,%s,%s,%s,%s)",
            (uname, pw, name, now, 0, 0)
        )
        conn.commit()
        cur.close(); conn.close()
        messagebox.showinfo("Registered", "Account created. Please login.")
        safe_destroy(win)
        login_window()

    tk.Button(win, text="Register", width=18, command=do_register).pack(pady=8)
    tk.Button(win, text="Back to Login", width=18, command=lambda: [safe_destroy(win), login_window()]).pack()
    win.mainloop()

# -------------------- USER WINDOWS --------------------
def user_home():
    win = tk.Tk()
    win.title(f"SIMS - Home ({current_user})")
    win.geometry("560x460")
    win.resizable(False, False)

    tk.Label(win, text=f"Welcome, {current_user}", font=("Arial", 13, "bold"), pady=10).pack()

    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Button(frame, text="Compose Mail (comma-separated recipients)", width=48,
              command=lambda: [safe_destroy(win), compose_mail_window()]).grid(row=0, column=0, pady=6)
    tk.Button(frame, text="Inbox", width=48, command=lambda: [safe_destroy(win), inbox_window()]).grid(row=1, column=0, pady=6)
    tk.Button(frame, text="Sentbox", width=48, command=lambda: [safe_destroy(win), sentbox_window()]).grid(row=2, column=0, pady=6)
    tk.Button(frame, text="Broadcast (to ALL users)", width=48, command=lambda: [safe_destroy(win), broadcast_user_window()]).grid(row=3, column=0, pady=6)
    tk.Button(frame, text="Give Feedback", width=48, command=lambda: [safe_destroy(win), feedback_window()]).grid(row=4, column=0, pady=6)
    tk.Button(frame, text="Change Password (verify nickname)", width=48, command=lambda: [safe_destroy(win), change_password_window()]).grid(row=5, column=0, pady=6)
    tk.Button(frame, text="Logout", width=48, command=lambda: [safe_destroy(win), logout()]).grid(row=6, column=0, pady=6)

    win.mainloop()

def compose_mail_window():
    win = tk.Tk()
    win.title("SIMS - Compose Mail")
    win.geometry("900x560")
    win.resizable(False, False)

    tk.Label(win, text="To (comma-separated usernames) — backend auto-handles single vs multiple", font=("Arial", 11, "bold")).pack(pady=8)
    to_entry = tk.Entry(win, width=120)
    to_entry.pack(pady=6)

    tk.Label(win, text="Message").pack()
    body = tk.Text(win, width=110, height=20)
    body.pack(pady=6)

    def send_mail():
        recipients_raw = to_entry.get().strip()
        message_body = body.get("1.0", tk.END).strip()
        if not recipients_raw or not message_body:
            messagebox.showwarning("Missing", "Recipient(s) and message are required.")
            return

        recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
        if not recipients:
            messagebox.showwarning("Invalid", "No valid recipients.")
            return

        # Validate recipients exist and map to IDs
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Build username -> user_id map
        '''cur.execute("SELECT username, user_id FROM users")
        urows = cur.fetchall()
        uname_to_id = {u["username"]: u["user_id"] for u in urows}

        for r in recipients:
            if r not in uname_to_id:
                cur.close(); conn.close()
                messagebox.showerror("Unknown recipient", f"Recipient '{r}' does not exist.")
                return

        sender_id = uname_to_id.get(current_user)'''
        cur.execute("SELECT username, user_id FROM users")
        rows = cur.fetchall()

        uname_to_id = {}

        for r in rows:
            # row as dict
            if isinstance(r, dict):
                uname = r["username"].strip().lower()
                uid = r["user_id"]
            # row as tuple
            else:
                uname = r[0].strip().lower()
                uid = r[1]

            uname_to_id[uname] = uid

        # normalize current user
        cu = current_user.strip().lower()

        if cu not in uname_to_id:
            messagebox.showerror("Critical Error", f"User '{current_user}' not found in USERS table.")
            return

        sender_id = uname_to_id[cu]



        ts = datetime.now().strftime(TS_FMT)
        # Insert message once
        cur2 = conn.cursor()
        cur2.execute("INSERT INTO messages (sender_id, body, timestamp) VALUES (%s, %s, %s)", (sender_id, message_body, ts))
        msg_id = cur2.lastrowid

        # Insert N recipients
        delivered = 0
        for r in recipients:
            rid = uname_to_id[r]
            cur2.execute("INSERT INTO message_recipients (msg_id, recipient_id, status) VALUES (%s, %s, 'SENT')", (msg_id, rid))
            cur2.execute("UPDATE users SET received = received + 1 WHERE user_id=%s", (rid,))
            delivered += 1

        # Update sender sent count
        cur2.execute("UPDATE users SET sent = sent + %s WHERE user_id=%s", (delivered, sender_id))
        conn.commit()
        cur2.close(); cur.close(); conn.close()

        messagebox.showinfo("Sent", f"Message delivered to {delivered} recipient(s).")
        safe_destroy(win)
        user_home()

    tk.Button(win, text="Send", width=18, command=send_mail).pack(pady=8)
    tk.Button(win, text="Back", width=18, command=lambda: [safe_destroy(win), user_home()]).pack()
    win.mainloop()

def inbox_window():
    win = tk.Tk()
    win.title(f"SIMS - Inbox ({current_user})")
    win.geometry("1120x620")
    win.resizable(False, False)

    tk.Label(win, text=f"Inbox - {current_user}", font=("Arial", 12, "bold"), pady=6).pack()

    # Query: messages received by current user
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Map current user to ID
    cur.execute("SELECT user_id FROM users WHERE username=%s", (current_user,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        messagebox.showerror("Error", "Current user not found.")
        safe_destroy(win)
        user_home()
        return
    my_id = row["user_id"]

    cur.execute("""
        SELECT m.msg_id, u.username AS sender, m.body AS message, m.timestamp
        FROM message_recipients mr
        JOIN messages m ON mr.msg_id = m.msg_id
        JOIN users u ON m.sender_id = u.user_id
        WHERE mr.recipient_id = %s
        ORDER BY m.timestamp DESC
    """, (my_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()

    cols = ("ID", "Sender", "Message", "Timestamp")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=24)
    tree.heading("ID", text="ID"); tree.column("ID", width=70, anchor="center")
    tree.heading("Sender", text="Sender"); tree.column("Sender", width=180, anchor="center")
    tree.heading("Message", text="Message"); tree.column("Message", width=700, anchor="w")
    tree.heading("Timestamp", text="Timestamp"); tree.column("Timestamp", width=170, anchor="center")

    for r in rows:
        ts = r["timestamp"].strftime(TS_FMT)
        tree.insert("", tk.END, values=(r["msg_id"], r["sender"], r["message"], ts))
    tree.pack(padx=12, pady=8, fill="both", expand=True)

    def refresh():
        safe_destroy(win)
        inbox_window()

    def delete_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select message(s) to delete (from your inbox).")
            return
        ids = [tree.item(s)["values"][0] for s in sel]
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        # deleting from inbox means delete recipient row for current user
        cur.execute("SELECT user_id FROM users WHERE username=%s", (current_user,))
        uid = cur.fetchone()[0]
        for mid in ids:
            cur.execute("DELETE FROM message_recipients WHERE msg_id=%s AND recipient_id=%s", (mid, uid))
        conn.commit(); cur.close(); conn.close()
        messagebox.showinfo("Deleted", "Selected message(s) removed from your inbox.")
        refresh()

    btnframe = tk.Frame(win); btnframe.pack(pady=6)
    tk.Button(btnframe, text="Refresh", width=14, command=refresh).grid(row=0, column=0, padx=6)
    tk.Button(btnframe, text="Delete Selected", width=16, command=delete_selected).grid(row=0, column=1, padx=6)
    tk.Button(btnframe, text="Back", width=14, command=lambda: [safe_destroy(win), user_home()]).grid(row=0, column=2, padx=6)
    win.mainloop()

def sentbox_window():
    win = tk.Tk()
    win.title(f"SIMS - Sentbox ({current_user})")
    win.geometry("1120x620")
    win.resizable(False, False)

    tk.Label(win, text=f"Sentbox - {current_user}", font=("Arial", 12, "bold"), pady=6).pack()

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Get sender_id
    cur.execute("SELECT user_id FROM users WHERE username=%s", (current_user,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        messagebox.showerror("Error", "Current user not found.")
        safe_destroy(win); user_home(); return
    my_id = row["user_id"]

    # Query sent messages + aggregate recipients (structured)
    # Use GROUP_CONCAT to show recipient usernames
    cur.execute("""
        SELECT 
            m.msg_id,
            m.body AS message,
            m.timestamp,
            GROUP_CONCAT(u2.username ORDER BY u2.username SEPARATOR ', ') AS recipients
        FROM messages m
        JOIN message_recipients mr ON m.msg_id = mr.msg_id
        JOIN users u2 ON mr.recipient_id = u2.user_id
        WHERE m.sender_id = %s
        GROUP BY m.msg_id, m.body, m.timestamp
        ORDER BY m.timestamp DESC
    """, (my_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()

    cols = ("ID", "Recipients", "Message", "Timestamp")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=24)
    tree.heading("ID", text="ID"); tree.column("ID", width=70, anchor="center")
    tree.heading("Recipients", text="Recipients"); tree.column("Recipients", width=300, anchor="w")
    tree.heading("Message", text="Message"); tree.column("Message", width=600, anchor="w")
    tree.heading("Timestamp", text="Timestamp"); tree.column("Timestamp", width=170, anchor="center")

    for r in rows:
        ts = r["timestamp"].strftime(TS_FMT)
        tree.insert("", tk.END, values=(r["msg_id"], r["recipients"] or "", r["message"], ts))
    tree.pack(padx=12, pady=8, fill="both", expand=True)

    def refresh():
        safe_destroy(win)
        sentbox_window()

    def delete_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select message(s) to delete.")
            return
        ids = [tree.item(s)["values"][0] for s in sel]
        # Deleting a sent message means deleting the message row entirely (cascades recipients)
        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        for mid in ids:
            cur.execute("DELETE FROM messages WHERE msg_id=%s AND sender_id=(SELECT user_id FROM users WHERE username=%s)", (mid, current_user))
        conn.commit(); cur.close(); conn.close()
        messagebox.showinfo("Deleted", "Selected sent message(s) deleted.")
        refresh()

    btnframe = tk.Frame(win); btnframe.pack(pady=6)
    tk.Button(btnframe, text="Refresh", width=14, command=refresh).grid(row=0, column=0, padx=6)
    tk.Button(btnframe, text="Delete Selected", width=16, command=delete_selected).grid(row=0, column=1, padx=6)
    tk.Button(btnframe, text="Back", width=14, command=lambda: [safe_destroy(win), user_home()]).grid(row=0, column=2, padx=6)
    win.mainloop()

def broadcast_user_window():
    win = tk.Tk()
    win.title("SIMS - Broadcast (User)")
    win.geometry("780x460")
    win.resizable(False, False)

    tk.Label(win, text="Broadcast Message to ALL users", font=("Arial", 12, "bold")).pack(pady=8)
    body = tk.Text(win, width=96, height=20)
    body.pack(pady=6)

    def do_broadcast():
        message_body = body.get("1.0", tk.END).strip()
        if not message_body:
            messagebox.showwarning("Empty", "Message cannot be empty.")
            return

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Map usernames to IDs
        cur.execute("SELECT username, user_id FROM users")
        umap = {r["username"]: r["user_id"] for r in cur.fetchall()}
        if current_user not in umap:
            cur.close(); conn.close()
            messagebox.showerror("Error", "Current user not found.")
            return

        sender_id = umap[current_user]
        # All other users are recipients
        recipients = [uid for uname, uid in umap.items() if uname != current_user]
        if not recipients:
            cur.close(); conn.close()
            messagebox.showwarning("No recipients", "There are no other users to broadcast to.")
            return

        ts = datetime.now().strftime(TS_FMT)
        cur2 = conn.cursor()
        # Insert message once
        cur2.execute("INSERT INTO messages (sender_id, body, timestamp) VALUES (%s, %s, %s)", (sender_id, message_body, ts))
        msg_id = cur2.lastrowid

        for rid in recipients:
            cur2.execute("INSERT INTO message_recipients (msg_id, recipient_id, status) VALUES (%s, %s, 'SENT')", (msg_id, rid))
            cur2.execute("UPDATE users SET received = received + 1 WHERE user_id=%s", (rid,))
        cur2.execute("UPDATE users SET sent = sent + %s WHERE user_id=%s", (len(recipients), sender_id))
        conn.commit()
        cur2.close(); cur.close(); conn.close()

        messagebox.showinfo("Broadcast", f"Broadcast delivered to {len(recipients)} users.")
        safe_destroy(win)
        user_home()

    tk.Button(win, text="Send Broadcast", width=18, command=do_broadcast).pack(pady=8)
    tk.Button(win, text="Back", width=18, command=lambda: [safe_destroy(win), user_home()]).pack()
    win.mainloop()

def feedback_window():
    win = tk.Tk()
    win.title("SIMS - Feedback")
    win.geometry("760x440")
    win.resizable(False, False)

    tk.Label(win, text="Submit Feedback to Admin", font=("Arial", 12, "bold")).pack(pady=8)
    body = tk.Text(win, width=92, height=18)
    body.pack(pady=6)

    def submit_fb():
        msg = body.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showwarning("Empty", "Feedback cannot be empty.")
            return
        with open(FEEDBACK_FILE, "a+", encoding="utf-8") as f:
            f.write(f"{current_user}:- {msg}\n")
        messagebox.showinfo("Submitted", "Feedback submitted.")
        safe_destroy(win)
        user_home()

    tk.Button(win, text="Submit", width=18, command=submit_fb).pack(pady=8)
    tk.Button(win, text="Back", width=18, command=lambda: [safe_destroy(win), user_home()]).pack()
    win.mainloop()

def change_password_window():
    win = tk.Tk()
    win.title("SIMS - Change Password")
    win.geometry("480x260")
    win.resizable(False, False)

    frm = tk.Frame(win); frm.pack(pady=12)
    tk.Label(frm, text="New Password").grid(row=0, column=0, sticky="w")
    newpw = tk.Entry(frm, width=32, show="*"); newpw.grid(row=0, column=1, pady=6)
    tk.Label(frm, text="Nickname (as registered)").grid(row=1, column=0, sticky="w")
    nick = tk.Entry(frm, width=32); nick.grid(row=1, column=1, pady=6)

    def do_change():
        npw = newpw.get().strip(); nn = nick.get().strip()
        if not npw or not nn:
            messagebox.showwarning("Missing", "Both fields required.")
            return
        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT nickname FROM users WHERE username=%s", (current_user,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            messagebox.showerror("Error", "Current user not found.")
            return
        if nn == row[0]:
            cur.execute("UPDATE users SET password=%s WHERE username=%s", (npw, current_user))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Changed", "Password changed. Please login again.")
            safe_destroy(win)
            logout()
        else:
            messagebox.showwarning("Mismatch", "Nickname does not match.")
    tk.Button(win, text="Change", width=16, command=do_change).pack(pady=8)
    tk.Button(win, text="Back", width=16, command=lambda: [safe_destroy(win), user_home()]).pack()
    win.mainloop()

def forgot_password_window():
    win = tk.Tk()
    win.title("SIMS - Forgot Password")
    win.geometry("540x320")
    win.resizable(False, False)

    frm = tk.Frame(win); frm.pack(pady=12)
    tk.Label(frm, text="Username").grid(row=0, column=0, sticky="w")
    uname_entry = tk.Entry(frm, width=36); uname_entry.grid(row=0, column=1, pady=6)
    tk.Label(frm, text="New Password").grid(row=1, column=0, sticky="w")
    npw_entry = tk.Entry(frm, width=36, show="*"); npw_entry.grid(row=1, column=1, pady=6)
    tk.Label(frm, text="Nickname").grid(row=2, column=0, sticky="w")
    nick_entry = tk.Entry(frm, width=36); nick_entry.grid(row=2, column=1, pady=6)

    def do_forgot():
        uname = uname_entry.get().strip(); npw = npw_entry.get().strip(); nn = nick_entry.get().strip()
        if not uname or not npw or not nn:
            messagebox.showwarning("Missing", "All fields required.")
            return
        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT nickname FROM users WHERE username=%s", (uname,))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Error", "Username not found.")
            cur.close(); conn.close(); return
        if nn == row[0]:
            cur.execute("UPDATE users SET password=%s WHERE username=%s", (npw, uname))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Success", "Password updated. Please login.")
            safe_destroy(win)
            login_window()
        else:
            messagebox.showwarning("Mismatch", "Nickname does not match.")

    tk.Button(win, text="Set New Password", width=18, command=do_forgot).pack(pady=8)
    tk.Button(win, text="Back to Login", width=18, command=lambda: [safe_destroy(win), login_window()]).pack()
    win.mainloop()

# -------------------- ADMIN WINDOWS --------------------
def admin_panel():
    win = tk.Tk()
    win.title("SIMS - Admin Panel")
    win.geometry("1080x680")
    win.resizable(False, False)

    tk.Label(win, text="ADMIN CONTROL PANEL", font=("Arial", 14, "bold"), pady=8).pack()

    cols = ("Username", "Nickname", "Created On", "Inbox Count", "Sent", "Received")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=24)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=170 if c == "Username" else 150, anchor="center")
    tree.pack(padx=12, pady=8, fill="both", expand=True)

    def load_users():
        for r in tree.get_children():
            tree.delete(r)
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        # get basic info
        cur.execute("SELECT user_id, username, nickname, created_on, sent, received FROM users ORDER BY created_on DESC")
        users = cur.fetchall()
        # compute inbox count as count of recipient rows
        cur2 = conn.cursor()
        for u in users:
            try:
                cur2.execute("SELECT COUNT(*) FROM message_recipients WHERE recipient_id=%s", (u["user_id"],))
                cnt = cur2.fetchone()[0]
            except Exception:
                cnt = 0
            tree.insert("", tk.END, values=(
                u["username"], u.get("nickname") or "", 
                u.get("created_on").strftime(TS_FMT) if u.get("created_on") else "",
                cnt, u.get("sent") or 0, u.get("received") or 0
            ))
        cur2.close(); cur.close(); conn.close()

    load_users()

    ctrl = tk.Frame(win); ctrl.pack(pady=6)
    def delete_user():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a user to delete.")
            return
        username_to_delete = tree.item(sel[0])["values"][0]
        if username_to_delete == ADMIN_USERNAME:
            messagebox.showerror("Protected", "Cannot delete admin.")
            return
        if not messagebox.askyesno("Confirm", f"Delete user '{username_to_delete}' and all their data?"):
            return
        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("DELETE FROM users WHERE username=%s", (username_to_delete,))
        conn.commit(); cur.close(); conn.close()
        messagebox.showinfo("Deleted", f"User '{username_to_delete}' deleted.")
        load_users()

    def admin_broadcast():
        bw = tk.Toplevel(win); bw.title("Admin Broadcast"); bw.geometry("760x420")
        tk.Label(bw, text="Compose Broadcast (Admin)", font=("Arial", 12, "bold")).pack(pady=8)
        txt = tk.Text(bw, width=96, height=18); txt.pack(pady=6)
        def do_send():
            body = txt.get("1.0", tk.END).strip()
            if not body:
                messagebox.showwarning("Empty", "Broadcast cannot be empty."); return
            conn = get_db_connection(); cur = conn.cursor(dictionary=True)
            cur.execute("SELECT user_id, username FROM users")
            users = cur.fetchall()
            umap = {u["username"]: u["user_id"] for u in users}
            if ADMIN_USERNAME not in umap:
                # Allow admin send without user row; sender will be 'admin' phantom. Create on-the-fly if desired.
                sender_id = None
            else:
                sender_id = umap[ADMIN_USERNAME]
            recipients = [u["user_id"] for u in users if u["username"] != ADMIN_USERNAME]
            if not recipients:
                cur.close(); conn.close()
                messagebox.showwarning("No recipients", "There are no users to broadcast to."); return
            ts = datetime.now().strftime(TS_FMT)
            cur2 = conn.cursor()
            # If admin has a DB row, store sender_id; else store a message with NULL sender and label later.
            if sender_id:
                cur2.execute("INSERT INTO messages (sender_id, body, timestamp) VALUES (%s, %s, %s)", (sender_id, body, ts))
            else:
                # Create a phantom sender row for admin if needed
                cur2.execute("INSERT INTO users (username, password, nickname, created_on, sent, received) VALUES ('admin','', 'ADMIN', %s, 0, 0)", (ts,))
                sender_id = cur2.lastrowid
                cur2.execute("INSERT INTO messages (sender_id, body, timestamp) VALUES (%s, %s, %s)", (sender_id, body, ts))
            msg_id = cur2.lastrowid
            for rid in recipients:
                cur2.execute("INSERT INTO message_recipients (msg_id, recipient_id, status) VALUES (%s, %s, 'SENT')", (msg_id, rid))
                cur2.execute("UPDATE users SET received = received + 1 WHERE user_id=%s", (rid,))
            cur2.execute("UPDATE users SET sent = sent + %s WHERE user_id=%s", (len(recipients), sender_id))
            conn.commit(); cur2.close(); cur.close(); conn.close()
            messagebox.showinfo("Sent", f"Broadcast delivered to {len(recipients)} users.")
            bw.destroy(); load_users()
        tk.Button(bw, text="Send Broadcast", width=18, command=do_send).pack(pady=8)
        tk.Button(bw, text="Cancel", width=12, command=bw.destroy).pack()
        bw.transient(win); bw.grab_set()

    def view_reports():
        safe_destroy(win)
        report_window()

    tk.Button(ctrl, text="Delete Selected User", width=20, command=delete_user).grid(row=0, column=0, padx=8)
    tk.Button(ctrl, text="Admin Broadcast", width=20, command=admin_broadcast).grid(row=0, column=1, padx=8)
    tk.Button(ctrl, text="View Reports", width=14, command=view_reports).grid(row=0, column=2, padx=8)
    tk.Button(ctrl, text="Refresh", width=12, command=load_users).grid(row=0, column=3, padx=8)
    tk.Button(ctrl, text="Logout Admin", width=14, command=lambda: [safe_destroy(win), login_window()]).grid(row=0, column=4, padx=8)
    win.mainloop()

def report_window():
    win = tk.Tk()
    win.title("SIMS - Reports")
    win.geometry("960x640")
    win.resizable(False, False)

    tk.Label(win, text="Users Report & Admin Actions", font=("Arial", 13, "bold")).pack(pady=8)

    lb = tk.Listbox(win, width=90, height=20)
    lb.pack(pady=6)

    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username FROM users ORDER BY created_on DESC")
    rows = cur.fetchall()
    users = []

    for r in rows:
        if isinstance(r, dict):
            users.append(r.get("username"))
        else:
            users.append(r[0])

    cur.close(); conn.close()
    for i, u in enumerate(users):
        lb.insert(i, u)

    def send_selected():
        sel = lb.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select at least one user."); return
        recipients = [lb.get(i) for i in sel]
        bw = tk.Toplevel(win); bw.title("Admin Send"); bw.geometry("760x420")
        tk.Label(bw, text="Message to selected users", font=("Arial", 12, "bold")).pack(pady=8)
        txt = tk.Text(bw, width=96, height=18); txt.pack(pady=6)
        def do_send():
            body = txt.get("1.0", tk.END).strip()
            if not body:
                messagebox.showwarning("Empty", "Message empty."); return
            conn = get_db_connection(); cur = conn.cursor(dictionary=True)
            cur.execute("SELECT username, user_id FROM users")
            umap = {r["username"]: r["user_id"] for r in cur.fetchall()}

            # ensure admin sender in DB
            sender_id = umap.get(ADMIN_USERNAME)
            ts = datetime.now().strftime(TS_FMT)
            cur2 = conn.cursor()
            if not sender_id:
                cur2.execute("INSERT INTO users (username, password, nickname, created_on, sent, received) VALUES ('admin','', 'ADMIN', %s, 0, 0)", (ts,))
                sender_id = cur2.lastrowid

            cur2.execute("INSERT INTO messages (sender_id, body, timestamp) VALUES (%s, %s, %s)", (sender_id, body, ts))
            msg_id = cur2.lastrowid

            count = 0
            for uname in recipients:
                rid = umap.get(uname)
                if not rid: continue
                cur2.execute("INSERT INTO message_recipients (msg_id, recipient_id, status) VALUES (%s, %s, 'SENT')", (msg_id, rid))
                cur2.execute("UPDATE users SET received = received + 1 WHERE user_id=%s", (rid,))
                count += 1
            cur2.execute("UPDATE users SET sent = sent + %s WHERE user_id=%s", (count, sender_id))
            conn.commit(); cur2.close(); cur.close(); conn.close()
            messagebox.showinfo("Sent", f"Sent to {count} users.")
            bw.destroy()
        tk.Button(bw, text="Send", command=do_send).pack(pady=6)
        tk.Button(bw, text="Cancel", command=bw.destroy).pack()
        bw.transient(win); bw.grab_set()

    def delete_selected():
        sel = lb.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select at least one user."); return
        username = lb.get(sel[0])
        if username == ADMIN_USERNAME:
            messagebox.showerror("Protected", "Cannot delete admin."); return
        if not messagebox.askyesno("Confirm", f"Delete '{username}'?"):
            return
        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("DELETE FROM users WHERE username=%s", (username,))
        conn.commit(); cur.close(); conn.close()
        lb.delete(sel[0]); messagebox.showinfo("Deleted", f"User '{username}' deleted.")

    def view_feedback():
        if not os.path.exists(FEEDBACK_FILE):
            messagebox.showinfo("Feedback", "No feedback file found.")
            return
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            data = f.read()
        fb_win = tk.Toplevel(win); fb_win.title("Feedback")
        txt = tk.Text(fb_win, width=110, height=32); txt.pack()
        txt.insert("1.0", data); txt.config(state="disabled")

    tk.Button(win, text="Send to Selected", width=18, command=send_selected).pack(pady=6)
    tk.Button(win, text="Delete Selected", width=18, command=delete_selected).pack(pady=6)
    tk.Button(win, text="View Feedback File", width=18, command=view_feedback).pack(pady=6)
    tk.Button(win, text="Back to Admin", width=18, command=lambda: [safe_destroy(win), admin_panel()]).pack(pady=6)
    win.mainloop()

# -------------------- LOGOUT --------------------
def logout():
    global current_user
    current_user = None
    login_window()

# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    # ensure feedback file exists
    if not os.path.exists(FEEDBACK_FILE):
        open(FEEDBACK_FILE, "a+", encoding="utf-8").close()

    init_db()
    login_window()
