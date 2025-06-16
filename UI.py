# app.py
import os
import datetime
import streamlit as st
from FigmaComparison import compare_figma_and_ui

# ---- Page config ----
st.set_page_config(
    page_title="Compare Figma Designs with UI Renders",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- CSS & Navbar HTML ----
st.markdown(
    """
    <style>
      /* reset Streamlit padding */
      .block-container { padding: 0; }

      /* Navbar */
      .nav { display: flex; justify-content: space-between; align-items: center;
             padding: 0.75rem 2rem; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
      .nav .brand { font-weight: bold; font-size: 1.25rem; }
      .nav-links a { margin-right: 1.5rem; color: #333; text-decoration: none; font-weight: 500; }
      .nav-links a:last-child { margin-right: 0; }
      .btn-contact { 
        background-color: #007bff; color: #fff; padding: 0.5rem 1rem; border-radius: 4px;
        text-decoration: none; font-weight: 500;
      }

      /* Title & subtitle */
      .header { padding: 2rem 2rem 0 2rem; }
      .header h1 { margin-bottom: 0.25rem; }
      .header p { margin-top: 0; color: #555; }

      /* Upload area */
      .upload-card { background: #fff; border-radius: 8px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
      .dropzone { border: 2px dashed #ccc !important;
                  border-radius: 6px; padding: 2rem; text-align: center; color: #666;
                  font-size: 0.95rem; }
      /* Streamlit file_uploader comes wrapped; force it to fit */
      div[data-testid="fileUploader"] > label { display: none; }
      div[data-testid="fileUploader"] { padding: 0 !important; }

      /* Buttons */
      .process-btn button { background-color: #007bff !important; color: #fff !important;
                             padding: 0.6rem 1.2rem; border-radius: 4px; border: none; }
      .download-btn button { background-color: #6c757d !important; color: #fff !important;
                              padding: 0.5rem 1rem; border-radius: 4px; border: none; }

      /* Generated markdown area */
      .results { background: #f8f9fa; border-radius: 8px; padding: 1.5rem; min-height: 200px; }
    </style>

    <div class="nav">
      <div class="brand">Aristocrat Leisure Limited</div>
      <div class="nav-links">
        <a href="#">Home</a>
        <a href="#">Products</a>
        <a href="#">Services</a>
        <a href="#">Support</a>
        <a href="#">About Us</a>
        <a href="#" class="btn-contact">Contact Us</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Header ----
st.markdown(
    """
    <div class="header">
      <h1>Compare Figma Designs with UI Renders</h1>
      <p>Upload your Figma design screenshots or a PDF file to compare with UI renders. The system will generate a markdown file for your review and download.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- File upload UI ----
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown("**Upload Screenshots**", unsafe_allow_html=True)
    st.markdown('<div class="dropzone">Drag & drop or click to browse</div>', unsafe_allow_html=True)
    imgs = st.file_uploader(
        label="", type=["png","jpg","jpeg"], accept_multiple_files=True, key="imgs"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown("**Upload PDF**", unsafe_allow_html=True)
    st.markdown('<div class="dropzone">Drag & drop or click to browse</div>', unsafe_allow_html=True)
    pdf = st.file_uploader(label="", type=["pdf"], accept_multiple_files=False, key="pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Process button ----
st.markdown('<div class="upload-card process-btn" style="margin-top:1rem;">', unsafe_allow_html=True)
if st.button("Process Files"):
    # prepare Inputs folder
    os.makedirs("Inputs", exist_ok=True)
    ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

    figma_path = ui_path = diff_pdf = None

    if pdf:
        # save only PDF
        name = f"pdf_{ts}.pdf"
        pdf_path = os.path.join("Inputs", name)
        with open(pdf_path, "wb") as f:
            f.write(pdf.getbuffer())
        diff_pdf = pdf_path
    else:
        # require exactly two images
        if len(imgs) != 2:
            st.error("Please upload exactly two images (Figma + UI).")
        else:
            f1, f2 = imgs
            ext1 = os.path.splitext(f1.name)[1]
            ext2 = os.path.splitext(f2.name)[1]
            figma_path = os.path.join("Inputs", f"figma_{ts}{ext1}")
            ui_path    = os.path.join("Inputs", f"ui_{ts}{ext2}")
            with open(figma_path, "wb") as f:
                f.write(f1.getbuffer())
            with open(ui_path, "wb") as f:
                f.write(f2.getbuffer())

    # run comparison
    if pdf or (figma_path and ui_path):
        md_file = compare_figma_and_ui(
            figma_jpeg=figma_path,
            ui_jpeg=ui_path,
            difference_pdf=diff_pdf
        )
        # read markdown
        md = open(md_file, encoding="utf-8").read()
        st.session_state["md"] = md

st.markdown("</div>", unsafe_allow_html=True)

# ---- Generated Markdown section ----
st.markdown('<div class="upload-card" style="margin-top:2rem;">', unsafe_allow_html=True)
st.markdown("**Generated Markdown**", unsafe_allow_html=True)

dl_disabled = "disabled" if "md" not in st.session_state else ""
href = ""
if "md" in st.session_state:
    data = st.session_state["md"].encode("utf-8")
    href = st.download_button(
        label="Download Markdown",
        data=data,
        file_name="comparison.md",
        mime="text/markdown",
        key="download",
    )

st.markdown('<div class="results">', unsafe_allow_html=True)
if "md" in st.session_state:
    st.markdown(st.session_state["md"], unsafe_allow_html=False)
else:
    st.markdown("_No Markdown Generated Yet_\n\nUpload a file to generate the markdown content.")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
