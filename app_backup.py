import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Health Chatbot",
    page_icon="🩺",
    layout="centered"
)



# =========================================================
# SESSION STATE

# =========================================================

if "step" not in st.session_state:
    st.session_state.step = 1

if "name" not in st.session_state:
    st.session_state.name = ""

if "age" not in st.session_state:
    st.session_state.age = 0

if "gender" not in st.session_state:
    st.session_state.gender = ""

if "symptoms" not in st.session_state:
    st.session_state.symptoms = ""

if "duration" not in st.session_state:
    st.session_state.duration = ""

if "severity" not in st.session_state:
    st.session_state.severity = ""

if "previous_conditions" not in st.session_state:
    st.session_state.previous_conditions = ""

if "medications" not in st.session_state:
    st.session_state.medications = ""

if "file_name" not in st.session_state:
    st.session_state.file_name = ""

if "file_type" not in st.session_state:
    st.session_state.file_type = ""

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None


# =========================================================
# BLOOD TEST ANALYSIS FUNCTION
# =========================================================

def analyze_blood_test(text, gender):

    results = []

    # -----------------------------------------------------
    # Hemoglobin
    # -----------------------------------------------------

    hemoglobin = re.search(
        r"(?:hemoglobin|hb)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if hemoglobin:

        value = float(hemoglobin.group(1))

        if gender == "Female":
            low = 12
            high = 16
        else:
            low = 13
            high = 17

        if value < low:

            status = "Below the typical reference range ⚠️"

        elif value > high:

            status = "Above the typical reference range ⚠️"

        else:

            status = "Within the typical reference range ✅"

        results.append(
            f"Hemoglobin: {value} g/dL — {status}"
        )


    # -----------------------------------------------------
    # White Blood Cells
    # -----------------------------------------------------

    wbc = re.search(
        r"(?:wbc|white blood cells?)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if wbc:

        value = float(wbc.group(1))

        if 4 <= value <= 11:

            status = "Within the typical reference range ✅"

        else:

            status = "Outside the typical reference range ⚠️"

        results.append(
            f"WBC: {value} — {status}"
        )


    # -----------------------------------------------------
    # Glucose
    # -----------------------------------------------------

    glucose = re.search(
        r"(?:glucose|blood sugar)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if glucose:

        value = float(glucose.group(1))

        if value < 70:

            status = (
                "Below the typical fasting "
                "reference range ⚠️"
            )

        elif value <= 99:

            status = (
                "Within the typical fasting "
                "reference range ✅"
            )

        else:

            status = (
                "Above the typical fasting "
                "reference range ⚠️"
            )

        results.append(
            f"Glucose: {value} mg/dL — {status}"
        )


    # -----------------------------------------------------
    # Platelets
    # -----------------------------------------------------

    platelets = re.search(
        r"(?:platelets|plt)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if platelets:

        value = float(platelets.group(1))

        if 150 <= value <= 450:

            status = "Within the typical reference range ✅"

        else:

            status = "Outside the typical reference range ⚠️"

        results.append(
            f"Platelets: {value} — {status}"
        )


    # -----------------------------------------------------
    # Return Results
    # -----------------------------------------------------

    return results


# =========================================================
# SYMPTOM ANALYSIS
# =========================================================

def analyze_symptoms(symptoms):

    symptoms_lower = symptoms.lower()

    possible_indicators = []

    # Respiratory symptoms

    respiratory_words = [
        "cough",
        "coughing",
        "shortness of breath",
        "breathing",
        "chest pain"
    ]

    for word in respiratory_words:

        if word in symptoms_lower:

            possible_indicators.append(
                "Respiratory-related condition may require evaluation."
            )

            break


    # Fever

    fever_words = [
        "fever",
        "high temperature",
        "temperature"
    ]

    for word in fever_words:

        if word in symptoms_lower:

            possible_indicators.append(
                "Fever may be associated with an infection or "
                "other medical conditions."
            )

            break


    # Headache

    headache_words = [
        "headache",
        "head pain"
    ]

    for word in headache_words:

        if word in symptoms_lower:

            possible_indicators.append(
                "Headache may have several possible causes "
                "and may require further assessment."
            )

            break


    # Dizziness

    dizziness_words = [
        "dizziness",
        "dizzy",
        "lightheaded"
    ]

    for word in dizziness_words:

        if word in symptoms_lower:

            possible_indicators.append(
                "Dizziness can have several possible causes "
                "and may require medical evaluation."
            )

            break


    # Fatigue

    fatigue_words = [
        "fatigue",
        "tired",
        "weakness",
        "weak"
    ]

    for word in fatigue_words:

        if word in symptoms_lower:

            possible_indicators.append(
                "Fatigue or weakness may have multiple possible "
                "causes and should be evaluated with other findings."
            )

            break


    return possible_indicators
def generate_recommendations(symptoms, blood_results):

    recommendations = []
    indicators = []

    symptoms_lower = symptoms.lower()

    low_hemoglobin = any(
        "Hemoglobin:" in result
        and "Below" in result
        for result in blood_results
    )

    if low_hemoglobin:

        indicators.append(
            "The symptoms and low hemoglobin result "
            "may be consistent with an anemia-related pattern."
        )

        recommendations.append(
            "Discuss the hemoglobin result with a healthcare professional."
        )

        recommendations.append(
            "A doctor may consider additional tests to determine "
            "the possible cause."
        )

    glucose_high = any(
        "Glucose:" in result
        and "Above" in result
        for result in blood_results
    )

    if glucose_high:

        indicators.append(
            "The glucose result is above the illustrative "
            "fasting reference range."
        )

        recommendations.append(
            "Discuss the glucose result with a healthcare professional."
        )

    abnormal_wbc = any(
        "WBC:" in result
        and "Outside" in result
        for result in blood_results
    )

    if abnormal_wbc:

        indicators.append(
            "The WBC result is outside the illustrative "
            "reference range."
        )

        recommendations.append(
            "The WBC result should be interpreted together "
            "with symptoms and other clinical findings."
        )

    if not indicators:

        indicators.append(
            "No specific pattern was identified from "
            "the available information."
        )

        recommendations.append(
            "Continue monitoring your symptoms and discuss "
            "the results with a healthcare professional."
        )

    return indicators, recommendations


# =========================================================
# STEP 1 - PATIENT INFORMATION
# =========================================================

if st.session_state.step == 1:

    st.title("🩺 Health Chatbot")

    st.write(
        "Welcome! Let's understand your symptoms first."
    )

    st.info(
        "This chatbot provides general health information "
        "and is not a substitute for a professional medical diagnosis."
    )


    # -----------------------------------------------------
    # Patient Information
    # -----------------------------------------------------

    st.header("Patient Information")


    name = st.text_input(
        "What is your name?"
    )


    age = st.number_input(
        "What is your age?",
        min_value=1,
        max_value=120,
        step=1
    )


    gender = st.selectbox(
        "Gender",
        [
            "Select",
            "Female",
            "Male"
        ]
    )


    # -----------------------------------------------------
    # Symptoms
    # -----------------------------------------------------

    st.header("Symptoms")


    symptoms = st.text_area(
        "Please describe your symptoms:",
        placeholder=(
            "Example: headache, fever, cough..."
        )
    )


    duration = st.selectbox(
        "How long have you had these symptoms?",
        [
            "Select",
            "Less than 1 day",
            "1-3 days",
            "4-7 days",
            "More than a week"
        ]
    )


    severity = st.selectbox(
        "How severe are your symptoms?",
        [
            "Select",
            "Mild",
            "Moderate",
            "Severe"
        ]
    )


    previous_conditions = st.text_area(
        "Do you have any previous medical conditions?",
        placeholder=(
            "Example: diabetes, asthma, hypertension..."
        )
    )


    medications = st.text_area(
        "Are you currently taking any medications?",
        placeholder=(
            "Write the medication names "
            "or type 'None'."
        )
    )


    # -----------------------------------------------------
    # Continue Button
    # -----------------------------------------------------

    if st.button("Continue"):


        if not name or not symptoms:

            st.warning(
                "Please enter your name and describe your symptoms."
            )


        elif (
            gender == "Select"
            or duration == "Select"
            or severity == "Select"
        ):

            st.warning(
                "Please answer all required questions."
            )


        else:

            # Save information

            st.session_state.name = name

            st.session_state.age = age

            st.session_state.gender = gender

            st.session_state.symptoms = symptoms

            st.session_state.duration = duration

            st.session_state.severity = severity

            st.session_state.previous_conditions = (
                previous_conditions
            )

            st.session_state.medications = medications


            # Move to Step 2

            st.session_state.step = 2

            st.rerun()


# =========================================================
# STEP 2 - MEDICAL EVIDENCE
# =========================================================

elif st.session_state.step == 2:

    st.title("🩺 Medical Evidence")


    st.success(
        f"Thank you, {st.session_state.name}!"
    )


    st.write(
        "To provide a better assessment, "
        "please upload a medical test, X-ray, "
        "or medical report."
    )


    # -----------------------------------------------------
    # File Type
    # -----------------------------------------------------

    file_type = st.selectbox(
        "What type of file do you want to upload?",
        [
            "Select",
            "Blood Test",
            "Urine Test",
            "X-Ray",
            "Medical Report"
        ]
    )


    # -----------------------------------------------------
    # File Upload
    # -----------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload your file",
        type=[
            "png",
            "jpg",
            "jpeg",
            "pdf"
        ]
    )


    # -----------------------------------------------------
    # Analyze Button
    # -----------------------------------------------------

    if uploaded_file:

        st.success(
            f"File uploaded successfully: "
            f"{uploaded_file.name}"
        )


        if st.button("Analyze My Information"):


            st.session_state.file_name = (
                uploaded_file.name
            )


            st.session_state.file_type = (
                file_type
            )


            st.session_state.uploaded_file = (
                uploaded_file
            )


            st.session_state.step = 3


            st.rerun()


# =========================================================
# STEP 3 - ANALYSIS
# =========================================================

elif st.session_state.step == 3:

    st.title(
        "🔍 Health Information Analysis"
    )


    st.success(
        "Analysis completed successfully."
    )


    # -----------------------------------------------------
    # Patient Summary
    # -----------------------------------------------------

    st.subheader(
        "Patient Information"
    )


    st.write(
        f"**Name:** {st.session_state.name}"
    )


    st.write(
        f"**Age:** {st.session_state.age}"
    )


    st.write(
        f"**Gender:** {st.session_state.gender}"
    )


    st.write(
        f"**Symptoms:** {st.session_state.symptoms}"
    )


    st.write(
        f"**Symptom Duration:** "
        f"{st.session_state.duration}"
    )


    st.write(
        f"**Severity:** "
        f"{st.session_state.severity}"
    )


    st.write(
        f"**Uploaded File:** "
        f"{st.session_state.file_name}"
    )


    # -----------------------------------------------------
    # Symptom Analysis
    # -----------------------------------------------------

    st.subheader(
        "🩺 Symptom Review"
    )


    symptom_results = analyze_symptoms(
        st.session_state.symptoms
    )


    if symptom_results:

        for result in symptom_results:

            st.write(
                "•",
                result
            )

    else:

        st.info(
            "No specific symptom pattern was identified. "
            "Further medical evaluation may be needed."
        )


    # -----------------------------------------------------
    # File Analysis
    # -----------------------------------------------------

    st.subheader(
        "📄 Medical File Analysis"
    )


    uploaded_file = (
        st.session_state.uploaded_file
    )


    if uploaded_file is not None:


        # =================================================
        # BLOOD TEST / MEDICAL REPORT / URINE TEST
        # =================================================

        if st.session_state.file_type in [
            "Blood Test",
            "Urine Test",
            "Medical Report"
        ]:


            try:


                # Read image

                image = Image.open(
                    uploaded_file
                )


                st.image(
                    image,
                    caption="Uploaded Medical File",
                    use_container_width=True
                )


                # -----------------------------------------
                # OCR
                # -----------------------------------------

                with st.spinner(
                    "Reading the medical file..."
                ):


                    reader = easyocr.Reader(
                        ["en"]
                    )


                    result = reader.readtext(
                        np.array(image),
                        detail=0
                    )


                    extracted_text = "\n".join(
                        result
                    )


                # -----------------------------------------
                # Display Extracted Text
                # -----------------------------------------

                st.subheader(
                    "📝 Extracted Information"
                )


                if extracted_text.strip():


                    st.text_area(
                        "Information detected in the file:",
                        extracted_text,
                        height=250
                    )


                else:


                    st.warning(
                        "No readable text was detected "
                        "in the image."
                    )


                # -----------------------------------------
                # Blood Test Analysis
                # -----------------------------------------

                if (
                    st.session_state.file_type
                    == "Blood Test"
                ):


                    st.subheader(
                        "🧪 Blood Test Analysis"
                    )


                    blood_results = (
                        analyze_blood_test(
                            extracted_text,
                            st.session_state.gender
                        )
                    )


                    if blood_results:


                        for result in blood_results:

                            st.write(
                                "•",
                                result
                            )


                    else:


                        st.info(
                            "No supported blood-test values "
                            "were detected."
                        )


                    st.warning(
                        "Reference ranges are illustrative "
                        "and may vary between laboratories."
                    )


            except Exception as error:


                st.error(
                    "We could not read this file as an image."
                )


        # =================================================
        # X-RAY
        # =================================================

        elif (
            st.session_state.file_type
            == "X-Ray"
        ):


            try:


                image = Image.open(
                    uploaded_file
                )


                st.image(
                    image,
                    caption="Uploaded X-Ray",
                    use_container_width=True
                )


                st.info(
                    "The X-Ray image was received successfully. "
                    "Image-based medical interpretation requires "
                    "a specialized medical imaging model."
                )


            except Exception:


                st.error(
                    "The X-Ray image could not be displayed."
                )


    # =====================================================
    # POSSIBLE INDICATORS
    # =====================================================

    st.subheader(
        "🔎 Possible Indicators"
    )

if st.session_state.file_type == "Blood Test":

    blood_results = analyze_blood_test(
        extracted_text,
        st.session_state.gender
    )

    indicators, recommendations = generate_recommendations(
        st.session_state.symptoms,
        blood_results
    )

else:

    indicators, recommendations = generate_recommendations(
        st.session_state.symptoms,
        []
    )


for indicator in indicators:
    st.write("•", indicator)


st.subheader(
    "📋 Recommended Next Steps"
)

for recommendation in recommendations:
    st.write("•", recommendation)


st.warning(
    "These results are educational indicators only "
    "and are not a confirmed medical diagnosis."
)
   # =====================================================
# MEDICAL DISCLAIMER
# =====================================================

st.divider()

st.caption(
    "⚠️ Medical Disclaimer: This chatbot is an "
    "educational prototype. It does not replace "
    "professional medical advice, diagnosis, or treatment."
)


# =====================================================
# START NEW ASSESSMENT
# =====================================================

if st.button("Start New Assessment"):

    st.session_state.clear()

    st.rerun()