# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS  # Add this import
# from RDKAssistant_Class import RDKAssistant
# import os
# app = Flask(__name__)
# CORS(app)  # Enable CORS

# assistant = RDKAssistant(
#     code_base_path=os.getenv('CODE_BASE_PATH'),
#     gemini_api_key=os.getenv('GEMINI_API_KEY')
# )
# assistant.initialize()


# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/chat', methods=['POST'])
# def chat():
#     query = request.json['query']
#     response = assistant.handle_user_query(query)
#     return jsonify({'response': response})

# if __name__ == '__main__':
#     app.run(debug=True)
#====================================== DEPLOYMENT ==================
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from RDKAssistant_Class import RDKAssistant
import os
from dotenv import load_dotenv
import serverless_wsgi

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize assistant with environment variables
assistant = RDKAssistant(
    code_base_path=os.getenv('CODE_BASE_PATH'),
    gemini_api_key=os.getenv('GEMINI_API_KEY')
)
assistant.initialize()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    query = request.json['query']
    response = assistant.handle_user_query(query)
    return jsonify({'response': response})

# Serverless handler for Netlify
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)