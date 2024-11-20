from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Add this import
from RDKAssistant_Class import RDKAssistant
app = Flask(__name__)
CORS(app)  # Enable CORS

assistant = RDKAssistant(
    code_base_path=r"C:\Users\39629\Downloads\rdkb_24q1\rdkb_24q1\rdkb\components\opensource\ccsp\OneWifi\source\dml\dml_webconfig",
    gemini_api_key="AIzaSyAxrAdNHgOau0STj06M17yreQHIOYZP-Zc"
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

if __name__ == '__main__':
    app.run(debug=True)