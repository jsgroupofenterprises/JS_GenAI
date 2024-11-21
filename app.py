import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from RDKAssistant_Class import RDKAssistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def handler(event, context):
    try:
        # Detailed logging
        print(f"Received event: {event}")
        print(f"Environment variables: CODE_BASE_PATH={os.getenv('CODE_BASE_PATH')}")
        
        # Initialize assistant
        assistant = RDKAssistant(
            code_base_path=os.getenv('CODE_BASE_PATH'),
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        assistant.initialize()

        # Parse the incoming request
        body = json.loads(event['body'])
        query = body.get('query', '')
        print(f"Received query: {query}")
    
        # Handle the query
        response = assistant.handle_user_query(query)
        print(f"Generated response: {response}")
    
        return {
            'statusCode': 200,
            'body': json.dumps({'response': response}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            }
        }
    except Exception as e:
        # More detailed error logging
        import traceback
        print(f"Full error traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        }