import os
import json
import sqlite3
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

st.set_page_config(page_title="Student Employability Intelligence", page_icon="🎓", layout="wide")

DB_PATH = "student_employability.db"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root { --ink:#f8fafc; --muted:#b9c4dc; --panel:#151d35; --line:#34415f; }
html, body, [class*="css"] {font-family:Inter,sans-serif}
.stApp {
  background:
    radial-gradient(ellipse at 8% 8%, rgba(124,58,237,.30), transparent 34%),
    radial-gradient(ellipse at 92% 18%, rgba(14,165,233,.22), transparent 32%),
    radial-gradient(ellipse at 65% 92%, rgba(217,70,239,.16), transparent 35%),
    linear-gradient(135deg,#070b19 0%,#10172d 48%,#11102a 100%);
  color:var(--ink);
}
[data-testid="stHeader"] {background:rgba(7,11,25,.72)}
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#090e20 0%,#17113b 52%,#24104b 100%);
  border-right:1px solid rgba(167,139,250,.24);
}
[data-testid="stSidebar"] * {color:#f8fafc !important}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#c7d2fe !important}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:9px 12px;border-radius:11px}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:rgba(139,92,246,.20)}
.block-container {padding-top:2rem;padding-bottom:3rem;max-width:1450px}
.hero {
  padding:36px 38px;border-radius:26px;color:white;
  background:linear-gradient(115deg,rgba(37,99,235,.96),rgba(109,40,217,.96) 54%,rgba(192,38,211,.92));
  border:1px solid rgba(255,255,255,.22);
  box-shadow:0 18px 55px rgba(76,29,149,.35),inset 0 1px 0 rgba(255,255,255,.18);
  margin-bottom:26px;position:relative;overflow:hidden;
}
.hero:after {content:"";position:absolute;width:260px;height:260px;border:1px solid rgba(255,255,255,.16);border-radius:50%;right:-55px;top:-110px;box-shadow:0 0 0 28px rgba(255,255,255,.035),0 0 0 58px rgba(255,255,255,.025)}
.hero h1 {font-size:36px;font-weight:900;letter-spacing:-1.1px;margin:0;color:white}
.hero p {font-size:16px;margin:10px 0 0;color:#f1eaff;max-width:850px;line-height:1.6}
.section-title {color:#f8fafc;font-size:27px;font-weight:850;letter-spacing:-.5px}
h1,h2,h3,h4 {color:#f8fafc !important;font-weight:800 !important}
p, label, .stMarkdown, [data-testid="stCaptionContainer"] {color:#d4def3}
[data-testid="stMetric"] {background:linear-gradient(145deg,#182440,#111a30);padding:18px 20px;border:1px solid #354565;border-radius:18px;box-shadow:0 10px 28px rgba(0,0,0,.20)}
[data-testid="stMetricLabel"] {color:#b9c8e7 !important}
[data-testid="stMetricValue"] {color:#fff !important;font-weight:850}
.metric-card {background:linear-gradient(145deg,#1b2948,#121a30);padding:20px 21px;border:1px solid #3b4b70;border-radius:19px;box-shadow:0 12px 30px rgba(0,0,0,.24);min-height:125px}
.metric-label {color:#b9c8e7;font-size:13px;font-weight:700;letter-spacing:.3px}
.metric-value {color:#fff;font-size:30px;font-weight:900;margin-top:7px}
.module-card {border-radius:22px;padding:23px 21px;min-height:245px;box-shadow:0 14px 34px rgba(0,0,0,.30),inset 0 1px 0 rgba(255,255,255,.18);transition:transform .2s,filter .2s;position:relative;overflow:hidden}
.module-card:hover {transform:translateY(-5px);filter:brightness(1.12)}
.module-card.github {background:linear-gradient(145deg,#0878ff 0%,#0645b7 62%,#0878d9 100%);border:1px solid #2995ff}
.module-card.skills {background:linear-gradient(145deg,#a21bdf 0%,#6715bb 65%,#8b36ef 100%);border:1px solid #d45aff}
.module-card.interview {background:linear-gradient(145deg,#00bfa5 0%,#007c78 65%,#00a99a 100%);border:1px solid #27e5d0}
.module-card.career {background:linear-gradient(145deg,#ff8a00 0%,#d94b00 65%,#ff7400 100%);border:1px solid #ffb04a}
.module-card h3 {color:#fff;font-size:20px;margin:12px 0 9px;line-height:1.25}
.module-card p {color:#fff;font-size:14px;line-height:1.55;opacity:.94}
.module-icon {width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.18);border:2px solid rgba(255,255,255,.65);font-size:29px;box-shadow:0 0 22px rgba(255,255,255,.24)}
[data-testid="stVerticalBlockBorderWrapper"] {background:rgba(19,29,52,.78);border:1px solid #354565;border-radius:18px}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input {
  background:#101a31 !important;color:#f8fafc !important;border:1px solid #46577d !important;border-radius:11px !important
}
.stSelectbox [data-baseweb="select"] > div,.stMultiSelect [data-baseweb="select"] > div {background:#101a31;color:#fff;border-color:#46577d}
.stCheckbox label,.stRadio label {color:#e2e8f0 !important}
[data-testid="stFileUploader"] {background:rgba(24,36,64,.75);border:1px dashed #7183b2;border-radius:15px;padding:10px}
[data-testid="stFileUploader"] section {background:transparent}
[data-testid="stAlert"] {border-radius:13px}
div.stButton>button,div.stDownloadButton>button {border:1px solid rgba(255,255,255,.18);border-radius:12px;font-weight:800;background:linear-gradient(95deg,#2563eb,#7c3aed 58%,#c026d3);color:white;padding:.62rem 1.1rem;box-shadow:0 7px 20px rgba(91,33,182,.25);transition:transform .18s,filter .18s}
div.stButton>button:hover,div.stDownloadButton>button:hover {color:white;border:1px solid #c4b5fd;filter:brightness(1.13);transform:translateY(-2px)}
.stProgress>div>div>div>div {background:linear-gradient(90deg,#22d3ee,#6366f1,#d946ef)}
[data-testid="stTabs"] button {color:#cbd5e1 !important;font-weight:700}
[data-testid="stTabs"] button[aria-selected="true"] {color:#fff !important;border-bottom:3px solid #a78bfa}
hr {border-color:#34415f}
[data-testid="stDataFrame"] {border:1px solid #34415f;border-radius:12px;overflow:hidden}
</style>
""", unsafe_allow_html=True)

CAREERS = {
    "Data Analyst": {
        "skills":["python","sql","excel","statistics","power bi","data visualization"],
        "project":"Build a data analysis dashboard using a public dataset.",
        "resources":{
            "python":"Practise Python basics, functions and Pandas.",
            "sql":"Practise SELECT, JOIN, GROUP BY and subqueries.",
            "excel":"Learn formulas, lookup functions and pivot tables.",
            "statistics":"Study descriptive statistics and probability.",
            "power bi":"Build an interactive report with filters.",
            "data visualization":"Practise selecting clear charts and explaining insights."
        }},
    "Web Developer":{
        "skills":["html","css","javascript","git","api","responsive design"],
        "project":"Build and publish a responsive personal portfolio website.",
        "resources":{
            "html":"Practise semantic HTML, forms and page structure.",
            "css":"Learn flexbox, grid and responsive layouts.",
            "javascript":"Build interactive features using JavaScript.",
            "git":"Practise commits, branches and pull requests.",
            "api":"Build a small application that consumes a REST API.",
            "responsive design":"Test layouts on mobile, tablet and desktop sizes."
        }},
    "Machine Learning Engineer":{
        "skills":["python","statistics","machine learning","pandas","scikit-learn","model evaluation"],
        "project":"Train and evaluate a machine-learning model on a documented dataset.",
        "resources":{
            "python":"Practise Python programming and data structures.",
            "statistics":"Study probability, distributions and hypothesis testing.",
            "machine learning":"Learn classification, regression and model validation.",
            "pandas":"Practise data cleaning and transformation.",
            "scikit-learn":"Train models using pipelines and cross-validation.",
            "model evaluation":"Understand precision, recall, F1-score and confusion matrices."
        }},
    "Python Developer":{
        "skills":["python","git","api","sql","testing","object-oriented programming"],
        "project":"Create a Python application with tests, documentation and database support.",
        "resources":{
            "python":"Practise functions, collections, modules and exceptions.",
            "git":"Use version control for every project milestone.",
            "api":"Create and consume REST APIs.",
            "sql":"Practise relational database queries.",
            "testing":"Write unit tests and validate edge cases.",
            "object-oriented programming":"Practise classes, inheritance and composition."
        }}
}

QUESTIONS = {
    "Python Developer":[
        "What is the difference between a list and a tuple in Python?",
        "Explain how exception handling works in Python.",
        "What is an API and when would you use one?"],
    "Data Analyst":[
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "How would you handle missing values in a dataset?",
        "When would you use a bar chart instead of a line chart?"],
    "Web Developer":[
        "What is the purpose of semantic HTML?",
        "How does responsive CSS help a website?",
        "What is a REST API?"],
    "Machine Learning Engineer":[
        "What is the difference between classification and regression?",
        "Why do we split data into training and test sets?",
        "What is overfitting and how can it be reduced?"]
}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS assessments(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, student_name TEXT,
        target_role TEXT, github_username TEXT, skill_score INTEGER,
        interview_score INTEGER, recommendations TEXT)""")

def normalize(text):
    return sorted(set(x.strip().lower() for x in text.split(",") if x.strip()))

def metric(label,value,icon,color):
    st.markdown(f"""<div class="metric-card" style="border-top:4px solid {color}">
    <div style="font-size:23px">{icon}</div><div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div></div>""",unsafe_allow_html=True)
    
def fetch_github(username, token=""):

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"

    try:
        profile_response = requests.get(
            f"https://api.github.com/users/{username.strip()}",
            headers=headers,
            timeout=20
        )

        if profile_response.status_code == 404:
            raise ValueError("GitHub username not found.")

        if profile_response.status_code == 403:
            raise ValueError(
                "GitHub API rate limit or access restriction. Try again later."
            )

        profile_response.raise_for_status()

        repos_response = requests.get(
            f"https://api.github.com/users/{username.strip()}/repos",
            params={
                "per_page": 100,
                "sort": "updated"
            },
            headers=headers,
            timeout=20
        )

        if repos_response.status_code == 403:
            raise ValueError("GitHub API rate limit reached.")

        repos_response.raise_for_status()

        return profile_response.json(), repos_response.json()

    except requests.exceptions.Timeout:
        raise ValueError("GitHub request timed out. Try again.")

    except requests.exceptions.ConnectionError:
        raise ValueError("Unable to connect to GitHub. Check your internet.")

    except requests.exceptions.RequestException as e:
        raise ValueError(f"GitHub request failed: {e}")
    
def ai_feedback(question, answer, role):

    try:
        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"].strip()
        )

        prompt = f"""
You are a strict but supportive technical mock interview evaluator.

Target Role: {role}
Interview Question: {question}
Student Answer: {answer}

Evaluate the student's answer carefully.

Give feedback using these headings:

1. Correctness:
   Clearly classify the answer as CORRECT, PARTIALLY CORRECT,
   or INCORRECT.

2. Score:
   Give a fair score out of 10 based on technical accuracy.

3. Correct Points:
   List technically correct points in the answer.

4. Incorrect Points:
   Identify incorrect statements or misunderstandings.
   If none, write "No major incorrect points found."

5. Missing Concepts:
   Mention important points the student did not include.

6. Improved Answer:
   Provide a technically accurate sample answer.

7. Improvement Suggestion:
   Give one practical suggestion.

Important rules:
- Do not give high marks just because the answer is long.
- Do not assume an answer is correct without checking its meaning.
- If the answer is vague or unrelated, give a low score.
- Be fair, specific and educational.
- Do not claim certainty when the answer lacks enough information.
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1200
        )

        return response.choices[0].message.content, None

    except Exception as e:
        return None, f"Groq request failed: {e}"
def rule_feedback(answer):
    n=len(answer.split())
    if n<8: return 2,"The answer is very brief. Add a definition, explanation and practical example."
    if n<25: return 5,"Add more technical detail and a clear example."
    return 7,"The answer has useful detail. Check technical accuracy and organise it into clear points."

def report_data():
    role=st.session_state.role
    skills=set(normalize(st.session_state.skills))
    for c in st.session_state.certificates: skills.update(c["skills"])
    for p in st.session_state.projects: skills.update(p["skills"])
    required=CAREERS[role]["skills"]
    matched=[s for s in required if s in skills]
    missing=[s for s in required if s not in skills]
    return {
        "student":st.session_state.student or "Student",
        "target_role":role,
        "generated_at":datetime.now().strftime("%Y-%m-%d %H:%M"),
        "github_username":st.session_state.github_username,
        "public_repositories":len(st.session_state.repos),
        "skill_match_score":round(100*len(matched)/len(required)),
        "matched_skills":matched,"skills_to_improve":missing,
        "certificates":st.session_state.certificates,
        "portfolio_projects":st.session_state.projects,
        "interview_score":st.session_state.interview_score
    }

init_db()
defaults={
    "student":"","role":"Data Analyst","skills":"","github_username":"",
    "profile":None,"repos":[],"certificates":[],"projects":[],
    "feedback":{},"interview_score":0
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

# Sidebar
with st.sidebar:
    st.markdown("## 🎓 STUDENT AI")
    st.caption("EMPLOYABILITY INTELLIGENCE")
    st.markdown("---")
    st.session_state.student=st.text_input("Student name",st.session_state.student,placeholder="Enter your name")
    roles=list(CAREERS)
    st.session_state.role=st.selectbox("Target career",roles,index=roles.index(st.session_state.role))
    page=st.radio("NAVIGATION",[
        "Dashboard","GitHub Repository Analysis","Skill Gap Analysis",
        "AI-Based Mock Interview","Career Recommendation","Final Assessment Report"])
    st.markdown("---")
    st.caption("Academic project prototype")

if st.sidebar.button("Test Groq API"):
    result, error = test_groq_api()

    if result:
        st.sidebar.success(result)
    else:
        st.sidebar.error(error)

# Skill gap
def get_groq_recommendations(role, matched, missing, score):
    try:
        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"].strip()
        )

        prompt = f"""
        You are a student career guidance assistant.

        Target career: {role}
        Skill match score: {score}%
        Matched skills: {matched}
        Missing skills: {missing}

        Give:
        1. Student skill assessment.
        2. Suggestions to improve missing skills.
        3. A practical project idea.
        4. A 2-week learning plan.

        Use simple and encouraging English.
        """

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq API error: {e}"
        
def test_groq_api():
    try:
        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"].strip()
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": "Reply only: Groq API working"
                }
            ],
            temperature=0.2,
            max_tokens=30
        )

        return response.choices[0].message.content, None

    except Exception as e:
        return None, str(e)


def ai_feedback(question, answer, role):
    try:
        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"].strip()
        )

        prompt = f"""
        You are an experienced technical interviewer.

        Target role: {role}
        Interview question: {question}
        Student answer: {answer}

        Evaluate the answer and provide:
        1. What was explained correctly.
        2. What is missing or needs improvement.
        3. A better way to structure the answer.
        4. One practical suggestion.
        5. An overall score out of 10.

        Be constructive and use simple English.
        """

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1000
        )

        return response.choices[0].message.content, None

    except Exception as e:
        return None, str(e)
        
# Dashboard
if page=="Dashboard":
    st.markdown("""<div class="hero"><h1>Student Employability Intelligence</h1>
    <p>Understand your strengths • Identify skill gaps • Practise interviews • Explore career paths</p></div>""",unsafe_allow_html=True)
    role=st.session_state.role
    skills=set(normalize(st.session_state.skills))
    for c in st.session_state.certificates: skills.update(c["skills"])
    for p in st.session_state.projects: skills.update(p["skills"])
    req=CAREERS[role]["skills"]
    score=round(100*len([x for x in req if x in skills])/len(req))
    cols=st.columns(4)
    with cols[0]: metric("Public repositories",len(st.session_state.repos),"📁","#2563eb")
    with cols[1]: metric("Skill match",f"{score}%","🎯","#8b5cf6")
    with cols[2]: metric("Portfolio projects",len(st.session_state.projects),"🧩","#0d9488")
    with cols[3]: metric("Interview score",f"{st.session_state.interview_score}/10" if st.session_state.interview_score else "Not assessed","🤖","#ea580c")
    st.write("")
    st.markdown('<div class="section-title">Your assessment workspace</div>',unsafe_allow_html=True)
    cards=[
        ("📁","GitHub Repository Analysis","Explore public repositories, programming languages and development activity","github"),
        ("🎯","Skill Gap Analysis","Discover missing skills and add certificates and portfolio projects","skills"),
        ("🤖","AI-Based Mock Interview","Practise role-based questions and receive answer feedback","interview"),
        ("💼","Career Recommendation","Explore career paths that match your current skill profile","career")]
    cc=st.columns(4, gap="medium")
    for i,(icon,title,desc,theme) in enumerate(cards):
        with cc[i]:
            st.markdown(f'<div class="module-card {theme}"><div class="module-icon">{icon}</div><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
    st.info("Begin by completing the modules from the sidebar. Dashboard values update from information entered in this session.")

# GitHub
elif page == "GitHub Repository Analysis":

    st.markdown(
        '<div class="section-title">📁 GitHub Repository Analysis</div>',
        unsafe_allow_html=True
    )

    st.write("Retrieve public GitHub profile and repository metadata.")

    username = st.text_input(
        "GitHub username",
        st.session_state.github_username,
        placeholder="e.g. octocat"
    )

    token = st.text_input(
        "Optional GitHub token",
        type="password",
        help="Do not share your token."
    )

    if st.button("Analyse GitHub Profile", type="primary"):

        if not username.strip():
            st.warning("Enter a GitHub username.")

        else:
            try:
                with st.spinner("Fetching GitHub data..."):
                    profile, repos = fetch_github(
                        username.strip(),
                        token.strip()
                    )

                st.session_state.github_username = username.strip()
                st.session_state.profile = profile
                st.session_state.repos = repos

                st.success("GitHub information retrieved.")

            except Exception as e:
                st.error(f"Unable to retrieve GitHub data: {e}")

    if st.session_state.profile:

        p = st.session_state.profile
        repos = st.session_state.repos

        cols = st.columns(4)

        with cols[0]:
            metric("Public repositories", p.get("public_repos", 0), "📦", "#2563eb")

        with cols[1]:
            metric("Followers", p.get("followers", 0), "👥", "#8b5cf6")

        with cols[2]:
            metric("Following", p.get("following", 0), "🔗", "#0d9488")

        with cols[3]:
            metric("Repositories loaded", len(repos), "📊", "#ea580c")

        st.markdown(
            f"**Profile:** [{p.get('login')}]({p.get('html_url')})"
        )

        st.caption(p.get("bio") or "No public bio supplied.")

        if repos:

            df = pd.DataFrame([
                {
                    "Repository": r.get("name"),
                    "Language": r.get("language") or "Not specified",
                    "Stars": r.get("stargazers_count", 0),
                    "Forks": r.get("forks_count", 0),
                    "Updated": (r.get("updated_at") or "")[:10],
                    "URL": r.get("html_url")
                }
                for r in repos
            ])

            left, right = st.columns([1.2, 1])

            with left:
                st.subheader("Repository details")
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            with right:
                st.subheader("Language distribution")

                langs = pd.Series([
                    r.get("language")
                    for r in repos
                    if r.get("language")
                ]).value_counts()

                if not langs.empty:
                    st.plotly_chart(
                        px.pie(
                            names=langs.index,
                            values=langs.values,
                            hole=.55
                        ),
                        use_container_width=True
                    )
                else:
                    st.info("No primary languages reported.")

        else:
            st.info("No public repositories found.")

        st.divider()
        st.subheader("🤖 AI-Powered GitHub Analysis")

        if st.button("Generate GitHub AI Analysis", type="primary"):

            try:
                with st.spinner("Groq AI is analysing your GitHub profile..."):

                    client = Groq(
                        api_key=st.secrets["GROQ_API_KEY"].strip()
                    )

                    repo_data = []

                    for r in repos[:20]:
                        repo_data.append({
                            "name": r.get("name"),
                            "language": r.get("language") or "Not specified",
                            "stars": r.get("stargazers_count", 0),
                            "forks": r.get("forks_count", 0),
                            "description": r.get("description") or "No description"
                        })

                    prompt = f"""
                    You are a student career guidance assistant.

                    Analyse this public GitHub profile and repository metadata.

                    Username: {p.get("login")}
                    Bio: {p.get("bio") or "Not provided"}
                    Public repositories: {p.get("public_repos", 0)}
                    Followers: {p.get("followers", 0)}

                    Repository information:
                    {repo_data}

                    Give:
                    1. GitHub profile summary.
                    2. Programming language insights.
                    3. Possible technical strengths.
                    4. Areas to improve.
                    5. Three practical project suggestions.
                    6. Suitable career roles to explore.

                    Use simple English.
                    Do not claim to have inspected source code.
                    Do not assume the student personally wrote every repository.
                    """

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                        max_tokens=1200
                    )

                    ai_result = response.choices[0].message.content
                st.session_state.github_ai_analysis = ai_result

                st.success("GitHub AI analysis completed!")
                st.markdown(ai_result)

            except Exception as e:
                st.error(f"Groq API error: {e}")

        st.caption(
            "AI analysis uses public profile and repository metadata only. "
            "It does not inspect source code or verify individual contributions."
        )
        
elif page == "Skill Gap Analysis":
    st.markdown(
        '<div class="section-title">🎯 Skill Gap Analysis</div>',
        unsafe_allow_html=True
    )

    role = st.session_state.role
    st.info(f"Target career: **{role}**")

    st.session_state.skills = st.text_area(
        "Your skills (comma-separated)",
        st.session_state.skills,
        placeholder="Python, SQL, Excel, Pandas, Git",
        height=90
)
    st.write("Groq AI integration is available for personalized skill recommendations.")

    # Certificate details
    with st.expander("🎓 Add certificate details"):
        with st.form("cert_form"):
            cn = st.text_input("Certificate / course name")
            issuer = st.text_input("Issuing organisation")
            cskills = st.text_input("Skills covered (comma-separated)")
            cfile = st.file_uploader(
                "Upload certificate image/PDF (optional)",
                type=["png", "jpg", "jpeg", "pdf"]
            )

            if st.form_submit_button("Add certificate"):
                if cn.strip() and issuer.strip():
                    st.session_state.certificates.append({
                        "name": cn.strip(),
                        "issuer": issuer.strip(),
                        "skills": normalize(cskills),
                        "file": cfile.name if cfile else ""
                    })
                    st.success(
                        "Certificate details recorded. "
                        "Authenticity is not independently verified."
                    )
                else:
                    st.warning("Enter certificate name and issuer.")

    # Portfolio project details
    with st.expander("🧩 Add portfolio project"):
        with st.form("project_form"):
            pn = st.text_input("Project name")
            pdsc = st.text_area("Project description")
            pskills = st.text_input(
                "Technologies / skills used (comma-separated)"
            )
            plink = st.text_input("Project URL (optional)")

            if st.form_submit_button("Add portfolio project"):
                if pn.strip():
                    st.session_state.projects.append({
                        "name": pn.strip(),
                        "description": pdsc.strip(),
                        "skills": normalize(pskills),
                        "url": plink.strip()
                    })
                    st.success("Portfolio project added.")
                else:
                    st.warning("Enter a project name.")

    st.divider()

    if st.button("Calculate Skill Gap", type="primary"):
        allskills = set(normalize(st.session_state.skills))

        for c in st.session_state.certificates:
            allskills.update(c["skills"])

        for p in st.session_state.projects:
            allskills.update(p["skills"])

        required = CAREERS[role]["skills"]

        matched = [s for s in required if s in allskills]
        missing = [s for s in required if s not in allskills]

        score = round(100 * len(matched) / len(required)) if required else 0

        st.session_state.skill_result = {
            "role": role,
            "matched": matched,
            "missing": missing,
            "score": score
        }

    # Display assessment result
    result = st.session_state.get("skill_result")

    if result and result["role"] == role:
        st.subheader("📊 Your Skill Assessment")

        a, b = st.columns(2)

        with a:
            st.metric("Skill Match Score", f"{result['score']}%")
            st.progress(result["score"] / 100)

        with b:
            st.metric("Skills Matched", len(result["matched"]))
            st.metric("Skills to Improve", len(result["missing"]))

        st.success(
            "Matched skills: " +
            (", ".join(result["matched"]) or "None yet")
        )

        st.warning(
            "Skills to improve: " +
            (", ".join(result["missing"]) or "No gaps in this checklist")
        )

        # Personalized recommendations
        st.subheader("💡 Personalized Improvement Recommendations")

        if result["missing"]:
            st.write(
                "Based on your selected career role and the skills you "
                "provided, focus on improving the following areas:"
            )

            for i, skill in enumerate(result["missing"], 1):
                resource = CAREERS[role]["resources"].get(
                    skill,
                    "Practise this skill through a small hands-on project."
                )

                st.markdown(f"**{i}. Improve {skill.title()}**")
                st.write(resource)

        else:
            st.success(
                "All skills in this career checklist are matched. "
                "Continue practising through real-world projects."
            )

        # Suggested project
        st.subheader("🚀 Recommended Practice Project")
        st.write(CAREERS[role]["project"])
        st.divider()

        if st.button("🤖 Generate AI Recommendations"):
            with st.spinner("Groq AI is analysing your skills..."):
                ai_result = get_groq_recommendations(
                    result["role"],
                    result["matched"],
                    result["missing"],
                    result["score"]
                )

            st.subheader("✨ Groq AI Career Guidance")
            st.markdown(ai_result)

        st.caption(
            "The score is based on a checklist comparison of supplied "
            "skills and evidence tags. It is not a validated professional "
            "competency score."
        )

    # Certificate records
    if st.session_state.certificates:
        st.divider()
        st.subheader("🎓 Certificate Records")

        st.dataframe(
            pd.DataFrame(st.session_state.certificates),
            use_container_width=True,
            hide_index=True
        )

    # Portfolio records
    if st.session_state.projects:
        st.divider()
        st.subheader("🧩 Portfolio Projects")

        for p in st.session_state.projects:
            with st.container(border=True):
                st.markdown(f"**{p['name']}**")
                st.write(p["description"] or "No description.")

                st.caption(
                    "Skills: " +
                    (", ".join(p["skills"]) or "Not specified")
                )

                if p["url"]:
                    st.markdown(f"[Open project]({p['url']})")
# Mock interview
elif page == "AI-Based Mock Interview":

    st.markdown(
        '<div class="section-title">🤖 AI-Based Mock Interview</div>',
        unsafe_allow_html=True
    )

    role = st.session_state.role
    questions = QUESTIONS[role]

    qi = st.selectbox(
        "Choose an interview question",
        range(len(questions)),
        format_func=lambda i: f"Question {i+1}: {questions[i]}"
    )

    question = questions[qi]

    st.markdown(
        f'<div class="module-card"><div class="metric-label">INTERVIEW QUESTION</div><h3>{question}</h3><p>Target role: {role}</p></div>',
        unsafe_allow_html=True
    )

    answer = st.text_area(
        "Your answer",
        height=160,
        placeholder="Explain the concept and include an example..."
    )

    use_ai = st.checkbox(
        "Use Groq AI feedback (requires API key)",
        value=True
    )

    if st.button("Submit answer for feedback", type="primary"):

        if len(answer.strip()) < 5:
            st.warning("Please enter an answer.")

        elif use_ai:

            with st.spinner("Generating Groq AI feedback..."):
                feedback, error = ai_feedback(question, answer, role)

            if feedback:
                st.session_state.feedback[f"{role}_{qi}"] = feedback
                st.session_state.interview_score = 0
                st.success("Groq AI feedback generated.")

            else:
                score, note = rule_feedback(answer)

                st.session_state.feedback[f"{role}_{qi}"] = (
                    f"Rule-based practice feedback (not AI): "
                    f"{score}/10. {note}\n\nGroq unavailable: {error}"
                )

                st.session_state.interview_score = score

                st.warning(
                    "Groq unavailable. Displaying clearly labelled "
                    "basic rule-based feedback."
                )

        else:
            score, note = rule_feedback(answer)

            st.session_state.feedback[f"{role}_{qi}"] = (
                f"Rule-based practice feedback (not AI): {score}/10. {note}"
            )

            st.session_state.interview_score = score

    fb = st.session_state.feedback.get(f"{role}_{qi}")

    if fb:
        st.subheader("Feedback")
        st.markdown(fb)

    st.caption(
        "Feedback is for practice only. Rule-based fallback checks "
        "answer length and structure, not technical correctness."
    )

elif page == "Career Recommendation":

    st.markdown(
        '<div class="section-title">🚀 Career Recommendation</div>',
        unsafe_allow_html=True
    )

    st.write("Discover suitable career paths using your skills.")

    skills = st.text_input(
        "Enter your skills (comma-separated)",
        placeholder="Python, SQL, Excel, Machine Learning"
    )

    interests = st.text_area(
        "What are your career interests?",
        placeholder="I am interested in data analysis and AI..."
    )

    if st.button("Generate Career Recommendations", type="primary"):

        if not skills.strip():
            st.warning("Please enter your skills.")

        else:
            try:
                client = Groq(
                    api_key=st.secrets["GROQ_API_KEY"].strip()
                )

                prompt = f"""
                You are an expert student career guidance assistant.

                Student skills: {skills}
                Student interests: {interests}

                Provide:
                1. Three suitable career roles.
                2. Why each role matches the student's skills.
                3. Skills required for each role.
                4. Skills the student should improve.
                5. A practical project for each role.
                6. A 30-day learning roadmap.

                Use simple English and clear headings.
                """

                with st.spinner("Groq AI is finding suitable careers..."):

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                        max_tokens=1200
                    )

                st.success("Career recommendations generated!")

                career_text = response.choices[0].message.content
                st.session_state.career_recommendation = career_text
                st.markdown(career_text)

            except Exception as e:
                st.error(f"Groq API error: {e}")

    st.caption(
        "Career suggestions are AI-generated guidance, "
        "not guaranteed job or placement predictions."
    )

elif page == "Final Assessment Report":

    st.markdown(
        '<div class="section-title">📄 Final Assessment Report</div>',
        unsafe_allow_html=True
    )

    st.write("Student Employability Assessment Report")

    student = st.session_state.get("student", "Student")
    role = st.session_state.get("role", "Not selected")
    result = st.session_state.get("skill_result")
    profile = st.session_state.get("profile")
    repos = st.session_state.get("repos", [])
    feedback = st.session_state.get("feedback", {})
    career = st.session_state.get("career_recommendation", "")
    github_analysis = st.session_state.get("github_ai_analysis", "")

    st.subheader("Student Details")
    st.write("Student:", student)
    st.write("Target Career:", role)

    st.subheader("GitHub Analysis")

    if profile:
        st.write("GitHub Username:", profile.get("login"))
        st.write("Public Repositories:", profile.get("public_repos"))
        st.write("Followers:", profile.get("followers"))
        st.write("Following:", profile.get("following"))

        st.markdown("### Repository Programming Languages")

        language_data = {}

        for repo in repos:
            language = repo.get("language")
            if language:
                language_data[language] = language_data.get(language, 0) + 1

        if language_data:
            chart_df = pd.DataFrame({
                "Language": list(language_data.keys()),
                "Repositories": list(language_data.values())
            })

            st.plotly_chart(
                px.pie(
                    chart_df,
                    names="Language",
                    values="Repositories",
                    hole=0.55,
                    title="Programming Language Distribution"
                ),
                use_container_width=True
            )
        else:
            st.info("No programming language data available.")

        st.markdown("### Recent Repositories")

        for repo in sorted(
            repos,
            key=lambda x: x.get("updated_at") or "",
            reverse=True
        )[:5]:
            st.write(
                repo.get("name"),
                "-",
                repo.get("updated_at", "Date unavailable")
            )

        st.markdown("### GitHub AI Analysis")

        if github_analysis:
            st.markdown(github_analysis)
        else:
            st.info("GitHub AI analysis not available.")

    else:
        st.info("GitHub analysis not completed.")

    st.subheader("Skill Gap Analysis")

    if result:
        st.metric("Skill Match Score", f"{result['score']}%")
        st.write("Matched Skills:", result["matched"])
        st.write("Missing Skills:", result["missing"])
    else:
        st.info("Skill Gap Analysis not completed.")

    st.subheader("Mock Interview")

    if feedback:
        for question, answer in feedback.items():
            st.write(question)
            st.write(answer)
    else:
        st.info("Mock Interview not completed.")

    st.subheader("Career Recommendation")

    if career:
        st.markdown(career)
    else:
        st.info("Career Recommendation not completed.")

    # PDF report creation
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    def add_pdf_line(text):
        nonlocal_y = y - 20
        return nonlocal_y

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Student Employability Assessment Report")
    y -= 35

    pdf.setFont("Helvetica", 10)

    pdf_lines = [
        "Student: " + str(student),
        "Target Career: " + str(role),
        "",
        "GITHUB ANALYSIS"
    ]

    if profile:
        pdf_lines.extend([
            "Username: " + str(profile.get("login")),
            "Public Repositories: " + str(profile.get("public_repos")),
            "Followers: " + str(profile.get("followers")),
            "Following: " + str(profile.get("following"))
        ])

    pdf_lines.append("")
    pdf_lines.append("SKILL GAP ANALYSIS")

    if result:
        pdf_lines.extend([
            "Skill Match Score: " + str(result.get("score")) + "%",
            "Matched Skills: " + str(result.get("matched")),
            "Missing Skills: " + str(result.get("missing"))
        ])

    pdf_lines.append("")
    pdf_lines.append("GITHUB AI ANALYSIS")
    if github_analysis:
        pdf_lines.extend(github_analysis.splitlines())

    pdf_lines.append("")
    pdf_lines.append("MOCK INTERVIEW")

    for question, answer in feedback.items():
        pdf_lines.append("Question: " + str(question))
        pdf_lines.append("Feedback: " + str(answer))
        pdf_lines.append("")

    pdf_lines.append("CAREER RECOMMENDATION")
    if career:
        pdf_lines.extend(career.splitlines())

    for line in pdf_lines:
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        pdf.drawString(50, y, str(line).encode("ascii", "replace").decode("ascii")[:100])
        y -= 16

    pdf.save()
    pdf_buffer.seek(0)

    st.download_button(
        label="Download Assessment Report PDF",
        data=pdf_buffer.getvalue(),
        file_name="Student_Assessment_Report.pdf",
        mime="application/pdf",
        type="primary"
    )

    st.success("Assessment summary displayed successfully!")