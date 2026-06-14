import streamlit as st
import google.generativeai as genai
import json
import re

# Page config
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="✦",
    layout="centered",
)

#Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 780px; }

/* Hero */
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6c63ff, #00d4aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.hero-sub {
    color: #8892a4;
    font-size: 1rem;
    margin-bottom: 2rem;
}
.badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    color: #00d4aa;
    border: 1px solid #00d4aa;
    padding: 3px 12px;
    border-radius: 99px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* Cards / result boxes */
.result-box {
    background: #1e2330;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 1rem;
    font-size: 0.93rem;
    line-height: 1.8;
    color: #f0f2f8;
    white-space: pre-wrap;
}
.result-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #00d4aa;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* Flashcards */
.fc-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 1rem;
}
.fc-card {
    background: #1e2330;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
}
.fc-q { font-weight: 600; font-size: 0.88rem; color: #f0f2f8; margin-bottom: 0.6rem; }
.fc-a { font-size: 0.83rem; color: #00d4aa; padding-top: 0.6rem; border-top: 1px solid rgba(255,255,255,0.07); }

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


#Helper: call Gemini
def call_gemini(prompt: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text


#Header 
st.markdown('<div class="hero-title">✦ AI Study Buddy</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Explain topics · Summarize notes · Generate quizzes — all with Gemini AI</div>', unsafe_allow_html=True)

#API Key
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

API_KEY = st.secrets["GEMINI_API_KEY"]


#Tabs
tab1, tab2, tab3 = st.tabs(["💡 Explain Topic", "📝 Summarize Notes", "🧠 Quiz / Flashcards"])


# TAB1  EXPLAIN
with tab1:
    st.subheader("Explain any topic in simple terms")
    st.caption("Get a clear, easy-to-understand explanation of any concept.")

    topic = st.text_area(
        "Topic",
        placeholder="e.g. How does photosynthesis work? / What is recursion in programming?",
        height=110,
        label_visibility="collapsed",
    )
    level = st.selectbox(
        "Difficulty level",
        ["🟢 Beginner (simple)", "🟡 Intermediate", "🔴 Advanced / detailed"],
    )

    if st.button("Explain this ✦", type="primary", key="explain_btn"):
        if not API_KEY:
            st.warning("Please save your Gemini API key first.")
        elif not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating explanation..."):
                prompt = (
                    f"Explain the following topic at a {level.split(' ')[1].lower()} level. "
                    f"Be clear, concise, and use examples where helpful. "
                    f"Format with clear sections if needed.\n\nTopic: {topic}"
                )
                try:
                    result = call_gemini(prompt, API_KEY)
                    st.markdown("#### 💡 Explanation")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error: {e}")


# TAB2  SUMMARIZE
with tab2:
    st.subheader("Summarize your study notes")
    st.caption("Paste any text or lecture notes and get a structured summary.")

    notes = st.text_area(
        "Notes",
        placeholder="Paste your notes, textbook content, or any text here...",
        height=180,
        label_visibility="collapsed",
    )
    style = st.selectbox(
        "Summary style",
        ["📌 Bullet points", "📄 Paragraph summary", "🔑 Key concepts with explanations"],
    )

    if st.button("Summarize ✦", type="primary", key="summarize_btn"):
        if not API_KEY:
            st.warning("Please save your Gemini API key first.")
        elif not notes.strip():
            st.warning("Please paste some notes.")
        else:
            with st.spinner("Summarizing..."):
                style_clean = style.split(" ", 1)[1]
                prompt = (
                    f"Summarize the following study notes as {style_clean}. "
                    f"Be concise and capture the most important points a student needs to remember.\n\n"
                    f"Notes:\n{notes}"
                )
                try:
                    result = call_gemini(prompt, API_KEY)
                    st.markdown("#### 📝 Summary")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error: {e}")


# TAB3 QUIZ 
with tab3:
    st.subheader("Generate quiz & flashcards")
    st.caption("Enter a topic or paste notes to instantly create study flashcards.")

    quiz_input = st.text_area(
        "Quiz topic",
        placeholder="e.g. The French Revolution / paste your chapter notes here...",
        height=130,
        label_visibility="collapsed",
    )
    count = st.selectbox("Number of flashcards", [4, 6, 8, 10], index=1)

    if st.button("Generate quiz ✦", type="primary", key="quiz_btn"):
        if not API_KEY:
            st.warning("Please save your Gemini API key first.")
        elif not quiz_input.strip():
            st.warning("Please enter a topic or notes.")
        else:
            with st.spinner("Creating flashcards..."):
                prompt = (
                    f"Generate exactly {count} flashcard-style Q&A pairs based on the following topic or notes. "
                    f"Return ONLY a JSON array with no extra text, in this exact format:\n"
                    f'[{{"q": "question here", "a": "answer here"}}, ...]\n\n'
                    f"Topic/Notes:\n{quiz_input}"
                )
                try:
                    raw = call_gemini(prompt, API_KEY)
                    clean = re.sub(r"```json|```", "", raw).strip()
                    cards = json.loads(clean)

                    st.markdown("**Click each expander to reveal the answer:**")
                    for i, card in enumerate(cards):
                        with st.expander(f"Q{i+1}. {card['q']}"):
                            st.success(f"💡 {card['a']}")

                except json.JSONDecodeError:
                    st.error("Could not parse quiz. Please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")


# Footer
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    "<center><small style='color:#8892a4'>Made by Vishv &nbsp;|&nbsp; "
    "Powered by <span style='color:#00d4aa'>Gemini AI</span></small></center>",
    unsafe_allow_html=True,
)
