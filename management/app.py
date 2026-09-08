from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-for-your-project"
)


# =========================================================
# MONGODB CONNECTION
# =========================================================

MONGO_URI = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URI)

db = client["hospital_management"]


# =========================================================
# COLLECTIONS
# =========================================================

users_collection = db["users"]

patients_collection = db["patients"]

doctors_collection = db["doctors"]

appointments_collection = db["appointments"]

medicines_collection = db["medicines"]

billing_collection = db["billing"]


# =========================================================
# TEST MONGODB CONNECTION
# =========================================================

try:

    client.admin.command("ping")

    print("MongoDB Connected Successfully")

except Exception as e:

    print("MongoDB Connection Error:", e)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    # If user is already logged in
    if "user_id" in session:

        return redirect(url_for("dashboard"))

    # If no admin exists, go to setup
    if users_collection.count_documents({}) == 0:

        return redirect(url_for("setup"))

    return redirect(url_for("login"))


# =========================================================
# FIRST ADMIN SETUP
# =========================================================

@app.route("/setup", methods=["GET", "POST"])
def setup():

    # Setup should only be available
    # when there are no users.
    if users_collection.count_documents({}) > 0:

        return redirect(url_for("login"))


    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # -----------------------------
        # Username validation
        # -----------------------------

        if not username:

            return render_template(
                "setup.html",
                error="Username is required."
            )


        if len(username) < 3:

            return render_template(
                "setup.html",
                error="Username must contain at least 3 characters."
            )


        # -----------------------------
        # Password validation
        # -----------------------------

        if len(password) < 6:

            return render_template(
                "setup.html",
                error="Password must contain at least 6 characters."
            )


        if password != confirm_password:

            return render_template(
                "setup.html",
                error="Passwords do not match."
            )


        # -----------------------------
        # Create password hash
        # -----------------------------

        password_hash = generate_password_hash(
            password
        )


        # -----------------------------
        # Create admin
        # -----------------------------

        admin = {

            "username": username,

            "password_hash": password_hash,

            "role": "admin",

            "created_at": datetime.now()

        }


        users_collection.insert_one(admin)


        print("---------------------------------------")
        print("First administrator created successfully.")
        print("Username:", username)
        print("---------------------------------------")


        return redirect(url_for("login"))


    return render_template("setup.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # Find user by username
        user = users_collection.find_one(
            {
                "username": username
            }
        )


        if user:

            password_hash = user.get(
                "password_hash"
            )


            # -----------------------------------------
            # Secure hashed password
            # -----------------------------------------

            if password_hash:

                if check_password_hash(
                    password_hash,
                    password
                ):

                    session["user_id"] = str(
                        user["_id"]
                    )

                    session["username"] = user["username"]

                    session["role"] = user.get(
                        "role",
                        "admin"
                    )

                    return redirect(
                        url_for("dashboard")
                    )


            # -----------------------------------------
            # Old plaintext password migration
            # -----------------------------------------
            #
            # This section helps if you previously
            # created an admin with:
            #
            # "password": "admin123"
            #
            # After successful login, it converts
            # that password into a secure hash.
            # -----------------------------------------

            old_password = user.get("password")

            if old_password:

                if password == old_password:

                    new_hash = generate_password_hash(
                        password
                    )

                    users_collection.update_one(

                        {
                            "_id": user["_id"]
                        },

                        {
                            "$set": {
                                "password_hash": new_hash
                            },

                            "$unset": {
                                "password": ""
                            }

                        }

                    )

                    session["user_id"] = str(
                        user["_id"]
                    )

                    session["username"] = user["username"]

                    session["role"] = user.get(
                        "role",
                        "admin"
                    )

                    return redirect(
                        url_for("dashboard")
                    )


        return render_template(
            "login.html",
            error="Invalid username or password"
        )


    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    total_patients = patients_collection.count_documents({})

    total_doctors = doctors_collection.count_documents({})

    total_appointments = appointments_collection.count_documents({})

    total_medicines = medicines_collection.count_documents({})


    return render_template(

        "dashboard.html",

        total_patients=total_patients,

        total_doctors=total_doctors,

        total_appointments=total_appointments,

        total_medicines=total_medicines

    )


# =========================================================
# PATIENTS
# =========================================================

@app.route("/patients")
def patients():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    patients_list = list(

        patients_collection.find().sort(
            "_id",
            -1
        )

    )


    return render_template(

        "patients.html",

        patients=patients_list

    )


# =========================================================
# ADD PATIENT
# =========================================================

@app.route("/patients/add", methods=["POST"])
def add_patient():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    patient = {

        "name": request.form.get(
            "name",
            ""
        ).strip(),

        "age": request.form.get(
            "age",
            ""
        ).strip(),

        "gender": request.form.get(
            "gender",
            ""
        ).strip(),

        "phone": request.form.get(
            "phone",
            ""
        ).strip(),

        "email": request.form.get(
            "email",
            ""
        ).strip(),

        "address": request.form.get(
            "address",
            ""
        ).strip(),

        "blood_group": request.form.get(
            "blood_group",
            ""
        ).strip(),

        "medical_history": request.form.get(
            "medical_history",
            ""
        ).strip(),

        "created_at": datetime.now()

    }


    patients_collection.insert_one(patient)


    return redirect(
        url_for("patients")
    )


# =========================================================
# DELETE PATIENT
# =========================================================

@app.route("/patients/delete/<patient_id>")
def delete_patient(patient_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    try:

        patients_collection.delete_one(

            {
                "_id": ObjectId(patient_id)
            }

        )

    except Exception:

        pass


    return redirect(
        url_for("patients")
    )


# =========================================================
# DOCTORS
# =========================================================

@app.route("/doctors")
def doctors():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    doctors_list = list(

        doctors_collection.find().sort(
            "_id",
            -1
        )

    )


    return render_template(

        "doctors.html",

        doctors=doctors_list

    )


# =========================================================
# ADD DOCTOR
# =========================================================

@app.route("/doctors/add", methods=["POST"])
def add_doctor():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    doctor = {

        "name": request.form.get(
            "name",
            ""
        ).strip(),

        "specialization": request.form.get(
            "specialization",
            ""
        ).strip(),

        "qualification": request.form.get(
            "qualification",
            ""
        ).strip(),

        "phone": request.form.get(
            "phone",
            ""
        ).strip(),

        "email": request.form.get(
            "email",
            ""
        ).strip(),

        "experience": request.form.get(
            "experience",
            ""
        ).strip(),

        "created_at": datetime.now()

    }


    doctors_collection.insert_one(doctor)


    return redirect(
        url_for("doctors")
    )


# =========================================================
# DELETE DOCTOR
# =========================================================

@app.route("/doctors/delete/<doctor_id>")
def delete_doctor(doctor_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    try:

        doctors_collection.delete_one(

            {
                "_id": ObjectId(doctor_id)
            }

        )

    except Exception:

        pass


    return redirect(
        url_for("doctors")
    )


# =========================================================
# APPOINTMENTS
# =========================================================

@app.route("/appointments")
def appointments():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    appointments_list = list(

        appointments_collection.find().sort(
            "_id",
            -1
        )

    )


    patients_list = list(
        patients_collection.find()
    )


    doctors_list = list(
        doctors_collection.find()
    )


    return render_template(

        "appointments.html",

        appointments=appointments_list,

        patients=patients_list,

        doctors=doctors_list

    )


# =========================================================
# ADD APPOINTMENT
# =========================================================

@app.route("/appointments/add", methods=["POST"])
def add_appointment():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    appointment = {

        "patient_id": request.form.get(
            "patient_id",
            ""
        ),

        "patient_name": request.form.get(
            "patient_name",
            ""
        ).strip(),

        "doctor_id": request.form.get(
            "doctor_id",
            ""
        ),

        "doctor_name": request.form.get(
            "doctor_name",
            ""
        ).strip(),

        "date": request.form.get(
            "date",
            ""
        ),

        "time": request.form.get(
            "time",
            ""
        ),

        "reason": request.form.get(
            "reason",
            ""
        ).strip(),

        "status": "Pending",

        "created_at": datetime.now()

    }


    appointments_collection.insert_one(
        appointment
    )


    return redirect(
        url_for("appointments")
    )


# =========================================================
# UPDATE APPOINTMENT STATUS
# =========================================================

@app.route(
    "/appointments/status/<appointment_id>/<status>"
)
def update_appointment_status(
    appointment_id,
    status
):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    allowed_status = [

        "Pending",

        "Confirmed",

        "Completed",

        "Cancelled"

    ]


    if status not in allowed_status:

        return redirect(
            url_for("appointments")
        )


    try:

        appointments_collection.update_one(

            {
                "_id": ObjectId(appointment_id)
            },

            {
                "$set": {
                    "status": status
                }
            }

        )

    except Exception:

        pass


    return redirect(
        url_for("appointments")
    )


# =========================================================
# MEDICINES
# =========================================================

@app.route("/medicines")
def medicines():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    medicines_list = list(

        medicines_collection.find().sort(
            "_id",
            -1
        )

    )


    return render_template(

        "medicines.html",

        medicines=medicines_list

    )


# =========================================================
# ADD MEDICINE
# =========================================================

@app.route("/medicines/add", methods=["POST"])
def add_medicine():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    medicine = {

        "name": request.form.get(
            "name",
            ""
        ).strip(),

        "category": request.form.get(
            "category",
            ""
        ).strip(),

        "quantity": request.form.get(
            "quantity",
            "0"
        ).strip(),

        "price": request.form.get(
            "price",
            "0"
        ).strip(),

        "manufacturer": request.form.get(
            "manufacturer",
            ""
        ).strip(),

        "created_at": datetime.now()

    }


    medicines_collection.insert_one(
        medicine
    )


    return redirect(
        url_for("medicines")
    )


# =========================================================
# DELETE MEDICINE
# =========================================================

@app.route("/medicines/delete/<medicine_id>")
def delete_medicine(medicine_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    try:

        medicines_collection.delete_one(

            {
                "_id": ObjectId(medicine_id)
            }

        )

    except Exception:

        pass


    return redirect(
        url_for("medicines")
    )


# =========================================================
# BILLING
# =========================================================

@app.route("/billing")
def billing():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    bills = list(

        billing_collection.find().sort(
            "_id",
            -1
        )

    )


    patients_list = list(
        patients_collection.find()
    )


    return render_template(

        "billing.html",

        bills=bills,

        patients=patients_list

    )


# =========================================================
# ADD BILL
# =========================================================

@app.route("/billing/add", methods=["POST"])
def add_bill():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    try:

        consultation_fee = float(

            request.form.get(
                "consultation_fee",
                0
            ) or 0

        )

        medicine_charge = float(

            request.form.get(
                "medicine_charge",
                0
            ) or 0

        )

        room_charge = float(

            request.form.get(
                "room_charge",
                0
            ) or 0

        )

        lab_charge = float(

            request.form.get(
                "lab_charge",
                0
            ) or 0

        )

    except ValueError:

        return redirect(
            url_for("billing")
        )


    total = (

        consultation_fee +

        medicine_charge +

        room_charge +

        lab_charge

    )


    bill = {

        "patient_id": request.form.get(
            "patient_id",
            ""
        ),

        "patient_name": request.form.get(
            "patient_name",
            ""
        ).strip(),

        "consultation_fee": consultation_fee,

        "medicine_charge": medicine_charge,

        "room_charge": room_charge,

        "lab_charge": lab_charge,

        "total": total,

        "payment_status": "Unpaid",

        "created_at": datetime.now()

    }


    billing_collection.insert_one(
        bill
    )


    return redirect(
        url_for("billing")
    )


# =========================================================
# MARK BILL AS PAID
# =========================================================

@app.route("/billing/pay/<bill_id>")
def pay_bill(bill_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    try:

        billing_collection.update_one(

            {
                "_id": ObjectId(bill_id)
            },

            {
                "$set": {
                    "payment_status": "Paid"
                }
            }

        )

    except Exception:

        pass


    return redirect(
        url_for("billing")
    )


# =========================================================
# DASHBOARD API
# =========================================================

@app.route("/api/dashboard")
def dashboard_api():

    if "user_id" not in session:

        return jsonify(
            {
                "error": "Unauthorized"
            }
        ), 401


    data = {

        "patients":
            patients_collection.count_documents({}),

        "doctors":
            doctors_collection.count_documents({}),

        "appointments":
            appointments_collection.count_documents({}),

        "medicines":
            medicines_collection.count_documents({}),

        "bills":
            billing_collection.count_documents({})

    }


    return jsonify(data)


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("---------------------------------------")

    print("Hospital Management System")

    print("Server running on http://127.0.0.1:5000")

    print("---------------------------------------")

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )