import os
import streamlit as st
from pypdf import PdfReader
from pydantic import BaseModel, Field
import ollama

# ---------------------------------------------------------------------------
# 1. STRUCTURAL DATA CONTRACTS (Pydantic Models)
# ---------------------------------------------------------------------------
# Part 1 Schema: For extracting and isolating topic questions
class RawQuestion(BaseModel):
    question_number: str = Field(description="e.g., Q1, Q2a")
    question_text: str = Field(description="The full text and tables of the question")
    raw_answer: str = Field(description="The matching raw baseline answer details")

class TopicExtractionResult(BaseModel):
    topic_name: str
    questions: list[RawQuestion] = []

# Part 2 Schema: For converting raw questions into strict points rubrics
class RubricPoint(BaseModel):
    point_value: int = Field(default=1)
    criteria: str = Field(description="Specific rule to earn this 1 mark")

class QuestionRubric(BaseModel):
    question_number: str
    max_marks: int
    points_breakdown: list[RubricPoint]

class ExamRubricSchema(BaseModel):
    topic_name: str
    rubrics: list[QuestionRubric] = []

# Part 3 Schema: For evaluating the final student output score
class PointEvaluation(BaseModel):
    criteria: str
    earned: bool = Field(description="True if the student achieved this specific point criteria")
    reason: str = Field(description="Short reason why the point was awarded or deducted")

class GradingReport(BaseModel):
    score_awarded: int
    max_marks: int
    points_feedback: list[PointEvaluation]
    overall_advice: str


# ---------------------------------------------------------------------------
# 2. APP CONFIGURATION & STATE INITIALIZATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Local Exam Master AI", layout="wide")
st.title("📚 Local Exam Topic Processor & Grader")
st.caption("Powered entirely locally by Ollama (gemma2:2b) | Python 3.14")

# Set up storage memory keys if they don't exist yet
if "extracted_bank" not in st.session_state:
    st.session_state.extracted_bank = None  # Stores Part 1 Data
if "generated_rubric" not in st.session_state:
    st.session_state.generated_rubric = None  # Stores Part 2 Data


# ---------------------------------------------------------------------------
# 🛠️ PART 1 UI: PDF INGESTION & FILTERING
# ---------------------------------------------------------------------------
st.header("🧩 Part 1: Topic Extraction Bank")
c1, c2 = st.columns([2, 1])

with c2:
    st.subheader("Control Center")
    pdf_file = st.file_uploader("Upload Past Year Exam PDF", type=["pdf"])
    target_topic = st.text_input("Enter Topic of Interest:", placeholder="e.g., Matrices")
    
    if st.button("Extract Questions 🚀", use_container_width=True):
        if not pdf_file or not target_topic:
            st.warning("Please provide both an Exam PDF and a Target Topic!")
        else:
            with st.spinner("Reading PDF and filtering text via gemma2:2b..."):
                # Data component: Parse raw PDF bytes into a text string
                reader = PdfReader(pdf_file)
                raw_text = ""
                for page in reader.pages:
                    text_layer = page.extract_text()
                    if text_layer:
                        raw_text += text_layer + "\n"
                
                # AI component: Query Ollama for structured extraction
                prompt = f"Target Topic: {target_topic}\nExam Text Material:\n{raw_text}"
                try:
                    response = ollama.chat(
                        model='gemma2:2b',
                        messages=[
                            {'role': 'system', 'content': 'You are an examiner data compiler. Extract ONLY questions and corresponding answer guidelines that match the target topic. Convert data tables to Markdown.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        format=TopicExtractionResult.model_json_schema()
                    )
                    # Save verified data to memory state
                    st.session_state.extracted_bank = TopicExtractionResult.model_validate_json(response.message.content)
                    st.success("Extraction Completed!")
                except Exception as e:
                    st.error(f"Local model error during Part 1: {e}")

with c1:
    st.subheader("Output Display: Isolated Questions")
    if st.session_state.extracted_bank:
        st.markdown(f"### Target Topic: `{st.session_state.extracted_bank.topic_name}`")
        for q in st.session_state.extracted_bank.questions:
            with st.expander(f"📝 {q.question_number}", expanded=True):
                st.markdown("**Question Text:**")
                st.write(q.question_text)
                st.markdown("**Raw Extracted Answer Guideline:**")
                st.info(q.raw_answer)
    else:
        st.info("Upload a file and click extract to populate the Question Bank output area.")

st.divider()

# ------------------------------------------------------------
# 🛠️ PART 2 UI: AUTOMATED RUBRIC BUILDER
# ------------------------------------------------------------
st.header("📋 Part 2: Granular Marking Rubric Generator")
c3, c4 = st.columns([1, 2])

with c3:
    st.subheader("Engine Control")
    if not st.session_state.extracted_bank:
        st.write("⚠️ *Waiting for Part 1 output bank to be populated...*")
    else:
        if st.button("Generate Rubric Schemes ⚙️", use_container_width=True):
            with st.spinner("AI parsing raw guides into strict numeric step metrics..."):
                # Convert our current cached extraction data into a serializable string payload
                bank_payload = st.session_state.extracted_bank.model_dump_json()
                
                try:
                    response = ollama.chat(
                        model='gemma2:2b',
                        messages=[
                            {'role': 'system', 'content': 'Convert the provided questions and raw answers into granular, logical step-by-step point-by-point scoring guidelines matching standard national grading structures.'},
                            {'role': 'user', 'content': bank_payload}
                        ],
                        format=ExamRubricSchema.model_json_schema()
                    )
                    st.session_state.generated_rubric = ExamRubricSchema.model_validate_json(response.message.content)
                    st.success("Rubric Mapping Complete!")
                except Exception as e:
                    st.error(f"Local model error during Part 2: {e}")

with c4:
    st.subheader("Output Display: Structured Schema")
    if st.session_state.generated_rubric:
        for r in st.session_state.generated_rubric.rubrics:
            st.markdown(f"#### Rubric Matrix for `{r.question_number}` (Max: {r.max_marks} Marks)")
            for pt in r.points_breakdown:
                st.markdown(f"- `[{pt.point_value} Mark]` {pt.criteria}")
            st.write("")
    else:
        st.info("Click generate to transform raw guidelines into structured numerical scoring rules.")

st.divider()

# ------------------------------------------------------------
# 🛠️ PART 3 UI: LIVE STUDENT EVALUATION INPUT LOOP
# ------------------------------------------------------------
st.header("📝 Part 3: Interactive Student Testing Workspace")

if not st.session_state.generated_rubric:
    st.info("Ensure Part 1 and Part 2 are completed to unlock the student check interface workspace.")
else:
    # 1. Let user choose which extracted question they want to practice trying
    q_options = [r.question_number for r in st.session_state.generated_rubric.rubrics]
    selected_q_num = st.selectbox("Select a question to practice:", q_options)
    
    # Locate the target structural specs from our cache records
    matched_q = next(q for q in st.session_state.extracted_bank.questions if q.question_number == selected_q_num)
    matched_rubric = next(r for r in st.session_state.generated_rubric.rubrics if r.question_number == selected_q_num)
    
    col_entry, col_report = st.columns(2)
    
    with col_entry:
        st.markdown("**Your Assignment Question:**")
        st.code(matched_q.question_text, language="text")
        
        # Student user typing input buffer field
        student_attempt = st.text_area("Type your working steps or short essay response here:", height=150, placeholder="Paste your answers here...")
        
        if st.button("Evaluate My Answer 🎯", use_container_width=True):
            if not student_attempt:
                st.warning("Please type your attempt text before running evaluation metrics.")
            else:
                with st.spinner("Strict Local Examiner is reviewing your text logs..."):
                    # Assemble evaluation bundle package payload
                    eval_bundle = {
                        "question": matched_q.question_text,
                        "rubric_rules": matched_rubric.model_dump(),
                        "student_submission": student_attempt
                    }
                    
                    try:
                        response = ollama.chat(
                            model='gemma2:2b',
                            messages=[
                                {'role': 'system', 'content': 'You are a strict, objective academic examiner. Evaluate the student submission ONLY against the criteria list lines provided. Compute total marks earned mathematically based on checks.'},
                                {'role': 'user', 'content': str(eval_bundle)}
                            ],
                            format=GradingReport.model_json_schema()
                        )
                        
                        # Store temporary local calculation run variables straight into the report layout view
                        report = GradingReport.model_validate_json(response.message.content)
                        
                        with col_report:
                            st.subheader("Your Grading Assessment Report")
                            st.metric(label="Calculated Marks Score", value=f"{report.score_awarded} / {report.max_marks}")
                            
                            st.markdown("**Line-by-Line Item Audit Checks:**")
                            for audit in report.points_feedback:
                                check_icon = "✅ [EARNED]" if audit.earned else "❌ [MISSED]"
                                st.markdown(f"**{check_icon}** *{audit.criteria}*")
                                st.caption(f"↳ Reason: {audit.reason}")
                                
                            st.markdown("**AI Tutor Improvement Recommendation Summary:**")
                            st.info(report.overall_advice)
                            
                    except Exception as e:
                        st.error(f"Local model error during Part 3: {e}")
                        