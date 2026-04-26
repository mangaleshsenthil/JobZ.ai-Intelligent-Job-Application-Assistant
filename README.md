# JobZ.ai: Intelligent Job Application Assistant 💼

An AI-powered full-stack application designed to streamline the job search process. JobsAI automates resume analysis, discovers highly relevant jobs, dynamically tailors application materials, and provides a hands-free auto-apply experience.

## 🌟 Key Features

- **Intelligent Resume Parsing:** Extracts skills, experiences, and core competencies from a single PDF upload using the Google Gemini API.
- **Semantic Job Matching:** Searches for live job listings and scores them against your profile using a hybrid of Keyword Matching and Deep Semantic Similarity (`sentence-transformers`).
- **Skill Gap Analysis & Learning Paths:** Identifies missing skills for lower-scoring matches and suggests concrete learning resources/courses to help you level up.
- **Dynamic Resume Tailoring:** Generates a custom-tailored PDF resume optimized for the specific keywords and requirements of your target job.
- **Automated Form Submission (Auto-Apply):** Utilizes **Playwright** to launch a browser session, purposefully navigate job portals, and intelligently fill out application forms with your data—leaving only final review and CAPTCHAs to you.
- **Interview Q&A Prep:** Autogenerates personalized interview questions and bespoke suggested answers based on the intersection of your resume and the specific job description.

## 🛠️ Technology Stack

- **Frontend UI:** Streamlit (with modern custom CSS)
- **AI & LLMs:** Google Generative AI (`gemini-2.5-flash-lite`)
- **Semantic Search:** Sentence Transformers, Scikit-Learn
- **Browser Automation:** Playwright for Python (`playwright`)
- **Document Processing:** PyPDF, PDFKit, ReportLab
- **Data Collection:** BeautifulSoup4, Requests

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed on your system.
- A free Google Gemini API key.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/JobsAI.git
cd JobsAI
```

### 2. Install Dependencies

Install the necessary python packages from the requirements file:

```bash
pip install -r requirements.txt
```

### 3. Setup Browser Automation

For the Auto-Apply feature, Playwright needs to install Chromium:

```bash
playwright install chromium
```

### 4. Configuration

Create a `.env` file in the root of the project to store your API keys safely:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the Application

Start the Streamlit application server:

```bash
streamlit run ui/app.py
```

## 💡 Usage Workflow

1. **Upload:** Start by dragging and dropping your most recent PDF resume into the application.
2. **Analysis:** The internal multi-agent framework (`ResumeParserAgent`, `RoleDetectionAgent`) breaks down your profile.
3. **Discovery:** The application cross-references your profile with live job postings. The `JobScorerAgent` meticulously ranks them based on match likelihood.
4. **Action:** Select a job card:
   - Click **Generate Resume** to receive a newly customized PDF.
   - Use the **Auto-Submit** feature to let the AI launch a browser and handle the heavy lifting of filling out the job's application form.

## 📝 Disclaimer

The Auto-Apply feature utilizes heuristic selectors to navigate highly dynamic web forms and is currently in Beta. Always review the data the agent has inputted into the browser before manually clicking the final submit button.
