import streamlit as st
import PyPDF2
import io
import language_tool_python

# Predefined job role requirements (expand this list)
JOB_REQUIREMENTS = {
    "data scientist": ["Python", "SQL", "Machine Learning", "Pandas", "Statistics"],
    "web developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "cloud engineer": ["AWS", "Docker", "Terraform", "Linux", "Networking"]
}

# Free learning resources (no API needed)
RESOURCE_LINKS = {
    "Python": "https://www.learnpython.org",
    "SQL": "https://www.w3schools.com/sql",
    "Machine Learning": "https://www.coursera.org/learn/machine-learning",
    # Add more resources as needed
}

def extract_text(file):
    """Extract text from PDF or TXT files"""
    if file.type == "application/pdf":
        pdf = PyPDF2.PdfReader(io.BytesIO(file.read()))
        return " ".join([page.extract_text() for page in pdf.pages])
    return file.read().decode("utf-8")

def check_grammar(text):
    """Check grammar using LanguageTool"""
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    return [f"{m.ruleId}: {m.message}" for m in matches[:5]]  # Return top 5 errors

def get_missing_skills(resume_text, job_role):
    """Compare resume with job requirements"""
    job_skills = JOB_REQUIREMENTS.get(job_role.lower(), [])
    resume_skills = [skill for skill in job_skills if skill.lower() in resume_text.lower()]
    return list(set(job_skills) - set(resume_skills))

# Streamlit UI
st.title("Simple Resume Checker")
st.write("Upload your resume for basic analysis")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
job_role = st.text_input("Job Role (optional)")

if uploaded_file and st.button("Analyze"):
    text = extract_text(uploaded_file)
    
    if not text.strip():
        st.error("Empty file content")
        st.stop()

    # Grammar check
    st.subheader("Grammar Suggestions")
    grammar_errors = check_grammar(text)
    if grammar_errors:
        for error in grammar_errors:
            st.error(error)
    else:
        st.success("No major grammar issues found")

    # Job-specific analysis
    if job_role:
        st.subheader(f"Job Requirements Check ({job_role})")
        missing_skills = get_missing_skills(text, job_role)
        
        if missing_skills:
            st.write("Missing skills/tools:")
            for skill in missing_skills:
                resource = RESOURCE_LINKS.get(skill, f"https://www.google.com/search?q=learn+{skill}")
                st.markdown(f"- [{skill}]({resource})")
        else:
            st.success("All recommended skills present!")
