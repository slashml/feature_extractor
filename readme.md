# Feature Extractor

## Overview

Feature extractor is a Streamlit-based web application that is used to extract specific information from the uploaded documents. It uses advanced natural language processing techniques to extract key information, and generate an excel file containing the extracted data.


## Technologies Used

- Python
- Streamlit
- Anthropic's Claude AI model


## Setup

1. Clone the repository:
   ```
   git clone repo_link
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Anthropic API key:
   - Option 1: Set it as an environment variable:
     ```
     export ANTHROPIC_API_KEY=your_api_key_here
     ```

## Usage

1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Upload multiple pdf documents.



