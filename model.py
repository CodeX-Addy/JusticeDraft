import os
import re
import subprocess
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class Compilation:
    def __init__(self):
        pass

    @staticmethod
    def generate_pdf(latex_code):
        tex_filename = 'user_document.tex'
        with open(tex_filename, 'w') as tex_file:
            tex_file.write(latex_code)
        try:
            subprocess.run(
                ['pdflatex', '-interaction=batchmode', tex_filename], check=True)
        except subprocess.CalledProcessError as e:
            print("PDF generation failed:", e)
            return

        if os.path.exists('user_document.pdf'):
            print("PDF generated successfully.")
        else:
            print("Generated PDF file not found.")

        auxiliary_files = ['user_document.aux',
                           'user_document.log', tex_filename]
        for aux_file in auxiliary_files:
            if os.path.exists(aux_file):
                    os.remove(aux_file)

class Simulations:
    def __init__(self):
        pass

    def user_satisfaction(question):
        divorce_pattern = re.compile(
            r'\b(divorce|separation|Divorce|DIVORCE)\b', re.IGNORECASE)
        hypothecation_pattern = re.compile(
            r'\b(hypothecation|Hypothecation|HYPOTHECATION)\b', re.IGNORECASE)

        if divorce_pattern.search(question):
            Model.embed_pdf_documents(["Divorce.pdf"])
            custom_prompt = "Generate LaTeX code for divorce document"
        elif hypothecation_pattern.search(question):
            Model.embed_pdf_documents(["Hypothecation.pdf"])
            custom_prompt = "Generate LaTeX code for hypothecation document"
        else:
            print("No matching document found for the question.")
            return
        
        latex_code = Model.user_input(custom_prompt)
        Compilation.generate_pdf(latex_code)

        satisfied = False
        while not satisfied:
            satisfaction = input(
                "Are you satisfied with the generated document? (yes/no): ")

            if satisfaction.lower() == "yes":
                print("Thank you! We are happy to help you.")
                satisfied = True

            elif satisfaction.lower() == "no":
                update_prompt = input(
                    "What do you want to update in the document? ")
                custom_prompt = f"{custom_prompt} and {update_prompt}"
                latex_code = Model.user_input(custom_prompt)
                Compilation.generate_pdf(latex_code)

class Model:
    def __init__(self):
        pass

    def get_pdf_text(pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=1500,
            length_function=len
        )
        text_chunks = text_splitter.split_text(text)
        return text_chunks

    def embed_text_chunks(text_chunks):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")

    def embed_pdf_documents(pdf_docs):
        text = Model.get_pdf_text(pdf_docs)
        text_chunks = Model.get_text_chunks(text)
        Model.embed_text_chunks(text_chunks)

    def get_conversational_chain():
        prompt_template = """
            Give latex code from pdf as it is, as per the input document type. Make sure do not include any other content or formatting. Just give the output same as written code in pdf
            Context:\n {context}?\n
            Question: \n{question}\n

            Answer:
        """

        model = ChatGoogleGenerativeAI(model="gemini-pro",
                                       temperature=0.3)
        prompt = PromptTemplate(template=prompt_template,
                                input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        return chain

    def user_input(user_question):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        new_db = FAISS.load_local(
            "faiss_index", embeddings, allow_dangerous_deserialization=True)

        docs = new_db.similarity_search(user_question)
        chain = Model.get_conversational_chain()

        response = chain.invoke(
            {"input_documents": docs, "question": user_question}, return_only_outputs=True)

        output_text = response["output_text"]
        return output_text

def main():
    question = input("Which document do you want to generate: ")
    print("Generating initially with random user's input")
    Simulations.user_satisfaction(question)

if __name__ == "__main__":
    main()
