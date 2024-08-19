import streamlit as st
import re
from collections import defaultdict



with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
def tokenize(text):
    return set(re.findall(r'\b\w+\b', text.lower()))

def build_inverted_index(docs):
    index = defaultdict(set)
    for doc_id, text in docs.items():
        words = tokenize(text)
        for word in words:
            index[word].add(doc_id)
    return index

def boolean_retrieval(index, query, all_docs):
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    result_docs = set(all_docs)

    if 'and' in query:
        terms = query.split(' and ')
        result_docs = index.get(terms[0].strip(), set())
        for term in terms[1:]:
            result_docs = result_docs.intersection(index.get(term.strip(), set()))
    elif 'or' in query:
        result_docs = set()
        terms = query.split(' or ')
        for term in terms:
            result_docs = result_docs.union(index.get(term.strip(), set()))
    elif 'not' in query:
        terms = query.split(' not ')
        if len(terms) == 2:
            term_to_exclude = terms[1].strip()
            result_docs = result_docs.difference(index.get(term_to_exclude, set()))
    else:
        result_docs = set()
        for token in tokens:
            result_docs = result_docs.union(index.get(token, set()))

    return result_docs

file_dict = {}
st.title("BrowseHub")

uploaded_files = st.file_uploader("Upload Text Files", accept_multiple_files=True, type=['txt'])

if uploaded_files:
    for uploaded_file in uploaded_files:
        content = uploaded_file.read().decode("utf-8")
        file_dict[uploaded_file.name] = content

    inverted_index = build_inverted_index(file_dict)
    
    query = st.text_input("Enter your query:")
    
    if query:
        results = boolean_retrieval(inverted_index, query, file_dict.keys())
        if results:
            st.write("Results:")
            for doc_id in results:
                st.write(f"**{doc_id}:**")
                st.text(file_dict[doc_id])
        else:
            st.write("No documents match your query.")
