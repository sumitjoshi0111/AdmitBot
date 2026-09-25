# AdmitBot – AI-Based College Admission Counselling Chatbot

## 1. Project Description

AdmitBot is a simple, rule-based AI chatbot that helps Maharashtra
engineering admission aspirants (MHT-CET students, DSE diploma
students, Class 12 students, and parents) with:

- Admission-related FAQs and terminology explanations
- A basic, sample-data-based college prediction (HIGH / MEDIUM / LOW)
- Guidance towards human counselling via the related **AdmitPro**
  project

AdmitBot is a **standalone** application. It is not integrated into
AdmitPro's backend or database — the two are connected only through a
simple "Ask AdmitBot" link/button, in either direction.

This is a **college mini-project prototype**, not a production system.

## 2. Features

1. Chat interface (Bootstrap-based)
2. Greeting messages
3. Admission FAQ answering
4. Admission terminology explanations
5. Rule-based / keyword-based intent detection
6. Student rank collection
7. Category collection
8. Preferred branch collection
9. Sample-data-based college prediction
10. HIGH / MEDIUM / LOW classification
11. Conversation context (remembers rank/category/branch during the session)
12. Fallback response for unsupported/out-of-scope questions
13. Counselling information + link to AdmitPro
14. Clear Chat button
15. Responsive Bootstrap UI
16. Suggested-question quick buttons

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Bootstrap 5, JavaScript (fetch API) |
| Backend | Python, Flask |
| Data storage | JSON (FAQs) and CSV (college cutoffs) |
| Chatbot logic | Rule-based / keyword-based intent detection (Python) |
| Session/context | Flask's built-in signed-cookie session |

No React, no Java/Spring Boot, no MySQL, no Docker, no external AI/LLM
API is used in this version — everything runs with plain Flask.

## 4. Project Structure

```
AdmitBot/
│
├── app.py              # Flask app: routes (/  , /chat, /clear)
├── chatbot.py           # Intent detection, FAQ search, slot-filling, context
├── predictor.py          # Loads colleges.csv, runs HIGH/MEDIUM/LOW logic
├── requirements.txt
├── README.md
│
├── data/
│   ├── faq.json          # FAQ question/answer/keyword data
│   └── colleges.csv       # SAMPLE cutoff dataset
│
├── templates/
│   └── index.html         # Chat UI page
│
└── static/
    ├── style.css           # Chat UI styling
    └── script.js            # Frontend logic (fetch calls, DOM updates)
```

## 5. How the Chatbot Works

1. The browser sends the user's typed message to `POST /chat` as JSON.
2. `app.py` loads the current session's context (rank/category/branch/stage)
   and passes the message + context to `chatbot.get_response(...)`.
3. `chatbot.py`:
   - If the bot is in the middle of collecting rank/category/branch
     (a "stage"), it tries to parse the expected value from the message.
   - Otherwise, it classifies the message into an **intent**:
     `GREETING`, `FAQ`, `PREDICTION`, `COUNSELLING`, or `UNKNOWN`,
     using simple keyword matching (see `detect_intent()`).
   - `FAQ` intent → looks up an answer in `data/faq.json` by keyword match.
   - `PREDICTION` intent → collects any missing rank/category/branch
     (one question at a time), then calls `predictor.predict(...)`.
   - `COUNSELLING` intent → returns the AdmitPro link message.
   - `UNKNOWN` → returns a fixed, honest fallback message.
4. The updated context is saved back into the Flask session.
5. The response text is sent back as JSON and displayed in the chat UI.

This is a **rule-based / keyword-based intent detection system** — it
is not a machine-learning model, and the project does not claim it is.
This is intentional and appropriate for a mini-project (see Section 20,
Rule 7 & 8 of the original project brief).

## 6. Prediction Logic (Deterministic Rule)

Implemented in `predictor.py`. For a given student rank and a stored
`closing_rank` for a college+branch+category:

```
if student_rank <= 0.8 * closing_rank:      HIGH
elif student_rank <= closing_rank:          MEDIUM
elif student_rank <= 1.2 * closing_rank:    LOW
else:                                       not shown (too far beyond cutoff)
```

- A **lower** rank number means **better** merit (rank 1 is the best).
- The 0.8 / 1.2 thresholds are simple, clearly-defined constants at the
  top of `predictor.py` (`HIGH_FACTOR`, `LOW_FACTOR`) so they are easy
  to explain and adjust.
- No cutoff numbers are ever invented — if no row matches the given
  category + branch, or the rank is too far beyond every closing rank,
  AdmitBot clearly says so instead of guessing.

## 7. Dataset Explanation

`data/colleges.csv` contains a **small, hand-made SAMPLE dataset**
(3 colleges × 3 branches × 5 categories = 45 rows) used only to
demonstrate how prediction works.

**This is NOT official, current MHT-CET/CAP cutoff data.** Real
admission decisions must be based on official DTE Maharashtra / CAP
data, not this file.

Columns: `College, Branch, Category, Closing_Rank`

## 8. Installation

```bash
# 1. Clone/copy the project folder, then move into it
cd AdmitBot

# 2. (Recommended) create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 9. How to Run

```bash
python app.py
```

Then open your browser at:

```
http://127.0.0.1:5000
```

## 10. Example Conversations

**FAQ:**
```
User: What is CAP?
Bot:  CAP stands for Centralized Admission Process...
```

**Prediction (step-by-step):**
```
User: My rank is 2500
Bot:  Great. What is your category? (Available in sample data: OPEN, OBC, SC, ST, EWS)

User: OBC
Bot:  Which branch are you interested in? (e.g., Computer Engineering, ...)

User: Computer Engineering
Bot:  Based on rank 2500, category OBC, branch Computer Engineering
      (using SAMPLE demonstration cutoff data, not official data):
      - PICT Pune (Computer Engineering, OBC): HIGH (sample closing rank: 3500)
      Note: This is an indication based on sample data only, not a guarantee of admission.
```

**Reusing context:**
```
User: What colleges can I get?
Bot:  (reuses the rank/category/branch already given, shows the same result)
```

**Counselling:**
```
User: I want counselling
Bot:  ... You can get full counselling support through AdmitPro.
      Open AdmitPro: PLACEHOLDER_ADMITPRO_URL
```

**Out of scope:**
```
User: Who is the Prime Minister?
Bot:  I am AdmitBot and I currently focus on engineering admission
      and counselling queries. Please ask me about CAP, CET, rank,
      category, branches, colleges, or counselling.
```

## 11. Limitations

- Uses a small sample dataset, not live/official cutoff data.
- Intent detection is keyword-based, not a trained NLP/ML model —
  unusual phrasing may not always be understood.
- No login/authentication — sessions are anonymous and browser-based.
- No real connection to AdmitPro's database; the AdmitPro link is a
  placeholder (`PLACEHOLDER_ADMITPRO_URL`) until a real deployed URL
  is available.
- Session context is stored in a Flask cookie, so it resets if cookies
  are cleared or a different browser/device is used.

## 12. Future Scope

- Replace the sample CSV with a real, regularly-updated cutoff dataset.
- Optional LLM API integration for more natural phrasing (while still
  keeping cutoff numbers strictly database-driven, never LLM-generated).
- Voice-based interaction.
- Marathi/Hindi language support.
- Real AdmitPro integration (once/if deeper integration is decided).
- Optional user login to save conversation history across sessions.
- Real-time admission data during live CAP rounds.

---
**This is a college-level prototype using sample demonstration data.**
