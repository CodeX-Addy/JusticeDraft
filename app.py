from flask import Flask, send_file, request, jsonify
from model import Compilation, Model, Simulations
import io

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate-document', methods=['POST'])
def generate_document():
    data = request.json
    document_type = data['documentType']
    
    # Use your existing code to generate the document
    custom_prompt = f"Generate LaTeX code for {document_type} document"
    latex_code = Model.user_input(custom_prompt)
    Compilation.generate_pdf(latex_code)
    
    # Send the generated PDF
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
    
    # Generate updated document
    custom_prompt = f"Generate LaTeX code for {document_type} document and {updates}"
    latex_code = Model.user_input(custom_prompt)
    Compilation.generate_pdf(latex_code)
    
    # Send the updated PDF
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