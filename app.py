import io
import os
import google.generativeai as genai
from flask import Flask, send_file, request, jsonify
from model import Compilation, Model, Simulations


app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(query):
    model = genai.GenerativeModel('gemini-pro')
    context = """
    You are an AI assistant for JusticeDraft, a legal document generation platform. 
    Focus on providing helpful information about:
    - Legal document types
    - Document generation process
    - Legal terminology
    - General legal guidance
    
    Be professional, concise, and helpful.
    """

    full_prompt = f"{context}\n\nUser Query: {query}"

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/chatbot-query', methods=['POST'])
def chatbot_query():
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({"response": "Please ask a valid question."})

    response = get_gemini_response(query)
    return jsonify({"response": response})


@app.route('/generate-document', methods=['POST'])
def generate_document():
    data = request.json
    document_type = data['documentType']
    
    ## From existing code
    custom_prompt = f"Generate LaTeX code for {document_type} document"
    latex_code = Model.user_input(custom_prompt)
    Compilation.generate_pdf(latex_code)
    
    ## Sending the generated PDF
    try:
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
    
    ## Generating the updated document
    custom_prompt = f"Generate LaTeX code for {document_type} document and {updates}"
    latex_code = Model.user_input(custom_prompt)
    Compilation.generate_pdf(latex_code)
    
    ## Sending the updated PDF
    try:
        return send_file(
            'user_document.pdf',
            mimetype='application/pdf',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
