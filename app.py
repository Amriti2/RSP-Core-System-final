from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------
# APP SETUP
# ------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------------
# FIREBASE SETUP
# ------------------------
# Ensure this JSON file is in your project folder!
import os
import firebase_admin
from firebase_admin import credentials, firestore

private_key = os.environ.get("FIREBASE_PRIVATE_KEY")

if private_key:
    private_key = private_key.replace("\\n", "\n")

firebase_config = {
    "type": os.environ.get("FIREBASE_TYPE"),
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key": private_key,
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
}

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

db = firestore.client()



# ------------------------
# CONSTANTS
# ------------------------
PRINCIPALS = ["amran_principal", "principal2"]

# ------------------------
# ROUTES
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Initialize with empty structures
        db.collection("users").add({
            "username": username,
            "password": password,
            "name": "",
            "subjects": [],
            "level": "",
            "notifications": [],
            "notes": [] 
        })

        flash("✅ Account created successfully!", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

PRINCIPALS = ["admin", "principal1", "principal2", "amran_principal"]  # Add principal usernames here
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = db.collection("users").where("username", "==", username).where("password", "==", password).stream()
        
        user_found = None
        for u in users:
            user_found = u
            break

        if user_found:
            if username in PRINCIPALS:
                return redirect(url_for("principal_dashboard"))
            else:
                return redirect(url_for("dashboard", user_id=user_found.id))
        
        flash("❌ Wrong username or password.", "error")
    return render_template("login.html")

@app.route("/dashboard/<user_id>")
def dashboard(user_id):
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        flash("User not found.", "error")
        return redirect(url_for("login"))

    user_data = user_doc.to_dict()
    user_data.setdefault("subjects", [])
    user_data.setdefault("notifications", [])
    user_data.setdefault("notes", [])

    return render_template("dashboard.html", user=user_data, user_id=user_id)

@app.route("/update/<user_id>", methods=["POST"])
def update(user_id):
    name = request.form.get("name")
    email = request.form.get("email")
    level = request.form.get("level")
    subjects_raw = request.form.get("subjects", "")
    subjects = [s.strip() for s in subjects_raw.split(",")] if subjects_raw else []

    db.collection("users").document(user_id).update({
        "name": name,
        "email": email,
        "level": level,
        "subjects": subjects
    })

    flash("✅ Profile Updated!", "success")
    return redirect(url_for("dashboard", user_id=user_id))

# ------------------------
# PRINCIPAL COMMANDS
# ------------------------

@app.route("/principal")
def principal_dashboard():
    query = request.args.get("search", "").lower()
    students_ref = db.collection("users").stream()
    all_students = []

    for s in students_ref:
        data = s.to_dict()
        data["id"] = s.id
        # Search Filter
        if not query or query in data.get("name", "").lower() or query in data.get("username", "").lower():
            all_students.append(data)

    all_students.sort(key=lambda x: x.get("name") or x.get("username"))

    # Load Global Notifications
    p_ref = db.collection("principal").document("principal_notifications")
    p_doc = p_ref.get()
    p_notes = p_doc.to_dict().get("notifications", []) if p_doc.exists else []

    return render_template("principal_dashboard.html", students=all_students, notifications=p_notes, search=query)

@app.route("/add_student", methods=["POST"])
def add_student():
    db.collection("users").add({
        "name": request.form.get("name"),
        "username": request.form.get("username"),
        "email": request.form.get("email", ""),
        "level": request.form.get("level", ""),
        "subjects": [],
        "notifications": [],
        "notes": []
    })
    return redirect(url_for("principal_dashboard"))

@app.route("/delete_student/<student_id>", methods=["POST"])
def delete_student(student_id):
    db.collection("users").document(student_id).delete()
    return redirect(url_for("principal_dashboard"))

# --- MESSAGE SYSTEM (The part you needed!) ---

@app.route("/notify/<student_id>", methods=["POST"])
def send_notification(student_id):
    msg = request.form.get("notification")
    if msg:
        user_ref = db.collection("users").document(student_id)
        user_ref.update({
            "notifications": firestore.ArrayUnion([msg])
        })
    return redirect(url_for("principal_dashboard"))

@app.route("/chat/<student_id>", methods=["POST"])
def principal_chat(student_id):
    """Sends a message into the student's sub-collection for real-time chat"""
    msg_text = request.form.get("chat_message")
    if not msg_text:
        return redirect(url_for("principal_dashboard"))

    # We add to the 'chat' sub-collection inside the student's document
    # This matches the 'db.collection("users").doc(userId).collection("chat")' in your JS
    db.collection("users").document(student_id).collection("chat").add({
        "message": f"Principal: {msg_text}",
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    
    flash("📡 Transmission Sent", "success")
    return redirect(url_for("principal_dashboard"))

@app.route("/principal_notify", methods=["POST"])
def principal_notify():
    msg = request.form.get("notification")
    if msg:
        p_ref = db.collection("principal").document("principal_notifications")
        p_ref.set({"notifications": firestore.ArrayUnion([msg])}, merge=True)
    return redirect(url_for("principal_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
