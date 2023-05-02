from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import  Pinecone,  FAISS
from dotenv import load_dotenv
import os
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
import io


load_dotenv()

OPENAI_KEY = ""

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

from typing import List

def get_raw_text(pdf_data) -> str:
    file_obj = io.BytesIO(pdf_data)
    reader = PdfReader(file_obj)
    raw_text = ''
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text
    return raw_text

def get_text_chunks(raw_text: str) -> List[str]:
    splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    text_chunks = splitter.split_text(raw_text)
    return list(text_chunks)

@app.route('/search', methods=['POST'])
def search():
    pdf_file = request.files['pdf_file']
    pdf_data = pdf_file.read()
    raw_text = get_raw_text(pdf_data)
    text_chunks = get_text_chunks(raw_text)

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_KEY)
    docsearch = FAISS.from_texts(list(text_chunks), embeddings)

    query = request.form.get('query')
    if query:
        docs = docsearch.similarity_search(query)
        page_docs = docs[0].page_content

        openai_chat = ChatOpenAI(model_name='gpt-3.5-turbo', openai_api_key=OPENAI_KEY)
        chain = load_qa_chain(openai_chat, chain_type="stuff")

        result = chain.run(input_documents=docs, question=query)
        return jsonify(result=result)
    else:
        return jsonify(error='Query parameter missing')

if __name__ == '__main__':
    app.run(debug=True)