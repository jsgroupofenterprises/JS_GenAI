import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask, request, jsonify
from RDKAssistant_Class import RDKAssistant
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def lambda_handler(event, context):
    # Initialize assistant
    assistant = RDKAssistant(
        code_base_path=os.getenv('CODE_BASE_PATH'),
        gemini_api_key=os.getenv('GEMINI_API_KEY')
    )
    assistant.initialize()

    # Parse the incoming request
    query = event.get('body', {})
    if isinstance(query, str):
        import json
        query = json.loads(query)
    
    # Handle the query
    response = assistant.handle_user_query(query.get('query', ''))
    
    # Return response in Netlify serverless function format
    return {
        'statusCode': 200,
        'body': json.dumps({'response': response}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        }
    }