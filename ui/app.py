import streamlit as st
import os
import sys

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.pdf_service import PDFService
from agents.resume_parser_agent import ResumeParserAgent
from agents.role_detection_agent import RoleDetectionAgent
from agents.job_discovery_agent import JobDiscoveryAgent
from agents.job_scorer_agent import JobScorerAgent
from agents.resume_tailor_agent import ResumeTailorAgent
from agents.application_agent import ApplicationAgent
from agents.interview_agent import InterviewAgent
from agents.auto_apply_agent import AutoApplyAgent
from agents.skill_gap_agent import SkillGapAgent

st.set_page_config(
    page_title="JobsAI - Intelligent Job Application Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* ---------- Base ---------- */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #ffffff !important;
  }

  /* Remove default Streamlit padding/margin on the top */
  .block-container {
    padding-top: 2rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1200px;
  }

  /* ---------- Navbar / Header ---------- */
  .app-header {
    background: linear-gradient(135deg, #1A56DB 0%, #0E3A8C 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 24px rgba(26,86,219,0.18);
  }
  .app-header-icon {
    font-size: 2.4rem;
    line-height: 1;
  }
  .app-header-text h1 {
    color: #ffffff;
    font-size: 1.85rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .app-header-text p {
    color: rgba(255,255,255,0.72);
    font-size: 0.9rem;
    margin: 4px 0 0;
  }

  /* ---------- Section heading ---------- */
  .section-heading {
    color: #1A56DB;
    font-size: 1.1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-left: 4px solid #1A56DB;
    padding-left: 12px;
    margin: 28px 0 16px;
  }

  /* ---------- Upload card ---------- */
  .upload-card {
    background: #ffffff;
    border: 2px dashed #A3BFFA;
    border-radius: 16px;
    padding: 36px;
    text-align: center;
    margin-bottom: 24px;
    transition: border-color 0.2s;
  }
  .upload-card:hover { border-color: #1A56DB; }

  /* ---------- Info / stat pill ---------- */
  .stat-pill {
    display: inline-block;
    background: #EBF2FF;
    color: #1A56DB;
    border-radius: 99px;
    padding: 4px 16px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 4px 4px 0 0;
  }

  /* ---------- Job card ---------- */
  .job-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 16px;
    border-left: 5px solid #1A56DB;
    box-shadow: 0 2px 12px rgba(26,86,219,0.07);
    transition: box-shadow 0.2s, transform 0.15s;
  }
  .job-card:hover {
    box-shadow: 0 6px 24px rgba(26,86,219,0.13);
    transform: translateY(-2px);
  }
  .job-card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 4px;
  }
  .job-card-meta {
    font-size: 0.85rem;
    color: #6B7280;
    margin: 0 0 12px;
  }
  .job-card-score-badge {
    background: linear-gradient(90deg, #1A56DB, #0E3A8C);
    color: white;
    font-size: 0.78rem;
    font-weight: 600;
    border-radius: 8px;
    padding: 3px 12px;
    display: inline-block;
    margin-bottom: 14px;
  }

  /* ---------- Role badge ---------- */
  .role-badge {
    display: inline-block;
    background: #EBF2FF;
    color: #1A56DB;
    border: 1px solid #A3BFFA;
    border-radius: 8px;
    padding: 5px 14px;
    font-size: 0.85rem;
    font-weight: 500;
    margin: 4px 4px 0 0;
  }

  /* ---------- Steps / pipeline strip ---------- */
  .pipeline-steps {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }
  .pipeline-step {
    background: #ffffff;
    border: 1px solid #BFDBFE;
    border-radius: 99px;
    padding: 6px 16px;
    font-size: 0.8rem;
    color: #374151;
    font-weight: 500;
  }
  .pipeline-step.done {
    background: #1A56DB;
    border-color: #1A56DB;
    color: #ffffff;
  }
  .pipeline-arrow { color: #9CA3AF; font-size: 0.85rem; }

  /* ---------- Q&A item ---------- */
  .qa-item {
    background: #F8FAFF;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 3px solid #1A56DB;
  }
  .qa-item .q { font-weight: 600; color: #111827; margin-bottom: 6px; font-size: 0.92rem; }
  .qa-item .a { color: #374151; font-size: 0.88rem; line-height: 1.55; }

  /* ---------- Auto-apply section ---------- */
  .auto-apply-box {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 12px;
    padding: 20px 24px;
    margin-top: 16px;
  }
  .auto-apply-box h4 { color: #1A56DB; font-size: 0.95rem; margin: 0 0 6px; }
  .auto-apply-box p  { color: #6B7280; font-size: 0.83rem; margin: 0; }

  /* ---------- Skill Gap Section ---------- */
  .gap-card {
    background: #FFF7ED;
    border: 1px solid #FFEDD5;
    border-radius: 12px;
    padding: 20px;
    margin-top: 12px;
  }
  .gap-title {
    color: #C2410C;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 4px;
  }
  .gap-suggestion {
    color: #431407;
    font-size: 0.88rem;
    line-height: 1.5;
    margin-bottom: 12px;
  }
  .course-pill {
    display: inline-block;
    background: #ffffff;
    border: 1px solid #FED7AA;
    color: #C2410C;
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 0.82rem;
    font-weight: 600;
    text-decoration: none;
    margin-right: 8px;
    margin-bottom: 8px;
    transition: all 0.2s;
  }
  .course-pill:hover {
    background: #C2410C;
    color: #ffffff;
    border-color: #C2410C;
  }

  /* ---------- Streamlit widget overrides ---------- */
  div[data-testid="stFileUploader"] {
    border: none !important;
    background: transparent !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, #1A56DB, #0E3A8C) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    padding: 0.45rem 1.2rem !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.88 !important; }

  .stDownloadButton > button {
    background: #EBF2FF !important;
    color: #1A56DB !important;
    border: 1px solid #A3BFFA !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
  }

  div[data-testid="stSuccess"] {
    background: #ECFDF5;
    border-left: 4px solid #10B981;
    border-radius: 10px;
    color: #065F46;
  }
  div[data-testid="stInfo"] {
    background: #EBF2FF;
    border-left: 4px solid #1A56DB;
    border-radius: 10px;
    color: #1E3A8A;
  }
  div[data-testid="stWarning"] {
    background: #FFFBEB;
    border-left: 4px solid #F59E0B;
    border-radius: 10px;
  }

  div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #1A56DB, #60A5FA) !important;
    border-radius: 99px !important;
  }

  /* Expander */
  details summary {
    color: #1A56DB !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
  }

  /* Hide Streamlit default branding */
  #MainMenu, footer { visibility: hidden; }
  header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# ── App Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-header-icon">💼</div>
  <div class="app-header-text">
    <h1>JobsAI</h1>
    <p>Intelligent resume analysis, job matching, and automated application submission</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Upload Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">Step 1 — Upload Your Resume</div>', unsafe_allow_html=True)

col_upload, col_tip = st.columns([2, 1])
with col_upload:
    uploaded_file = st.file_uploader("Select a PDF resume file", type="pdf", label_visibility="collapsed")

with col_tip:
    st.info("**Tip:** Upload your latest resume in PDF format. The AI will extract your skills, experience, and preferred roles automatically.")

# ── Main Flow ──────────────────────────────────────────────────────────────────
if uploaded_file:

    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    # Pipeline progress indicator
    st.markdown("""
    <div class="pipeline-steps">
      <span class="pipeline-step done">Resume Parsed</span>
      <span class="pipeline-arrow">›</span>
      <span class="pipeline-step done">Skills Extracted</span>
      <span class="pipeline-arrow">›</span>
      <span class="pipeline-step done">Jobs Scored</span>
      <span class="pipeline-arrow">›</span>
      <span class="pipeline-step">Application</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Reading and analyzing your resume..."):
        resume_text = PDFService.extract_text_from_pdf(file_path)
        parsed_resume = ResumeParserAgent.parse_resume(resume_text)
        
        if isinstance(parsed_resume, dict) and "error" in parsed_resume:
            st.error(f"⚠️ {parsed_resume['error']}")
            st.info("The Gemini API free tier has a daily limit (20 requests). Please try again later or use a different API key in your .env file.")
            st.stop()

    st.success("Resume analyzed successfully.")

    # ── Extract Skills / Keywords from Resume ─────────────────────────────
    st.markdown('<div class="section-heading">Step 2 — Skills & Keywords Detected</div>', unsafe_allow_html=True)

    resume_keywords_str = RoleDetectionAgent.detect_role(parsed_resume)
    resume_keywords = [k.strip() for k in resume_keywords_str.split(",") if k.strip()]

    skills_html = " ".join([f'<span class="role-badge">{k}</span>' for k in resume_keywords])
    st.markdown(f'<div style="margin-bottom:8px">{skills_html}</div>', unsafe_allow_html=True)
    st.caption(f"{len(resume_keywords)} keywords extracted from your resume — these are used to match and rank jobs.")

    # ── Job Discovery ─────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">Step 3 — Job Matches</div>', unsafe_allow_html=True)

    with st.spinner("Searching and ranking live job listings against your resume..."):
        raw_jobs = JobDiscoveryAgent.fetch_jobs(resume_keywords)
        # Refine scoring with semantic similarity
        scored_jobs = JobScorerAgent.score_jobs(parsed_resume, raw_jobs)

    if not scored_jobs:
        st.warning("No matching positions found right now. Try again or update your resume with more specific skills.")
    else:
        st.markdown(f'<span class="stat-pill">{len(scored_jobs)} positions evaluated</span>'
                    f'<span class="stat-pill">Showing top 10 matches</span>', unsafe_allow_html=True)
        st.write("")

        for idx, job in enumerate(scored_jobs[:10]):

            score_val = int(job.get("score", 0))

            st.markdown(f"""
            <div class="job-card">
              <div class="job-card-title">{job["title"]}</div>
              <div class="job-card-meta">{job["company"]} &nbsp;·&nbsp; {job["location"]}</div>
              <div class="job-card-score-badge">Match Score: {score_val}%</div>
            </div>
            """, unsafe_allow_html=True)

            # Skill Gap Analysis for low scores
            if score_val < 50:
                with st.expander("💡 Unlock this role — Skill Gap Analysis & Learning Path", expanded=False):
                    with st.spinner("Analyzing missing skills..."):
                        gaps = SkillGapAgent.analyze_gap(parsed_resume, job["description"])
                        if not gaps:
                            st.info("No major gaps detected, however the semantic match is low. Try emphasizing your technical background more.")
                        else:
                            st.write("To become a top candidate for this role, consider focusing on these areas:")
                            for gap in gaps:
                                links_html = "".join([f'<a href="{l["url"]}" target="_blank" class="course-pill">{l["title"]}</a>' for l in gap.get("links", [])])
                                st.markdown(f"""
                                <div class="gap-card">
                                  <div class="gap-title">🎯 {gap['skill']}</div>
                                  <div class="gap-suggestion">{gap['suggestion']}</div>
                                  <div>{links_html}</div>
                                </div>
                                """, unsafe_allow_html=True)

            btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 4])

            with btn_col1:
                if job.get("url"):
                    st.link_button("Apply", job["url"], use_container_width=True)

            with btn_col2:
                apply_clicked = st.button("Generate Resume", key=f"apply_{idx}", use_container_width=True)

            if apply_clicked:
                with st.spinner(f"Tailoring your resume for {job['title']}..."):
                    tailored_resume = ResumeTailorAgent.tailor_resume(parsed_resume, job["description"])
                    output_pdf = ApplicationAgent.apply(job, tailored_resume)

                st.success("Tailored application package ready.")

                with open(output_pdf, "rb") as file:
                    st.download_button(
                        label="Download Tailored Resume (PDF)",
                        data=file,
                        file_name=os.path.basename(output_pdf),
                        mime="application/pdf",
                        key=f"dl_{idx}"
                    )

                # Interview Q&A
                with st.spinner("Generating application Q&A guidance..."):
                    try:
                        guidance = InterviewAgent.generate_guidance(tailored_resume, job["description"])
                        with st.expander("Application Q&A — Suggested Responses", expanded=False):
                            st.markdown("These responses are tailored to your profile and the job description:")
                            st.write("")
                            for qa in guidance:
                                st.markdown(f"""
                                <div class="qa-item">
                                  <div class="q">Q: {qa['question']}</div>
                                  <div class="a">{qa['answer']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Could not generate Q&A guidance: {str(e)}")

                # Auto-apply
                if job.get("url"):
                    st.markdown(f"""
                    <div class="auto-apply-box">
                      <h4>Automated Submission (Beta)</h4>
                      <p>This will launch a browser and attempt to fill out the application form automatically using your tailored resume and profile.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    if st.button(f"Auto-Submit Application to {job['company']}", key=f"auto_{idx}"):
                        with st.spinner("Launching automated submission..."):
                            success, msg, img_path = AutoApplyAgent.attempt_apply(job["url"], tailored_resume, output_pdf)

                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

                        try:
                            st.image(img_path, caption="Browser state at completion")
                        except:
                            pass