from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random, json
from ollama import chat
import asyncio

app = FastAPI(title="AI Excel Interviewer Backend")

# Load question bank
with open("db/questions.json", "r", encoding="utf-8") as f:
    question_bank = json.load(f)["questions"]

# -----------------------
# Request Models
# -----------------------
class AnswerSubmission(BaseModel):
    question_id: int
    user_answer: str

class SummaryRequest(BaseModel):
    user_name: str
    answers: list

# -----------------------
# Helper: Evaluate with timeout
# -----------------------
async def evaluate_with_timeout(prompt, timeout=10):
    try:
        loop = asyncio.get_event_loop()
        # Run chat in executor to avoid blocking
        response = await asyncio.wait_for(loop.run_in_executor(None, lambda: chat(
            model="phi3:mini", messages=[{"role": "user", "content": prompt}]
        )), timeout=timeout)
        result = json.loads(response['content'])
        # Validate score
        score = int(result.get("score", 0))
        remarks = result.get("remarks", "")
        return {"score": max(0, min(4, score)), "remarks": remarks}
    except Exception as e:
        return {"score": 0, "remarks": "Could not evaluate answer. Please try again."}

# -----------------------
# Endpoints
# -----------------------
@app.get("/questions")
def get_questions():
    if len(question_bank) < 25:
        raise HTTPException(status_code=400, detail="Not enough questions in question bank")
    selected_questions = random.sample(question_bank, 25)
    for q in selected_questions:
        q.pop("answer", None)
    return {"questions": selected_questions}

@app.post("/evaluate")
async def evaluate_answer(submission: AnswerSubmission):
    question_text = next((q.get("question", "") for q in question_bank if q["id"] == submission.question_id), None)
    if not question_text:
        raise HTTPException(status_code=404, detail="Question ID not found")

    prompt = f"""
You are an expert Excel interviewer and evaluator.
Evaluate the candidate's answer for the following question.

Question: {question_text}
Candidate Answer: {submission.user_answer}

Instructions:
- Evaluate the answer as correct, partially correct, or incorrect.
- Ignore minor spelling/formatting mistakes.
- Respond ONLY in JSON format:
  {{"score": <0-4>, "remarks": "Short constructive comment"}}
- 4 = fully correct, 2-3 = partially correct, 0 = incorrect.
- Do NOT hallucinate information.
"""

    return await evaluate_with_timeout(prompt, timeout=10)

@app.post("/summary")
async def generate_summary(summary: SummaryRequest):
    answers_with_context = []
    for a in summary.answers:
        q_text = next((q["question"] for q in question_bank if q["id"] == a["id"]), "")
        answers_with_context.append({
            "question": q_text,
            "user_answer": a["user_answer"],
            "score": a.get("score", 0)
        })

    prompt = f"""
You are an expert Excel interviewer. Analyze the candidate's answers.

Candidate: {summary.user_name}
Answers with context: {answers_with_context}

Instructions:
- Provide strengths, weaknesses, and actionable improvement suggestions.
- Output ONLY in JSON format:
  {{"strengths": "...", "weaknesses": "...", "suggestions": "..."}}
- Make it constructive, human-friendly, and concise.
"""

    return await evaluate_with_timeout(prompt, timeout=15)
