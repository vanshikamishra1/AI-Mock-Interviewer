#FRONTEND
import streamlit as st
import requests, time, random

API_URL = "http://127.0.0.1:8000"
INTERVIEW_DURATION = 30 * 60  # 30 minutes in seconds

st.set_page_config(page_title="AI Excel Interviewer", layout="wide")

# -----------------------
# Session State
# -----------------------
if "stage" not in st.session_state:
    st.session_state.stage = "welcome"
    st.session_state.name = ""
    st.session_state.college = ""
    st.session_state.rules_ack = False
    st.session_state.questions = []
    st.session_state.current_q = 0
    st.session_state.answers = []
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.timer_started = False
    st.session_state.feedback_message = ""
    st.session_state.feedback_expire = 0
    st.session_state._rerun_flag = False  
    st.session_state.top_message = ""  

# -----------------------
# Helper Functions
# -----------------------
def trigger_rerun():
    st.session_state._rerun_flag = not st.session_state._rerun_flag

def submit_answer(user_answer):
    q_id = st.session_state.questions[st.session_state.current_q]["id"]

    with st.spinner("Evaluating your answer..."):
        try:
            resp = requests.post(
                f"{API_URL}/evaluate",
                json={"question_id": q_id, "user_answer": user_answer},
                timeout=15
            )
            result = resp.json()
            score = result.get("score", 0)
            remarks = result.get("remarks", "")
        except:
            score = 0
            remarks = "Could not evaluate answer. Please try again."

    st.session_state.answers.append({
        "id": q_id,
        "question": st.session_state.questions[st.session_state.current_q]["question"],
        "user_answer": user_answer.strip(),
        "score": score,
        "remarks": remarks
    })
    st.session_state.current_q += 1

    # Intermittent motivational tips
    if st.session_state.current_q % random.randint(2, 4) == 0:
        tips = [
            "Remember to structure your answers clearly.",
            "Take a moment to think before answering.",
            "Good progress! Keep it up.",
            "Be concise and stay confident.",
            "Focus on the key Excel functions asked."
        ]
        st.session_state.feedback_message = random.choice(tips)
        st.session_state.feedback_expire = time.time() + 5
    else:
        st.session_state.feedback_message = ""

    trigger_rerun()  # simulate rerun

# -----------------------
# Timer Display
# -----------------------
def display_timer():
    if st.session_state.timer_started:
        remaining = int(st.session_state.end_time - time.time())
        if remaining <= 0:
            st.warning("Time is up! Interview has ended.")
            st.session_state.stage = "results"
            trigger_rerun()
        else:
            mins, secs = divmod(remaining, 60)
            st.sidebar.markdown(f"### ⏱ Time Remaining: {mins:02d}:{secs:02d}")

# -----------------------
# Welcome Page
# -----------------------
if st.session_state.stage == "welcome":
    st.title("AI-Powered Excel Interviewer")
    st.markdown("""
    ### Welcome Candidate!
    I am your **AI Interviewer**. This interactive session is designed to evaluate your Excel expertise efficiently and objectively. 
    You will receive questions, real-time guidance, and constructive feedback to help you demonstrate your skills to the fullest.
    """)

    st.session_state.name = st.text_input("Full Name", st.session_state.name)
    st.session_state.college = st.text_input("College / Institute", st.session_state.college)

    st.markdown("""
    ### Interview Guidelines
    - Total of **25 carefully curated questions** designed to assess your Excel proficiency.
    - **30-minute duration** (the timer begins once you click 'Start Interview').
    - Answers will be **evaluated in real-time** using the AI model `phi3:mini`.
    - Each question carries **4 marks**, with no negative marking.
    - Once an answer is submitted, it **cannot be modified**, so please review before submitting.
    """)

    st.session_state.rules_ack = st.checkbox("I have read and understood the instructions.")

    if st.button("Start Interview") and st.session_state.name and st.session_state.college and st.session_state.rules_ack:
        try:
            st.session_state.questions = requests.get(f"{API_URL}/questions").json()["questions"]
        except:
            st.session_state.questions = [{"id": i+1, "question": f"Mock Question {i+1}", "type": "text"} for i in range(5)]
        st.session_state.start_time = time.time()
        st.session_state.end_time = st.session_state.start_time + INTERVIEW_DURATION
        st.session_state.timer_started = True
        st.session_state.stage = "interview"
        trigger_rerun()
    else:
        st.stop()

# -----------------------
# Interview Page
# -----------------------
if st.session_state.stage == "interview":
    display_timer()  # Timer on sidebar

    # If all questions done, go to results
    if st.session_state.current_q >= len(st.session_state.questions):
        st.session_state.stage = "results"
        trigger_rerun()

    if st.session_state.stage == "interview":
        q = st.session_state.questions[st.session_state.current_q]

        # feedback
        if st.session_state.feedback_message and time.time() < st.session_state.feedback_expire:
            st.success(st.session_state.feedback_message)

        # Show gentle top message if last answer was empty
        if st.session_state.top_message:
            st.warning(st.session_state.top_message)
            st.session_state.top_message = ""  # reset after showing

        st.subheader(f"Question {st.session_state.current_q + 1}: {q['question']}")

        if q.get("type") == "mcq":
            user_ans = st.radio("Select your answer:", q.get("options", []), key=f"q_{q['id']}")
        else:
            user_ans = st.text_area("Your Answer:", key=f"q_{q['id']}", height=120)

        if st.button("Submit Answer"):
            # if User skips answer
            if not user_ans.strip():
                st.session_state.top_message = "You did not provide an answer. Previous question will be marked as unattempted."
            submit_answer(user_ans)

# -----------------------
# Results Page with inline strengths & weaknesses
# -----------------------
if st.session_state.stage == "results":
    total_questions = len(st.session_state.questions)
    attempted = sum(1 for a in st.session_state.answers if a["user_answer"].strip())
    unattempted = total_questions - attempted
    total_score = sum(a["score"] for a in st.session_state.answers)

    st.title("Interview Completed")
    st.success(f"Congratulations {st.session_state.name}, you have completed the AI Interview!")

    st.write(f"Total Questions: {total_questions}")
    st.write(f"Attempted: {attempted}")
    st.write(f"Unattempted: {unattempted}")
    st.write(f"Final Score: {total_score} / {total_questions*4}")

    
    strengths_list = [
        "Excellent clarity in answers.",
        "Strong logical structuring.",
        "Good attention to detail.",
        "Confident and concise.",
        "Demonstrates consistent knowledge."
    ]
    weaknesses_list = [
        "Needs to improve time management.",
        "Sometimes misses minor details.",
        "Could provide more examples.",
        "Needs more practice with advanced formulas.",
        "Occasionally vague in explanation."
    ]

    # Show individual remarks with inline strength & weakness
    for a in st.session_state.answers:
        st.markdown(f"Question: {a['question']}")
        st.markdown(f"Your Answer: {a['user_answer']}")
        # Randomly pick one strength & one weakness
        inline_strength = random.choice(strengths_list)
        inline_weakness = random.choice(weaknesses_list)
        st.markdown(f"Evaluation Remarks: {a['remarks']}")
        st.markdown(f"Note: Strength - {inline_strength} | Weakness - {inline_weakness}")
        st.markdown("---")

    # candidate feedback
    st.markdown("### Candidate Feedback")
    feedback = st.text_area("Please share your feedback about this interview experience:", height=120)
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback! It will help us improve.")

