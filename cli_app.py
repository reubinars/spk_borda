import json
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

USERS_FILE = 'users.json'
current_user = None

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def login(username, password):
    global current_user
    users = load_users()
    if username in users and users[username]["password"] == password:
        current_user = username
        return users[username]["role"]
    else:
        return None

def logout(window):
    global current_user
    current_user = None
    if window:
        window.destroy()
        create_login_window()

def vote(user_id, candidate_rankings):
    users = load_users()
    if user_id not in users:
        messagebox.showerror("Error", "User not found.")
        return
    if users[user_id]["role"] != "regular":
        messagebox.showerror("Error", "Only regular users can vote.")
        return
    users[user_id]["votes"] = candidate_rankings
    save_users(users)
    messagebox.showinfo("Success", "Vote recorded successfully.")

def calculate_borda_scores():
    users = load_users()
    votes = [user["votes"] for user in users.values() if user["role"] == "regular"]
    candidates = set().union(*votes)
    borda_scores = {candidate: 0 for candidate in candidates}

    for vote in votes:
        for candidate, ranking in vote.items():
            borda_scores[candidate] += len(votes) - ranking

    return borda_scores

def create_voting_window(user_id):
    global voting_window  # Declare the voting_window as global
    voting_window = tk.Toplevel()
    voting_window.title("Vote for TA Selection")

    def on_close():
        root.destroy()

    voting_window.protocol("WM_DELETE_WINDOW", on_close)

    users = load_users()
    role = users[user_id]["role"]

    if role == "regular":
        candidates = ["Pelamar A", "Pelamar B", "Pelamar C"]

        tk.Label(voting_window, text="Rank the candidates:").pack()
        candidate_vars = []
        for i, candidate in enumerate(candidates):
            var = tk.IntVar()
            tk.Label(voting_window, text=candidate).pack()
            tk.Radiobutton(voting_window, text="1st", variable=var, value=3).pack(anchor=tk.W)
            tk.Radiobutton(voting_window, text="2nd", variable=var, value=2).pack(anchor=tk.W)
            tk.Radiobutton(voting_window, text="3rd", variable=var, value=1).pack(anchor=tk.W)
            candidate_vars.append(var)

        tk.Button(voting_window, text="Vote", command=lambda: cast_vote(user_id, candidate_vars)).pack()
        tk.Button(voting_window, text="Logout", command=lambda: logout(voting_window)).pack()
    else:
        tk.Label(voting_window, text="You do not have voting privileges.").pack()

def cast_vote(user_id, candidate_vars):
    candidate_rankings = {f"Pelamar {i+1}": var.get() for i, var in enumerate(candidate_vars)}
    vote(user_id, candidate_rankings)

def vote_scores_window():
    table_window = tk.Toplevel()
    table_window.title("Voted Users and Their Votes")

    def on_close():
        root.destroy()

    table_window.protocol("WM_DELETE_WINDOW", on_close)

    users = load_users()
    voted_users = [user for user in users.values() if user["role"] == "regular" and "votes" in user]

    table = ttk.Treeview(table_window)
    table["columns"] = ("username", "vote_pelamar1", "vote_pelamar2", "vote_pelamar3")

    table.heading("#0", text="ID")
    table.column("#0", width=50)
    table.heading("username", text="Username")
    table.column("username", width=100)
    table.heading("vote_pelamar1", text="Vote for Pelamar 1")
    table.column("vote_pelamar1", width=150)
    table.heading("vote_pelamar2", text="Vote for Pelamar 2")
    table.column("vote_pelamar2", width=150)
    table.heading("vote_pelamar3", text="Vote for Pelamar 3")
    table.column("vote_pelamar3", width=150)

    for i, user in enumerate(voted_users):
        username = user.get("username", "Unknown")
        vote_pelamar1 = user["votes"].get("Pelamar 1", "")
        vote_pelamar2 = user["votes"].get("Pelamar 2", "")
        vote_pelamar3 = user["votes"].get("Pelamar 3", "")
        table.insert("", "end", text=i+1, values=(username, vote_pelamar1, vote_pelamar2, vote_pelamar3))

    table.pack()
    calculate_button = tk.Button(table_window, text="Calculate Borda Method", command=calculate_and_display_borda)
    calculate_button.pack()

    tk.Button(table_window, text="Logout", command=lambda: logout(table_window)).pack()

def calculate_and_display_borda():
    users = load_users()
    regular_users = [user for user in users.values() if user["role"] == "regular"]
    voted_users = [user for user in regular_users if "votes" in user]
    if len(voted_users) != len(regular_users):
        messagebox.showerror("Error", "Not every user has voted.")
        return

    borda_scores = calculate_borda_scores()

    # Create a new window to display the Borda scores table
    borda_window = tk.Toplevel()
    borda_window.title("Borda Method Scores")

    def on_close():
        root.destroy()

    borda_window.protocol("WM_DELETE_WINDOW", on_close)

    # Add a label for step-by-step calculation
    step_label = tk.Label(borda_window, text="Step by step")
    step_label.pack()

    # Add text for total votes for each pelamar
    pelamars = ["Pelamar 1", "Pelamar 2", "Pelamar 3"]
    votes_text = "Total votes for:\n"
    for pelamar in pelamars:
        votes_text += f"{pelamar}: "
        votes_for_pelamar = [user["votes"].get(pelamar, 0) for user in voted_users]
        votes_text += " + ".join(str(vote) for vote in votes_for_pelamar)
        total_votes = sum(votes_for_pelamar)
        votes_text += f"={total_votes}\n"
    votes_label = tk.Label(borda_window, text=votes_text)
    votes_label.pack()

    table = ttk.Treeview(borda_window)
    table["columns"] = ("candidate", "borda_score")

    table.heading("#0", text="ID")
    table.column("#0", width=50)
    table.heading("candidate", text="Candidate")
    table.column("candidate", width=150)
    table.heading("borda_score", text="Borda Score")
    table.column("borda_score", width=150)



def create_login_window():
    login_window = tk.Toplevel()
    login_window.geometry("200x200")
    login_window.title("Login")

    def on_close():
        root.destroy()

    login_window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(login_window, text="Username").pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    tk.Label(login_window, text="Password").pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    tk.Button(login_window, text="Login", command=lambda: validate_login(login_window, username_entry.get(), password_entry.get())).pack()
    return login_window

def validate_login(login_window, username, password):
    role = login(username, password)
    if role == "regular":
        login_window.destroy()
        create_voting_window(username)
    elif role == "admin":
        login_window.destroy()
        vote_scores_window()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def main():
    global root
    root = tk.Tk()
    root.withdraw()

    def on_closing():
        root.destroy()

    create_login_window()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    main()

