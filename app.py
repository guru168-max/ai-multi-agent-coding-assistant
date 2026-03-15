import os
import streamlit as st
from groq import Groq
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Multi-Agent Coding Assistant",
    page_icon="🤖",
    layout="wide"
)

# =========================
# THEME TOGGLE
# =========================
theme = st.toggle("🌙 Dark Mode", value=True)

if theme:
    bg = "#0e1117"
    card_wait = "#444"
    card_run = "#ff9800"
    card_done = "#4CAF50"
    text_color = "white"
else:
    bg = "#f5f5f5"
    card_wait = "#cfcfcf"
    card_run = "#ff9800"
    card_done = "#4CAF50"
    text_color = "black"

st.markdown(f"""
<style>
body {{
background-color:{bg};
}}

.agent-card {{
padding:12px;
border-radius:10px;
text-align:center;
color:{text_color};
font-weight:bold;
}}

.wait {{background:{card_wait};}}
.run {{background:{card_run};}}
.done {{background:{card_done};}}
</style>
""", unsafe_allow_html=True)

# =========================
# GROQ CLIENT
# =========================

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# =========================
# SESSION STATE
# =========================
if "step" not in st.session_state:
    st.session_state.step = 0

if "problem" not in st.session_state:
    st.session_state.problem = ""

if "results" not in st.session_state:
    st.session_state.results = {}

if "memory" not in st.session_state:
    st.session_state.memory = []

# =========================
# MODEL CALL
# =========================
def call_agent(prompt):

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":prompt}]
        )

        return res.choices[0].message.content

    except Exception as e:

        return f"Error: {e}"

# =========================
# STREAMING TEXT
# =========================
def stream_text(text):

    placeholder = st.empty()
    output = ""

    for c in text:
        output += c
        placeholder.markdown(output)
        time.sleep(0.01)

# =========================
# MEMORY CONTEXT
# =========================
def memory_context():

    txt = ""

    for m in st.session_state.memory[-3:]:
        txt += f"Previous problem: {m}\n"

    return txt

# =========================
# SHOW RESULTS
# =========================
def show_results():

    if "explanation" in st.session_state.results:
        with st.expander("📘 Explanation", expanded=True):
            st.write(st.session_state.results["explanation"])

    if "hints" in st.session_state.results:
        with st.expander("💡 Hints"):
            st.write(st.session_state.results["hints"])

    if "code" in st.session_state.results:
        with st.expander("💻 Code"):
            st.code(st.session_state.results["code"])

    if "debug" in st.session_state.results:
        with st.expander("🐞 Debug Analysis"):
            st.write(st.session_state.results["debug"])

    if "tests" in st.session_state.results:
        with st.expander("🧪 Tests"):
            st.write(st.session_state.results["tests"])

    if "optimization" in st.session_state.results:
        with st.expander("⚡ Optimization"):
            st.write(st.session_state.results["optimization"])

# =========================
# AGENT CARD
# =========================
def agent_card(name,index):

    step = st.session_state.step

    if step > index:
        style="done"
    elif step == index:
        style="run"
    else:
        style="wait"

    st.markdown(
        f"<div class='agent-card {style}'>{name}</div>",
        unsafe_allow_html=True
    )

# =========================
# TIMELINE
# =========================
def agent_timeline(step):

    agents=["Explain","Hints","Code","Debug","Tests","Optimize"]

    timeline=""

    for i,a in enumerate(agents):

        if step>i+1:
            icon="✓"
        elif step==i+1:
            icon="⚙"
        else:
            icon="○"

        timeline+=f"[{icon} {a}]"

        if i<len(agents)-1:
            timeline+=" ➜ "

    st.markdown(f"### ⚡ Agent Timeline\n{timeline}")

# =========================
# HEADER
# =========================
st.markdown("""
<h1 style='text-align:center'>
🤖 Multi-Agent AI Coding System
</h1>
""", unsafe_allow_html=True)

# =========================
# MODE
# =========================
mode = st.selectbox(
"Mode",
["Learning Mode","Interview Mode"]
)

# =========================
# INPUT
# =========================
user_input = st.chat_input("Enter Coding Problem")

if user_input:
    st.session_state.problem = user_input
    st.session_state.step = 1
    st.session_state.memory.append(user_input)

problem = st.session_state.problem

if problem:
    st.write("**Problem:**",problem)

# =========================
# SIDEBAR MEMORY
# =========================
with st.sidebar:

    st.title("Agent Memory")

    for p in st.session_state.memory[-5:]:
        st.write("•",p)

# =========================
# EXTRA AI TOOLS
# =========================
c1,c2,c3=st.columns(3)

with c1:
    if st.button("Detect Difficulty") and problem:
        d=call_agent(
            f"Classify difficulty (Easy Medium Hard):\n{problem}"
        )
        st.info(d)

with c2:
    if st.button("Similar Problems") and problem:
        s=call_agent(
            f"Give 3 coding interview problems similar to:\n{problem}"
        )
        st.write(s)

with c3:
    if st.button("Algorithm Explanation") and problem:
        e=call_agent(
            f"Explain algorithm step-by-step:\n{problem}"
        )
        st.write(e)

# =========================
# PIPELINE UI
# =========================
agent_timeline(st.session_state.step)

progress=min(st.session_state.step/6,1.0)
st.progress(progress)

col1,col2,col3,col4,col5,col6=st.columns(6)

with col1: agent_card("Explain",1)
with col2: agent_card("Hints",2)
with col3: agent_card("Code",3)
with col4: agent_card("Debug",4)
with col5: agent_card("Tests",5)
with col6: agent_card("Optimize",6)

# =========================
# COLLABORATION MODE
# =========================
if problem and st.button("🚀 Collaboration Mode"):

    st.subheader("Agents Collaborating")

    exp = call_agent(f"Explain:\n{problem}")
    stream_text("### Explainer Agent\n"+exp)

    hints = call_agent(f"Give hints:\n{problem}")
    stream_text("\n\n### Hint Agent\n"+hints)

    code = call_agent(f"Write Python code:\n{problem}")
    stream_text("\n\n### Code Agent\n"+code)

# =========================
# INTERVIEW MODE
# =========================
if mode=="Interview Mode" and problem:

    if st.button("Start Interview"):

        q=call_agent(
            f"Ask 3 interview questions about:\n{problem}"
        )

        st.subheader("👨‍💻 AI Interviewer")
        st.write(q)

# =========================
# PIPELINE EXECUTION
# =========================
if st.session_state.step==1:

    res=call_agent(
        f"{memory_context()}Explain this coding problem:\n{problem}"
    )

    st.session_state.results["explanation"]=res
    st.session_state.step=2
    st.rerun()

elif st.session_state.step==2:

    show_results()

    if st.button("Run Hint Agent"):
        res=call_agent(f"Give hints:\n{problem}")
        st.session_state.results["hints"]=res
        st.session_state.step=3
        st.rerun()

elif st.session_state.step==3:

    show_results()

    if st.button("Run Code Agent"):
        res=call_agent(f"Write Python code:\n{problem}")
        st.session_state.results["code"]=res
        st.session_state.step=4
        st.rerun()

elif st.session_state.step==4:

    show_results()

    if st.button("Run Debug Agent"):

        code=st.session_state.results["code"]

        res=call_agent(
            f"Debug this code:\n{code}"
        )

        st.session_state.results["debug"]=res
        st.session_state.step=5
        st.rerun()

elif st.session_state.step==5:

    show_results()

    if st.button("Run Test Agent"):

        res=call_agent(
            f"Generate test cases:\n{problem}"
        )

        st.session_state.results["tests"]=res
        st.session_state.step=6
        st.rerun()

elif st.session_state.step==6:

    show_results()

    if st.button("Run Optimization Agent"):

        res=call_agent(
            f"Explain optimization and time complexity:\n{problem}"
        )

        st.session_state.results["optimization"]=res
        st.session_state.step=7
        st.rerun()

elif st.session_state.step==7:

    st.success("All agents completed")

    show_results()