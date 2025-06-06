# FigmaComparison

This script (`FigmaComparison.py`) facilitates automated visual comparison between two Figma design files (or screenshots) using Azure OpenAI. It encodes the files in base64, combines them with a prompt template, and sends the full prompt to Azure OpenAI for analysis. The result is saved as a Markdown file with a timestamped filename.

## Features

- Reads and encodes two image files (baseline and current).
- Injects the encoded images into a customizable prompt template.
- Sends the structured prompt to an Azure OpenAI chat model.
- Outputs the model's response to a `.md` file named with the current date.

---

## Requirements

Ensure the following environment variables are set either in your shell or `.env` file:

- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- `OPENAI_API_VERSION`
- `OPENAI_DEPLOYMENT_NAME`

---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/UtsavDB/FigmaComparison
    cd your-repo
    ```

2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

