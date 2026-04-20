# AI Resume Screening & Interview Management System
## Final Year Project - Comprehensive Explanation Guide

This document provides a complete, step-by-step technical and functional breakdown of the AI Resume Screening System. It is designed to help you confidently explain your final year project to your faculty, covering all logic, workflow steps, and features.

---

## 1. Project Overview & Motivation
**What it is:** A comprehensive recruitment platform bridging the gap between applicants and recruiters with the help of AI and automation.
**Problem it Solves:** Manual resume screening is biased and time-consuming. Coordinating interviews involves a lot of back-and-forth emails. 
**Solution:** This system uses Natural Language Processing (NLP) to read, anonymize (remove bias), and rank resumes. It also automates the entire hiring pipeline from screening questions to scheduling and conducting interviews.

---

## 2. Key Features & Their Working Logic

### A. Role-Based Access Control (Authentication)
*   **Feature:** Allows two distinct types of users to the platform: **Applicants** and **Recruiters**.
*   **Working:** Passwords are encrypted using modern hashing techniques (`bcrypt`). The application uses session-based authentication to track whether a user is logged in as a recruiter or an applicant, dynamically shifting what dashboard features they have access to.

### B. AI Resume Parsing & Anonymization Engine
*   **Feature:** Extracts data from uploaded resumes and hides identifiable information to ensure unbiased hiring.
*   **Working Logic:**
    1.  **Text Extraction:** When an applicant uploads a PDF, DOCX, or TXT file, the backend (`PyPDF2`, `docx`) reads the physical file and converts it into a continuous string of raw text.
    2.  **Anonymization (Bias Removal):** The code uses Regular Expressions (`Regex`) to find patterns representing Emails, Phone Numbers, and Gender-specific words (he/she/him/her). It replaces these strings with generic placeholders like `[EMAIL]` or `[PHONE]`. It also scans the first few lines to detect and remove the candidate's name.

### C. Skill Matching & TF-IDF Scoring Model
*   **Feature:** Automatically scores resumes against the Job Description.
*   **Working Logic:**
    1.  **Contextual Similarity:** We use **TF-IDF Vectorization** (Term Frequency - Inverse Document Frequency) and **Cosine Similarity** from the `Scikit-Learn` machine learning library. It compares the semantic context of the anonymized resume against the job description to output a base percentage match.
    2.  **Keyword Intersection:** The text is scanned against a pre-defined database of critical skills (Python, Java, Machine Learning, etc.). It calculates a "Skill Score" based on how many required skills the candidate possesses.
    3.  **Experience Extraction:** A regex formula extracts the numeric years of experience mentioned in the resume.
    4.  **Final Score Calculation:** The final rating is a weighted sum (60% TF-IDF similarity, 40% Keyword matching) which ranks all applicants automatically on the recruiter's dashboard.

### D. Advanced Recruitment Pipeline
*   **Feature:** The lifecycle of an application going through defined stages.
*   **Working Logic:** A status field tracks the application dynamically updating the UI. The flow is:
    `Pending` ➔ `Selected` ➔ `Questions Answered` ➔ `Interview Scheduled` ➔ `Interviewed` ➔ `Hired / Rejected`

### E. Custom Screening Questions
*   **Feature:** Recruiters can define job-specific questions, and selected applicants must answer them before an interview is scheduled.
*   **Working Logic:** Recruiters add questions to the database linked to the specific Job ID. When an applicant is selected for the next round, their dashboard prompts them to answer these questions. The answers are stored in a dedicated `interview_responses` table accessible to the recruiter.

### F. Automated Interview Scheduling & Notifications
*   **Feature:** Real-time feedback and scheduling without external emails.
*   **Working Logic:**
    1.  When a recruiter schedules an interview, the system assigns a unique auto-generated `room_id`.
    2.  **Notification System Engine:** Whenever critical actions occur (e.g., Recruiter selects a candidate, or Applicant answers questions), the backend immediately inserts a new record into the `notifications` database table linked to the target user's ID. 
    3.  **Real-Time Retrieval:** The next time that user (applicant or recruiter) refreshes their dashboard or clicks the Notifications tab, the system queries the database (`SELECT * FROM notifications WHERE user_id=? AND is_read=0`) and displays the alert in the portal, creating a seamless, automated, two-way communication loop without relying on external emails.
    4.  **Rescheduling Notifications:** If a recruiter changes the time, the backend dynamically alerts the applicant of the new date, and simultaneously sends a confirmation receipt to the recruiter's portal.

### G. Virtual Interview Room & Live Camera Access
*   **Feature:** A dedicated URL and UI space for the actual interview, featuring live hardware integration.
*   **Working Logic:** 
    1. **Room Access Validation:** Both the recruiter and candidate join the same unique routing URL (`/interview-room/<room_id>`). The backend first verifies if the current time matches the scheduled time. If the interview hasn't started, the system automatically redirects them to an `interview_waiting.html` lobby. 
    2. **Live Camera & Microphone Access:** The interview room utilizes the browser's built-in **WebRTC Web Audio/Video APIs** (`navigator.mediaDevices.getUserMedia`). When the page loads, Javascript requests the client's permission and directly binds their local camera and microphone stream to a live HTML `<video>` element. Features to mute/unmute and turn off the camera dynamically pause these tracking streams.
    3. **Screen Sharing:** Uses `navigator.mediaDevices.getDisplayMedia` to allow the user's screen capture to be broadcasted seamlessly in the UI.
    4. **Post-Interview Processing:** Once the interview is complete, the recruiter submits notes and a rating (1 to 5 stars) from a side panel, which triggers the backend routing to update the SQLite database to `interviewed` status, unlocking the final `Hired` option.

---

## 3. Technology Stack & Backend Architecture
*   **How the Backend Works (Flask Architecture):** 
    *   **Routing System:** The `app.py` file uses Flask `@app.route` decorators to listen for HTTP requests (like clicking a link or submitting a form) from the frontend browser.
    *   **Data Processing:** When a request hits a route (e.g., uploading a resume), backend Python functions execute the core logic, such as extracting text or calculating ML scores.
    *   **Database Interactions:** The backend explicitly opens a connection to `SQLite3`, runs parameterized SQL commands (`INSERT`, `UPDATE`, `SELECT`) to securely save or fetch statuses, and then commits the changes to structure the app's memory.
    *   **Templating:** Finally, the backend passes variables directly to the HTML using Jinja2 templating (`render_template`), which dynamically builds the webpage the user sees.
*   **Backend Framework:** Python with Flask (Lightweight server processing, Application Routing)
*   **Database:** SQLite3 (Relational structuring of Users, Jobs, Notifications, and Interviews)
*   **Frontend Design:** HTML5, CSS3, Jinja2 Templating
*   **AI / Machine Learning:** `scikit-learn` (TF-IDF Vectorizer, Cosine Similarity)
*   **Security:** `bcrypt` for secure hashing
*   **File Parsing:** `PyPDF2` (PDFs), `python-docx` (Word Docs)
*   **Document Generation:** `fpdf` (generates PDF resumes dynamically from parsed text)

---

## 4. How to Explain Step-by-Step Flow to Faculty

If faculty asks: **"Show me how your project works from start to finish?"**, demonstrate this sequence:

1.  **Recruiter Setup:** Log in as a Recruiter. Navigate to "Post Job". Add a title, description, and list required skills.
2.  **Job Posting:** Point out that the job is now live in the system database. 
3.  **Applicant Journey:** Open an incognito window. Log in as an Applicant. Go to the Jobs feed and click Apply. Upload a Resume PDF.
4.  **The "Magic" Step (AI Explanation):** Explain to the faculty that behind the scenes right now, Python is ripping the text from the PDF, stripping away the name and gender to remove bias, and applying Machine Learning mathematical models (TF-IDF) to score the applicant out of 100%. 
5.  **Recruiter Review:** Go back to the Recruiter window. Open the application. Show the AI Match Score, highlight Missing/Matched skills, and show the Anonymized text output. 
6.  **Screening:** Select the applicant. Explain the notification system triggering an alert for the candidate.
7.  **Interview Workflow:** Have the Candidate answer the custom screening questions. Have the Recruiter review the answers, Schedule an Interview, and demonstrate the Waiting Room logic. Finally, provide feedback and click **Hire**. 

---

## 5. Potential Defense Questions & Answers

*   **Q: Why use TF-IDF instead of simple keyword matching?**
    *   *Answer:* "Simple keyword matching only looks at exact words and fails to understand the overall context or length of the document. TF-IDF gives more mathematical weight to unique and important words within the scope of the description, making our matching algorithm far more robust and intelligent."
*   **Q: How does the anonymizer maintain data accuracy without deleting relevant content?**
    *   *Answer:* "Instead of simply deleting blocks of text, we utilized Regular Expressions (Regex) that specifically hunt for logical patterns like `@gmail.com` structures or `+1-` phone patterns, substituting them perfectly. For names, it limits its search safely to the header (first 3 lines) to avoid deleting regular capitalized terminology."
*   **Q: How secure are passwords in your database?**
    *   *Answer:* "We do not store plain-text passwords. We use `bcrypt` which uses mathematical salting and hashing. Even if the database was compromised, the passwords are functionally mathematically impossible to decrypt."
*   **Q: What happens if an applicant uploads a corrupted file type?**
    *   *Answer:* "The backend has error handling inside `extract_text_from_file()`. If `PyPDF2` fails to read it, the system safely falls back to returning empty text alerting the user, rather than explicitly crashing the web app."

---

## 6. Future Scope

If the faculty asks: **"What could be the future enhancements for this project?"**, you can discuss the following ideas:

1.  **Deep Learning / Transformer Models:** Upgrading the current TF-IDF keyword vectorization engine to a more advanced Transformer-based NLP model (like BERT or OpenAI APIs) to understand the semantic nuances of a resume with even higher accuracy.
2.  **Live Video Analytics:** Implementing Real-time Emotion Detection or Speech-to-Text transcription during the live WebRTC video interview to provide the recruiter with automated AI insights on candidate confidence and communication skills.
3.  **External Third-Party Notifications:** Integrating SMS (via Twilio) or external email support (via SendGrid/SMTP) to instantly push database alerts directly to the user's phone or email inbox for immediate interview updates.
4.  **Recruiter Analytics Dashboard:** Adding a specialized dashboard utilizing charting libraries (like `Chart.js`) to display visual metrics—such as application drop-off rates, average time-to-hire, and keyword popularity over time.
5.  **Automated Background Checks & Integrations:** Building API hooks to allow the platform to automatically export finalized hiring data into larger corporate ERP/HR systems (like Workday) or perform automated LinkedIn profile scraping to verify resume claims.
