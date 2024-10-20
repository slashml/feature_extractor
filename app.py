import streamlit as st
import pandas as pd
from anthropic import Anthropic
from io import BytesIO
import PyPDF2
import os
from datetime import datetime
import json
import re

def init_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return Anthropic(api_key=api_key)

def read_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF {uploaded_file.name}: {str(e)}")
        return None

def clean_json_string(text):
    """Clean and extract JSON from Claude's response"""
    # Try to find JSON-like structure in the text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        # Replace any invalid escape sequences
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        return json_str
    return None

def extract_information(client, text):
    system_prompt = """You are a research paper data extractor. Your task is to extract specific information and return it ONLY as a JSON object, with no additional text or explanation. 

Extract exactly these fields:
1. First author last name
2. Publication year
3. Journal name
4. Country of corresponding author
5. Funding source (ONLY use: Industry/Non-industry/Combined/No funding/Not reported)
6. Author financial conflicts of interest
7. Main eligibility criteria
8. Country(ies) of participants
9. N included
10. N (%) females/women
11. Trial arm names
12. Group descriptions

Return ONLY this JSON structure with no other text:
{
    "first_author": "",
    "pub_year": "",
    "journal": "",
    "corresponding_author_country": "",
    "funding_source": "",
    "conflicts": "",
    "eligibility_criteria": "",
    "participant_countries": "",
    "n_included": "",
    "females_percentage": "",
    "trial_arms": "",
    "group_descriptions": ""
}

If you cannot find information for a field, use "Not reported" as the value. Do not include any explanatory text outside the JSON structure."""

    try:
        # Send request to Claude
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0,  # Added temperature=0 for more consistent outputs
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract the requested information from this paper and return it ONLY as a JSON object: {text[:50000]}"
                }
            ]
        )
        
        # Get the response text
        response_text = message.content[0].text
        
        # Try to parse the direct response first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to clean the response
            clean_json = clean_json_string(response_text)
            if clean_json:
                return json.loads(clean_json)
            else:
                st.error(f"Could not extract valid JSON from response")
                st.text("Response received:")
                st.text(response_text[:500])  # Show first 500 chars of response for debugging
                return None
                
    except Exception as e:
        st.error(f"Error during extraction: {str(e)}")
        return None

def main():
    st.title("Research Paper Data Extractor")
    
    # Initialize session state
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = []
    
    # Add a clear button
    if st.button("Clear All Data"):
        st.session_state.extracted_data = []
        st.success("Data cleared!")
    
    # File uploader
    uploaded_files = st.file_uploader("Upload PDF files", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        client = init_client()
        
        # Process button
        if st.button("Process Files"):
            progress_bar = st.progress(0)
            failed_files = []
            
            for idx, file in enumerate(uploaded_files):
                try:
                    # Update progress
                    progress = (idx + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    
                    # Process file
                    st.write(f"Processing: {file.name}")
                    text = read_pdf(file)
                    
                    if text:
                        # Extract information
                        data = extract_information(client, text)
                        if data:
                            data['filename'] = file.name
                            st.session_state.extracted_data.append(data)
                        else:
                            failed_files.append(file.name)
                    else:
                        failed_files.append(file.name)
                        
                except Exception as e:
                    st.error(f"Error processing {file.name}: {str(e)}")
                    failed_files.append(file.name)
            
            if failed_files:
                st.error(f"Failed to process: {', '.join(failed_files)}")
            else:
                st.success("Processing complete!")
        
        # Show results
        if st.session_state.extracted_data:
            df = pd.DataFrame(st.session_state.extracted_data)
            st.write("Extracted Data:")
            st.dataframe(df)
            
            # Download button
            if st.button("Download Excel"):
                try:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    
                    output.seek(0)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    st.download_button(
                        label="Click to Download",
                        data=output,
                        file_name=f"extracted_data_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Error creating Excel file: {str(e)}")

if __name__ == "__main__":
    main()