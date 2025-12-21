import streamlit as st
import requests

# Backend API URL
API_URL = "https://lh9fjb64-5000.uks1.devtunnels.ms/"

st.title("📝 MCQ Generator")
st.write("Generate multiple choice questions from text or uploaded documents")

# Tab selection
tab1, tab2 = st.tabs(["📄 Upload File", "✍️ Enter Text"])

# Tab 1: File Upload
with tab1:
    st.subheader("Upload a PDF or Word Document")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "doc"])
    num_questions_file = st.number_input("Number of questions", min_value=1, max_value=20, value=5, key="file")
    
    if st.button("Generate MCQs from File", type="primary"):
        if uploaded_file is not None:
            with st.spinner("Generating MCQs..."):
                try:
                    files = {"file": uploaded_file}
                    data = {"nb_questions": num_questions_file}
                    response = requests.post(f"{API_URL}/generate_mcq_file", files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        mcqs = result.get("mcqs", [])
                        
                        st.success(f"✅ Generated {len(mcqs)} MCQs!")
                        
                        for i, mcq in enumerate(mcqs, 1):
                            with st.expander(f"Question {i}: {mcq.get('question', 'N/A')}"):
                                st.write("**Options:**")
                                for opt in mcq.get('options', []):
                                    st.write(f"- {opt}")
                                st.write(f"**Correct Answer:** {mcq.get('correct_answer', 'N/A')}")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")
        else:
            st.warning("Please upload a file first!")

# Tab 2: Text Input
with tab2:
    st.subheader("Enter Text Directly")
    
    text_input = st.text_area("Paste your text here", height=200)
    num_questions_text = st.number_input("Number of questions", min_value=1, max_value=20, value=5, key="text")
    
    if st.button("Generate MCQs from Text", type="primary"):
        if text_input.strip():
            with st.spinner("Generating MCQs..."):
                try:
                    payload = {"text": text_input, "nb_questions": num_questions_text}
                    response = requests.post(f"{API_URL}/generate_mcq", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        mcqs = result.get("mcqs", [])
                        
                        st.success(f"✅ Generated {len(mcqs)} MCQs!")
                        
                        for i, mcq in enumerate(mcqs, 1):
                            with st.expander(f"Question {i}: {mcq.get('question', 'N/A')}"):
                                st.write("**Options:**")
                                for opt in mcq.get('options', []):
                                    st.write(f"- {opt}")
                                st.write(f"**Correct Answer:** {mcq.get('correct_answer', 'N/A')}")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")
        else:
            st.warning("Please enter some text first!")

# Footer
st.divider()
st.caption("Make sure your Flask backend is running on http://127.0.0.1:5000")