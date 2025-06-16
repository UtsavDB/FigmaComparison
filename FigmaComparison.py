#!/usr/bin/env python3
"""
send_prompt.py

Usage:
    python send_prompt.py path/to/Baseline.file path/to/Current.file
"""

import os
import argparse
import base64

import openai
import sys
from datetime import datetime

def load_env():
    # Make sure these four are set in your shell or .env
    openai.api_key    = os.getenv("OPENAI_API_KEY")
    openai.api_type   = "azure"
    openai.api_base   = os.getenv("OPENAI_API_BASE")
    openai.api_version= os.getenv("OPENAI_API_VERSION")
    if not all([openai.api_key, openai.api_base, openai.api_version]):
        raise RuntimeError("Please set OPENAI_API_KEY, OPENAI_API_BASE and OPENAI_API_VERSION")

def read_prompt_template():
    path = os.path.join("Prompt_template", "Figma_promptTemplate.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def encode_file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def build_full_prompt(template: str, file1_path: str, file2_path: str) -> str:
    # read & encode
    file1_b64 = encode_file_to_base64(file1_path)
    file2_b64 = encode_file_to_base64(file2_path)

    # if your template already has placeholders like {file1_b64} you can:
    return template.format(
        file1_name=os.path.basename(file1_path),
        file1_b64=file1_b64,
        file2_name=os.path.basename(file2_path),
        file2_b64=file2_b64,
    )
    
    # otherwise we simply append both attachments at the end:
#     attachment_block = f"""
# --- Attachment: {os.path.basename(file1_path)} ---
# {file1_b64}

# --- Attachment: {os.path.basename(file2_path)} ---
# {file2_b64}
# """
#     return template + "\n" + attachment_block

def compare_figma_and_ui(figma_jpeg=None, ui_jpeg=None, difference_pdf=None):
    """
    Compares Figma and UI images or a difference PDF using Azure OpenAI.
    If difference_pdf is provided, figma_jpeg and ui_jpeg are ignored.
    """
    load_env()
    prompt_template = read_prompt_template()
    if difference_pdf:
        # Use the difference PDF as both file1 and file2 for prompt (or adjust as needed)
        file1 = difference_pdf
        file2 = difference_pdf
    else:
        file1 = figma_jpeg
        file2 = ui_jpeg
    full_prompt = build_full_prompt(prompt_template, file1, file2)

    client = openai.AzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_API_BASE")
    )
    models = client.models.list()
    print("Loaded environment variables:")
    print(f"  OPENAI_API_KEY: {'set' if openai.api_key else 'not set'}")
    print(f"  OPENAI_API_BASE: {openai.api_base}")
    print(f"  OPENAI_API_VERSION: {openai.api_version}")
    deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
    print(f"  deployment_name: {deployment_name}")

    resp = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": full_prompt}]
    )
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + ".md"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(resp.choices[0].message.content)
    print(f"Response saved to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Send a template + two attachments to Azure OpenAI")
    parser.add_argument("file1", nargs="?", help="First file path")
    parser.add_argument("file2", nargs="?", help="Second file path")
    parser.add_argument("--difference_pdf", help="Difference PDF file path", default=None)
    args = parser.parse_args()

    if args.difference_pdf:
        compare_figma_and_ui(difference_pdf=args.difference_pdf)
    else:
        file1 = args.file1 or "./Inputs/Overview and schedule Figma.png"
        file2 = args.file2 or "./Inputs/Overview and schedule Implementation.png"
        compare_figma_and_ui(figma_jpeg=file1, ui_jpeg=file2)


if __name__ == "__main__":
    main()
