import streamlit as st
import time
import cv2
import os
import face_recognition
import numpy as np
import mysql.connector as mc
import pandas as pd
import speech_recognition as sr
import pyttsx3
import random
import pickle
from datetime import datetime


# =========================================================
# LOAD KNOWN FACES
# =========================================================

@st.cache_data
def load_known_faces():

    if os.path.exists("encodings.pkl"):

        with open("encodings.pkl", "rb") as f:
            return pickle.load(f)

    known_encodings = []
    known_names = []

    base_folder = "face"

    os.makedirs(base_folder, exist_ok=True)

    for student_name in os.listdir(base_folder):

        folder = os.path.join(base_folder, student_name)

        if os.path.isdir(folder):

            for img_name in os.listdir(folder):

                img_path = os.path.join(folder, img_name)

                img = face_recognition.load_image_file(img_path)

                enc = face_recognition.face_encodings(img)

                if len(enc) > 0:

                    known_encodings.append(enc[0])

                    known_names.append(student_name)

    with open("encodings.pkl", "wb") as f:

        pickle.dump((known_encodings, known_names), f)

    return known_encodings, known_names


# =========================================================
# ATTENDANCE FUNCTION
# =========================================================

def run_attendance():

    # ================= SESSION =================

    if "step" not in st.session_state:
        st.session_state.step = 0

    if "name" not in st.session_state:
        st.session_state.name = None

    if "blink" not in st.session_state:
        st.session_state.blink = 0

    frame_count = 0

    # =====================================================
    # STEP 1 : FACE DETECTION
    # =====================================================

    if st.session_state.step == 1:

        frame_placeholder = st.empty()

        known_encodings, known_names = load_known_faces()

        cam = cv2.VideoCapture(0)

        name = None

        start_time = time.time()

        while True:

            ret, frame = cam.read()

            if not ret:
                continue

            frame = cv2.flip(frame, 1)

            gray_full = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            # ================= ANTI SPOOFING =================

            blur_value = cv2.Laplacian(gray_full,cv2.CV_64F).var()

            if blur_value < 50:

                cv2.putText(frame,"FAKE FACE / SCREEN DETECTED", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,0,255),2)

                frame_placeholder.image( frame, channels="BGR")

                continue

            # ================= SMALL FRAME =================

            small = cv2.resize(frame,(160,120))

            rgb_small = cv2.cvtColor(small,cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small)

            # ================= NO FACE =================

            if len(face_locations) == 0:

                cv2.putText(frame,"NO REAL FACE DETECTED",(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)

                frame_placeholder.image(frame,channels="BGR")

                continue

            # ================= MULTIPLE FACE BLOCK =================

            if len(face_locations) > 1:

                cv2.putText( frame, "ONLY ONE PERSON ALLOWED", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

                frame_placeholder.image(frame,channels="BGR")
                continue

            # ================= FACE SIZE CHECK =================

            top, right, bottom, left = face_locations[0]

            face_width = right - left
            face_height = bottom - top

            if face_width < 40 or face_height < 40:

                cv2.putText( frame,"MOVE CLOSER TO CAMERA",(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)

                frame_placeholder.image(frame,channels="BGR")
                continue

            # ================= FACE BOX =================

            cv2.rectangle( frame, (left*4, top*4), (right*4, bottom*4), (0,255,0), 2)

            frame_placeholder.image(frame,channels="BGR")

            # ================= FACE MATCH =================

            faces = face_recognition.face_encodings(rgb_small,face_locations)

            if len(faces) > 0:

                matches = face_recognition.compare_faces( known_encodings, faces[0], tolerance=0.5)

                if True in matches:

                    index = matches.index(True)

                    name = known_names[index]

                    st.success(f"✅ Face Matched: {name}")

                    time.sleep(2)

                    break

            # ================= TIMEOUT =================

            if time.time() - start_time > 10:
                break

        cam.release()

        frame_placeholder.empty()

        # ================= NEW USER =================

        if name is None:

            st.warning("⚠ New User Detected")

            new_name = st.text_input("Enter Your Name")

            if st.button("📸 Save Face"):

                folder = os.path.join("face",new_name)

                os.makedirs(folder, exist_ok=True)

                cam = cv2.VideoCapture(0)

                save_placeholder = st.empty()

                st.info( "📸 Capturing Real Face Images...")

                count = 0

                while count < 5:

                    ret, frame = cam.read()

                    if not ret:
                        continue

                    frame = cv2.flip(frame, 1)

                    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

                    blur = cv2.Laplacian(gray,cv2.CV_64F ).var()
                    
                    if blur < 50:

                        cv2.putText( frame,"FAKE FACE DETECTED",(20,40), cv2.FONT_HERSHEY_SIMPLEX,0.8, (0,0,255),2)
                           
                    
                        save_placeholder.image(frame,channels="BGR")
        
                        continue

                    rgb = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB )
                       
                       
                   

                    detected_faces = face_recognition.face_locations(rgb)

                    if len(detected_faces) != 1:

                        cv2.putText( frame, "SHOW ONLY ONE REAL FACE", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

                        save_placeholder.image(frame,channels="BGR")

                        continue

                    save_placeholder.image(frame,channels="BGR")

                    cv2.imwrite(os.path.join(folder,f"{count}.jpg"),frame)

                    count += 1

                    time.sleep(1)

                cam.release()

                if os.path.exists("encodings.pkl"):
                    os.remove("encodings.pkl")

                st.success( "✅ New Face Saved Successfully" )

                st.session_state.name = new_name

                st.session_state.step = 2

                st.rerun()

        else:

            st.session_state.name = name

            st.session_state.step = 2
    
    # STEP 2 : BLINK DETECTION
    # =====================================================

    if st.session_state.step == 2:

        eyes_blinks = np.random.randint(1, 4)

        st.write(f"👉 Please Blink Your Eyes {eyes_blinks} Times")

        frame_placeholder = st.empty()

        cam = cv2.VideoCapture(0)

        blink_count = 0

        eye_closed = False

        face_cascade = cv2.CascadeClassifier( cv2.data.haarcascades + 'haarcascade_frontalface_default.xml' )

        eye_cascade = cv2.CascadeClassifier( cv2.data.haarcascades + 'haarcascade_eye.xml')

        last_time = time.time()

        while True:

            ret, frame = cam.read()

            if not ret:
                continue

            frame = cv2.flip(frame, 1)

            gray = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )

            faces = face_cascade.detectMultiScale(gray,1.3,5 )

            for (x, y, w, h) in faces:

                cv2.rectangle(frame,(x, y),(x+w, y+h),(0, 255, 0),2)

                roi_gray = gray[y:y+h, x:x+w]

                roi_color = frame[y:y+h, x:x+w]

                eyes = eye_cascade.detectMultiScale(roi_gray,1.2,5)

                for (ex, ey, ew, eh) in eyes:

                    cv2.rectangle(roi_color,(ex, ey),(ex+ew, ey+eh),(255, 0, 0),2)

                # ================= REAL BLINK =================

                if len(eyes) == 0 and not eye_closed:

                    eye_closed = True

                    last_time = time.time()

                elif len(eyes) >= 2 and eye_closed:

                    blink_duration = (time.time() - last_time)

                    if blink_duration > 0.08:

                        blink_count += 1

                        eye_closed = False

            cv2.putText( frame, f"Blinks : {blink_count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            frame_placeholder.image(frame,channels="BGR")

            # ================= VERIFY =================

            if blink_count >= eyes_blinks:

                blink_count = eyes_blinks

                st.success( f"✅ Real Blink Verified ({blink_count})" )

                st.session_state.blink = blink_count

                st.session_state.step = 3

                break

        cam.release()

        st.rerun()

    
    # STEP 3 : VOICE DETECTION
    # =====================================================

    if st.session_state.step == 3:

        engine = pyttsx3.init()

        word = random.choice(["apple","python","india","water", "java","code" ])

        st.write(f"👉 Speak This Word for your attandace : **{word}**" )

        engine.say(word)
   
        engine.runAndWait()

        r = sr.Recognizer()

        for _ in range(5):

            try:

                with sr.Microphone() as source:

                    r.adjust_for_ambient_noise( source, duration=1)

                    audio = r.listen(source,timeout=5 )

                text = r.recognize_google(audio,language="en-IN")

                if text.lower() == word.lower():

                    st.success(f"✅ Voice Verified : {word}")

                    st.session_state.step = 4
                    break
                else:

                    st.warning("❌ Wrong Word, Try Again")

            except:

                st.warning("🎤 Mic Error")

    
    # STEP 4 : SAVE DATABASE
    # =====================================================

    if st.session_state.step == 4:

        db = mc.connect(
            host="localhost",
            user="root",
            password="1234",
            database="attendance_db"
        )

        cursor = db.cursor()

        now = datetime.now()

        cursor.execute(""" INSERT INTO attendance_log
            (
                student_name,
                blink_count,
                date_str,
                time_str
            )
            VALUES (%s,%s,%s,%s)
            """,
            (
                st.session_state.name,
                st.session_state.blink,
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S")
            )
        )

        db.commit()

        cursor.close()

        db.close()

        st.success(
            f"🎉 Attendance Saved For "
            f"{st.session_state.name}"
        )

        st.balloons()

        st.session_state.step = 0

   

#   SHOW RECORD 
# =========================================================

def show_record():

    st.subheader("📊 Attendance Records")

    # ================= DELETE BUTTON =================

    col1, col2 = st.columns([8,2])

    with col2:

        if st.button("🗑 Delete All"):

            try:

                db = mc.connect(
                    host="localhost",
                    user="root",
                    password="1234",
                    database="attendance_db"
                )

                cursor = db.cursor()

                # DELETE QUERY
                cursor.execute(
                    "TRUNCATE TABLE attendance_log"
                )

                db.commit()

                cursor.close()
                db.close()

                st.success(
                    "✅ All Records Deleted"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

    # ================= SHOW RECORDS =================

    try:

        db = mc.connect(
            host="localhost",
            user="root",
            password="1234",
            database="attendance_db"
        )

        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM attendance_log ORDER BY id DESC"
        )

        data = cursor.fetchall()

        columns = [col[0] for col in cursor.description]

        df = pd.DataFrame(
            data,
            columns=columns
        )

        if "time_str" in df.columns:

            df["time_str"] = (
                df["time_str"].astype(str)
            )

            df["time_str"] = df["time_str"].apply(
                lambda x: x.split(" ")[-1]
                if " " in x else x
            )

        st.dataframe(
            df,
            use_container_width=True
        )

        cursor.close()

        db.close()

    except Exception as e:

        st.error(str(e))