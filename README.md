# AI-Powered Excel Mock Interviewer

**Prepared by:** Vanshika Mishra  

---

## 1. Executive Summary
The organization is experiencing rapid expansion across Finance, Operations, and Data Analytics divisions. Advanced proficiency in Microsoft Excel is a critical skill for new hires, directly impacting productivity and analytical decision-making.  

Traditional manual Excel interviews are time-consuming, inconsistent, and resource-intensive, causing delays and variability in candidate evaluation.  

**Project Objective:**  
To design and implement an automated, interactive Excel interview system that:  
- Evaluates candidate responses in real-time  
- Provides constructive inline feedback  
- Stores evaluation results for audit and analytics  
- Ensures fairness, efficiency, and a consistent assessment standard  

---

## 2. Project Goals
- **Structured Interview Flow:** Multi-turn experience mimicking human interviews, displaying one question at a time with instructions and motivational prompts.  
- **Intelligent Answer Evaluation:** Real-time scoring and constructive remarks for every answer.  
- **Interactive Feedback:** Dynamic, inline motivational messages to enhance engagement.  
- **Data Management:** Persistent storage of answers, scores, and remarks in a structured JSON database.  
- **Scalability:** Support for multiple concurrent candidates using session management and asynchronous backend evaluation.  

---

## 3. System Architecture

### 3.1 Overview
The system comprises three main integrated components:

| Component           | Purpose                                                  | Technology        |
|--------------------|----------------------------------------------------------|-----------------|
| Frontend (UI)       | Collects candidate info, presents questions, displays timer & feedback | Streamlit        |
| Backend (API Layer)  | Handles question retrieval, answer evaluation, summary aggregation | FastAPI          |
| Answer Evaluation    | Evaluates responses with structured scoring and remarks | Ollama LLM (Phi3:mini) |
| Async Handling       | Non-blocking evaluation and timeout management          | Python asyncio   |
| Data Layer           | Stores responses, scores, remarks                       | JSON files       |
| HTTP Requests        | Facilitates communication between frontend and backend | Python requests  |
| Utility Functions    | Random question selection, motivational feedback, timers | Python random, time |

**Architecture Diagram:**
+------------------+ +----------------+ +------------------+
| Streamlit UI | <--> | FastAPI API | <--> | JSON Database |
+------------------+ +----------------+ +------------------+

### 3.2 Frontend Design (Streamlit)
- **Welcome Page:** Captures candidate name, institute, and consent.  
- **Instructions Panel:** Clear guidelines for interview process.  
- **Question Flow:**  
  - One question per page  
  - Supports MCQ and text answers  
  - Motivational messages displayed intermittently  
- **Timer Management:** 30-minute countdown starts upon "Start Interview"  
- **Results Page:** Displays final scores, remarks, and candidate feedback input  

**Rationale:** Streamlit enables rapid prototyping, Python integration, minimal deployment overhead, and a clean, interactive interface.

### 3.3 Backend Design (FastAPI)
**Endpoints:**  
- `/questions`: Retrieves 25 random, preprocessed questions from `questions.json`.  
- `/evaluate`: Accepts candidate response, sends it to Ollama LLM, returns JSON with score (0–4) and remarks.  
- `/summary`: Aggregates all answers and generates performance summary.  

**Answer Evaluation Workflow:**  
1. Candidate submits answer via frontend  
2. Backend constructs structured prompt with question, response, and evaluation instructions  
3. LLM evaluates and returns score + remarks  
4. Backend stores results in JSON database and sends feedback to frontend  

**Technologies:**  
- FastAPI: Lightweight, asynchronous, performant  
- Python asyncio: Non-blocking evaluation  
- Ollama LLM (Phi3:mini): Structured, human-readable scoring  
- JSON Database: Simple, auditable, extendable  

### 3.4 Database & Data Storage
JSON files store:  
- Candidate name & institute  
- Question ID  
- Candidate response  
- Score & remarks  
- Timestamp  

This ensures easy retrieval, analytics, auditing, and future migration to relational databases.

---

## 4. Question Bank Strategy
- **Source:** Kaggle Excel datasets and top Excel interview questions  
- **Preprocessing:** Remove duplicates, standardize formatting, assign unique IDs, include metadata (question type, difficulty, expected answer)  
- **Storage:** `questions.json` with random sampling of 25 questions per candidate  

---

## 5. Evaluation Workflow
- Candidate submits answer → `/evaluate` endpoint  
- Backend constructs structured LLM prompt → evaluates answer  
- Structured scoring: 0–4, constructive remarks  
- STAR technique applied for scenario-based questions  
- Backend stores results → frontend displays score and feedback  

---

## 6. Session Management & State Handling
Streamlit session state maintains:  
- Current question index  
- Candidate responses  
- Timer & elapsed time  
- Motivational feedback messages  
- Skipped questions handled gracefully  
- State preserved even on slow interaction or page refresh  

---

## 7. Deployment Strategy
- **Frontend & Backend:** Streamlit Cloud  
- **Database:** JSON (with future option for relational DB)  
- **Scalability:** Async endpoints for multiple candidates  
- **Security:** HTTPS, input sanitization, session isolation  

---

## 8. Advantages of the Approach
- **Efficiency:** Reduces manual evaluation effort  
- **Consistency:** Standardized scoring, eliminates bias  
- **Interactive Experience:** Motivational prompts & inline feedback  
- **Data-Driven Insights:** Stored results allow analytics  
- **Scalable & Flexible:** Expandable for multiple candidates and new question sets  

---

## 9. Future Enhancements
- Dynamic question generation using NLP  
- Integration with candidate dashboards  
- Advanced analytics on performance  
- Migration to relational databases for enterprise scale  
- More complex evaluation rules and customizable feedback  

---

## 10. Conclusion
This project delivers a comprehensive, automated Excel interview system with:  
- Structured, interactive interview flow  
- Real-time LLM-based evaluation  
- Persistent storage of scores and remarks  
- Human-like motivational feedback  
- Efficient, scalable, and maintainable technology stack  

---

**Technologies Used:**  
- **Frontend:** Streamlit  
- **Backend:** FastAPI, Python asyncio  
- **Answer Evaluation:** Ollama LLM (Phi3:mini)  
- **Data Storage:** JSON files  
