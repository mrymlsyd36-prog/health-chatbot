import streamlit as st
import os
import json
import hashlib
from PIL import Image

# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="HealthCare Chatbot",
    page_icon="🩺",
    layout="centered"
)

# =========================
# FILES
# =========================

USERS_FILE = "users.json"

# =========================
# USER DATABASE FUNCTIONS
# =========================

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# SESSION STATE
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Sign In"


# =========================
# SIGN UP
# =========================

def signup_page():

    st.title("🩺 HealthCare Chatbot")
    st.subheader("Create a New Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    if st.button("Create Account", use_container_width=True):

        if not name or not email or not password:
            st.error("Please fill in all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        elif len(password) < 6:
            st.error("Password must contain at least 6 characters.")

        else:

            users = load_users()

            email_key = email.lower().strip()

            if email_key in users:
                st.error("An account with this email already exists.")

            else:

                users[email_key] = {
                    "name": name,
                    "password": hash_password(password)
                }

                save_users(users)

                st.success(
                    "Account created successfully! "
                    "You can now Sign In."
                )

    st.write("")

    if st.button("Already have an account? Sign In"):
        st.session_state.page = "Sign In"
        st.rerun()


# =========================
# SIGN IN
# =========================

def signin_page():

    st.title("🩺 HealthCare Chatbot")
    st.subheader("Sign In")

    email = st.text_input("Email")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Sign In", use_container_width=True):

        users = load_users()
        email_key = email.lower().strip()

        if email_key not in users:
            st.error("Account not found.")

        elif users[email_key]["password"] != hash_password(password):
            st.error("Incorrect password.")

        else:

            st.session_state.logged_in = True
            st.session_state.username = users[email_key]["name"]

            st.success("Login successful!")

            st.rerun()

    st.write("")

    if st.button("Don't have an account? Sign Up"):
        st.session_state.page = "Sign Up"
        st.rerun()


# =========================
# HEALTH CHATBOT
# =========================

def chatbot_page():

    # SIDEBAR

    st.sidebar.title("🩺 HealthCare Chatbot")

    st.sidebar.write(
        f"Welcome, **{st.session_state.username}**"
    )

    st.sidebar.divider()

    if st.sidebar.button("Logout", use_container_width=True):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "Sign In"

        st.rerun()

    # MAIN PAGE

    st.title("🩺 HealthCare Chatbot")

    st.write(
        "Welcome to the HealthCare Chatbot. "
        "This system provides preliminary health guidance "
        "based on the information provided by the user."
    )

    st.info(
        "⚠️ This chatbot is for preliminary guidance only "
        "and does not replace a professional doctor."
    )

    # =========================
    # PATIENT INFORMATION
    # =========================

    st.header("👤 Patient Information")

    patient_name = st.text_input(
        "Patient Name",
        value=st.session_state.username
    )

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=20
    )

    gender = st.selectbox(
        "Gender",
        ["Male", "Female"]
    )

    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="Example: headache, fever, cough..."
    )

    # =========================
    # DISEASE SELECTION
    # =========================

    st.header("🔍 Select Health Condition")

    disease = st.selectbox(
        "Choose a condition",
        [
            "Select a condition",
            "Diabetes",
            "Anemia",
            "Hypertension",
            "Respiratory Problems",
            "Heart Problems",
            "General Health Check"
        ]
    )

    # =========================
    # TEST / X-RAY UPLOAD
    # =========================

    st.header("📄 Upload Test Result / X-Ray")

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Medical Image",
            use_container_width=True
        )

    # =========================
    # ANALYZE BUTTON
    # =========================

    if st.button(
        "🔎 Analyze Information",
        use_container_width=True
    ):

        if not patient_name:
            st.warning("Please enter the patient's name.")

        elif not symptoms:
            st.warning("Please describe the symptoms.")

        elif disease == "Select a condition":
            st.warning("Please select a health condition.")

        elif uploaded_file is None:
            st.warning(
                "Please upload a test result or X-ray."
            )

        else:

            st.success("Analysis completed.")

            st.header("📊 Preliminary Analysis")

            st.write(
                f"**Patient:** {patient_name}"
            )

            st.write(
                f"**Age:** {age}"
            )

            st.write(
                f"**Gender:** {gender}"
            )

            st.write(
                f"**Selected Condition:** {disease}"
            )

            st.write(
                f"**Reported Symptoms:** {symptoms}"
            )

            st.write(
                "The uploaded medical image has been received "
                "successfully."
            )

            # =========================
            # RESULTS
            # =========================

            st.subheader("Possible Indicators")

            if disease == "Diabetes":

                st.write(
                    "The selected condition may be associated "
                    "with blood glucose abnormalities."
                )

            elif disease == "Anemia":

                st.write(
                    "The selected condition may be associated "
                    "with low hemoglobin or iron deficiency."
                )

            elif disease == "Hypertension":

                st.write(
                    "The selected condition may be associated "
                    "with elevated blood pressure."
                )

            elif disease == "Respiratory Problems":

                st.write(
                    "The selected condition may involve "
                    "respiratory symptoms and requires "
                    "professional evaluation."
                )

            elif disease == "Heart Problems":

                st.write(
                    "Heart-related symptoms should be evaluated "
                    "by a qualified healthcare professional."
                )

            else:

                st.write(
                    "The information provided requires "
                    "professional medical evaluation."
                )

            # =========================
            # RECOMMENDED NEXT STEPS
            # =========================

            st.subheader("💡 Recommended Next Steps")

            st.write(
                "1. Review the uploaded test result with a doctor."
            )

            st.write(
                "2. Do not rely on the chatbot as a final diagnosis."
            )

            st.write(
                "3. Follow the doctor's recommended tests "
                "and treatment plan."
            )

            st.write(
                "4. If symptoms become severe or suddenly worsen, "
                "seek medical attention immediately."
            )


# =========================
# APPLICATION ROUTING
# =========================

if st.session_state.logged_in:

    chatbot_page()

else:

    if st.session_state.page == "Sign Up":

        signup_page()

    else:

        signin_page()