import numpy as np
import streamlit as st
from langchain import OpenAI
import faiss
import pandas as pd
import re
import os
from langchain_openai import AzureOpenAIEmbeddings


endpoint = os.getenv("ENDPOINT_URL")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  

# Load the CSV file into a DataFrame
df = pd.read_csv('./Dataset/messages.csv')

# Filter data based on a specific value in a column
df = df[df['blocks'] == '[{"type": "rich_text"}]']

# function to replace data in a row in a column using regex
def replace_data(row, column, pattern, replacement):
    if isinstance(row[column], str):
        row[column] = re.sub(pattern, replacement, row[column])
    return row

df = df.apply(lambda row: replace_data(row, 'text', r'<@[A-Z0-9]+>', ''), axis=1)
# Ensure all text data is string and handle missing values
df['text'] = df['text'].fillna('').astype(str)


embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002")
# Generate embeddings
df['embeddings'] = df['text'].apply(lambda x: embeddings.embed_documents([x])[0])

# Convert embeddings to numpy array
embedding_matrix = np.array(df['embeddings'].tolist())


# Create FAISS index
index = faiss.IndexFlatL2(embedding_matrix.shape[1])
index.add(embedding_matrix)

# Save the index to a file
faiss.write_index(index, 'faiss_index.bin')

# Load FAISS index
index = faiss.read_index('faiss_index.bin')

# Configure LangChain
llm = OpenAI(api_key=subscription_key, api_base= endpoint)

def get_relevant_text(query):
    # Convert query to vector using AzureOpenAIEmbeddings
    query_vector = embeddings.embed_query(query)

    # Search FAISS index
    D, I = index.search(np.array([query_vector]), k=5)  # Get top 5 results

    # Ensure indices are valid
    relevant_texts = []
    for i in I[0]:
        if i < len(df):  # Check if index exists in DataFrame
            relevant_texts.append(df.iloc[i]['text'])  # Use iloc for positional indexing
        else:
            relevant_texts.append(f"Index {i} not found in DataFrame")
    return relevant_texts

def generate_response(query):
    relevant_texts = get_relevant_text(query)
    context = " ".join(relevant_texts)
    response = llm.generate(context + query)
    return response

st.title("RAG Application with FAISS and LangChain")
query = st.text_input("Enter your query:")
if query:
    response = generate_response(query)
    st.write(response)