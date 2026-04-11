import streamlit as st
from bioLOLPython.interpreter import handle_line, reset_bio_vars
from bioLOLPython.dialects import get_dialect, list_dialects, dialect_names
import io
from contextlib import redirect_stdout

# Styling
st.set_page_config(
    page_title="bioLOL Webshell",
    layout="wide",
    page_icon="😹"
)
st.markdown(
    """
    <style>
        .stApp {
            background-color: rgba(0,0,0) !important;
            color: #33ff33;
            font-family: 'Courier New', Courier, monospace;
        }
        .stTextArea textarea {
            background-color: rgba(0,0,0,0.7) !important;
            color: #33ff33 !important;
        }
        .stButton>button {
            background-color: #111;
            border: 1px solid #33ff33;
            color: #33ff33;
        }
        h1, h2, h3, h4, h5, h6 {
            color: white !important;
        }
        .css-1lcbmhc.e1f1d6gn0 {
           gap: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)


st.title("bioLOL Interpurr-ter")
st.markdown("_A time capsule of internet slang meets bioinformatics. Pick your meme era and sequence some DNA._")

col1, col2 = st.columns(2, gap="large", border=True)
with col1:
    st.markdown("""

### What is this?

**bioLOLPython** is a bioinformatics scripting language written in internet slang. Each dialect represents a different era of internet culture:

- **lolcat** (~2005-2012): The original cheezburger era
- **gen_z** (~2018-2023): TikTok-era slang
- **brainrot** (~2023-2026): Skibidi sigma posting

Built on [LOLPython](https://github.com/KartikTalwar/LOLPython) and [Biopython](https://biopython.org/).

![](https://github.com/ChenHsieh/bioLOLPython/blob/master/static/bg_lolcat.jpg?raw=true)

    """)
with col2:
    st.markdown("""

### How to Use

1. Choose a **meme era** (dialect) from the dropdown.
2. Pick an example or write your own script.
3. Click **RUN da CODE** to see the output.

Each dialect uses different slang for the same DNA operations.
""")
    st.divider()

    # Dialect selector
    dialect_info = {d["name"]: d for d in list_dialects()}
    dialect_name = st.selectbox(
        "🎭 Choose your meme era:",
        dialect_names(),
        format_func=lambda n: f"{n} ({dialect_info[n]['era']}) — {dialect_info[n]['description']}"
    )

    # Get dialect-specific examples
    dialect = get_dialect(dialect_name)
    examples = dialect.get("examples", {})

    # Selection
    st.markdown("Choose an example or start typing your own:")
    script_option = st.selectbox(
        "Choose an example:",
        ["Write your own"] + list(examples.keys()),
        label_visibility="collapsed",
    )

    # Script input
    default_code = examples.get(script_option, "")
    st.markdown("Write your .lolz code here:")
    code = st.text_area(
        "Write your .lolz code here:",
        default_code,
        height=200,
        label_visibility="collapsed",
    )

    # Run
    if st.button("💥 RUN da CODE"):
        st.subheader("Outputz")
        reset_bio_vars()
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            try:
                for line in code.splitlines():
                    result = handle_line(line.strip(), dialect_name=dialect_name)
                    if result is not None:
                        print(result)
            except Exception as e:
                st.error(f"Oopsie: {e}")
        st.code(output_buffer.getvalue(), language="text")
