# UI.py – Dark‑theme interface with live Markdown preview + raw source
# -------------------------------------------------------------------
# Streamlit app for comparing Figma screenshots or a diff‑PDF against UI renders.
# This build fixes the **preview still empty** issue by handling both return‐types
# from `compare_figma_and_ui()`:
#   • It might return raw Markdown **content** (string)
#   • Or a **path** to a generated .md file
# We now detect which case we have, read the file when necessary, and always
# pass the real Markdown text to the preview / raw viewer / download button.

import os
import tempfile
import datetime as dt
import streamlit as st
from FigmaComparison import compare_figma_and_ui

# ── Page config & dark theme override ─────────────────────────────────────────
st.set_page_config(page_title="Compare Figma UI", layout="wide")
st.markdown(
    """
    <style>
      /* Remove default white cards and containers */
      section.block-container, .stFileUploader, .stButton { background-color: transparent !important; }
      /* Ensure dark background */
      .stApp, .stApp>div { background-color: #0f0f0f !important; color: #f5f5f5 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🔍 Compare Figma design to live UI renders")
st.write(
    "Upload **two screenshots** (Figma & Implementation) *or* a **single diff‑PDF**. "
    "Click **Process Files** to generate a Markdown deviation report."
)

# ── File uploaders ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")
with col1:
    screenshots = st.file_uploader(
        "Screenshots (exactly two – PNG / JPG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )
with col2:
    pdf_file = st.file_uploader(
        "Diff‑PDF (upload one file only)",
        type=["pdf"],
        accept_multiple_files=False,
    )

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_temp_file(uploaded):
    """Save an UploadedFile to a temp path and return the path."""
    suffix = os.path.splitext(uploaded.name)[1]
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(uploaded.getbuffer())
    return path

# ── Processing ─────────────────────────────────────────────────────────────────
if st.button("🔍 Process Files"):
    # Decide mode & validate
    if screenshots and not pdf_file:
        if len(screenshots) != 2:
            st.error("Please upload exactly two screenshots.")
            st.stop()
        f1_path = to_temp_file(screenshots[0])
        f2_path = to_temp_file(screenshots[1])
        result = compare_figma_and_ui(f1_path, f2_path)
    elif pdf_file and not screenshots:
        pdf_path = to_temp_file(pdf_file)
        result = compare_figma_and_ui(pdf_path)
    else:
        st.error("Choose either two screenshots *or* one PDF — not both and not none.")
        st.stop()

    st.success("✅ Analysis complete – scroll down for the report.")

    # ── Determine if `result` is a path or raw Markdown ───────────────────────
    if isinstance(result, str) and os.path.isfile(result):
        md_path = result
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    else:
        md_content = str(result)
        # Persist to /output for download convenience
        os.makedirs("output", exist_ok=True)
        timestamp = dt.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        md_path = os.path.join("output", f"{timestamp}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

    # ── Report viewer ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Generated Report 📄")
    preview_tab, raw_tab = st.tabs(["Preview", "Raw Source"])

    with preview_tab:
        st.markdown(md_content, unsafe_allow_html=False)

    with raw_tab:
        st.text_area("Raw Markdown", value=md_content, height=400)

    # ── Download button ───────────────────────────────────────────────────────
    st.download_button(
        label="Download Markdown",
        data=md_content,
        file_name=os.path.basename(md_path),
        mime="text/markdown",
    )
