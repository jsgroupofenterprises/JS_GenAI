# netlify/functions/chat.py
import json
from RDKAssistant_Class import RDKAssistant

# Initialize the assistant (you'll need to handle API key securely)
assistant = RDKAssistant(
    code_base_path="/path/to/code/base",  # This will need to be adjusted
    gemini_api_key="your_api_key_from_netlify_environment"
)
assistant.initialize()

def handler(event, context):
    try:
        # Parse the incoming request body
        body = json.loads(event['body'])
        query = body.get('query', '')

        # Process the query
        response = assistant.handle_user_query(query)

        # Return the response
        return {
            'statusCode': 200,
            'body': json.dumps({'response': response}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }