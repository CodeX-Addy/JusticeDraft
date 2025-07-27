import io
import os
import google.generativeai as genai
from flask import Flask, send_file, request, jsonify
from model import *
import os.path
import getpass

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Gemini LLM's API key: ")

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

app = Flask(__name__)

def initialize_faiss_index():
    if not os.path.exists("faiss_index"):
        print("Initializing FAISS index...")
        default_docs = ["Divorce.pdf", "Hypothecation.pdf"]
        existing_docs = [doc for doc in default_docs if os.path.exists(doc)]
        
        if existing_docs:
            Model.embed_pdf_documents(existing_docs)
            print(f"FAISS index created with documents: {existing_docs}")
        else:
            print("Warning: No default documents found. FAISS index initialization skipped.....")

@app.route('/')
def index():
    return app.send_static_file('index.html')

def get_gemini_response(query):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        context = """
        You are an AI assistant for JusticeDraft, a legal document drafting platform. 
        Focus on providing helpful information about:
        - Legal documents types
        - Document generation process
        - Legal terminologies and jargons
        - General legal guidance
        - FOR ANY OTHER QUESTIONS, REPLY WITH "I CAN'T HELP WITH THAT."
        Be professional, concise, and helpful.
        """

        full_prompt = f"{context}\n\nUser Query: {query}"   
        response = model.generate_content(full_prompt)  
        return response.text
        
    except Exception as e:
        print(f"Error in get_gemini_response: {str(e)}")
        return f"An error occurred: {str(e)}"

@app.route('/chatbot-query', methods=['POST'])
def chatbot_query():
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({"response": "Please ask a valid question."})

    response = get_gemini_response(query)
    if not isinstance(response, str):
        response = str(response)
        
    return jsonify({"response": response})

@app.route('/generate-document', methods=['POST'])
def generate_document():
    data = request.json
    document_type = data['documentType']
    
    if not os.path.exists("faiss_index"):
        initialize_faiss_index()
    
    custom_prompt = f"Generate LaTeX code for {document_type} document"
    try:
        latex_code = Model.user_input(custom_prompt)
        Compilation.generate_pdf(latex_code)
        
        return send_file(
            'user_document.pdf',
            mimetype='application/pdf',
            as_attachment=False
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update-document', methods=['POST'])
def update_document():
    data = request.json
    document_type = data['documentType']
    updates = data['updates']
    
    if not os.path.exists("faiss_index"):
        initialize_faiss_index()
    
    try:
        custom_prompt = f"Generate LaTeX code for this {document_type} document and {updates}"
        latex_code = Model.user_input(custom_prompt)
        Compilation.generate_pdf(latex_code)
        
        return send_file(
            'user_document.pdf',
            mimetype='application/pdf',
            as_attachment=False
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize_faiss_index()
    app.run(debug=True)
