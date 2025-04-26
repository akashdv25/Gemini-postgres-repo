from flask import Flask, request, jsonify, render_template
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

app = Flask(__name__, 
    template_folder='templates',    
    static_folder='static'         
)

# PostgreSQL connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    """Create a database connection"""
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

# Create tables if they don't exist
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    except Exception as e:
        logging.error(f"Error creating table: {e}")
    finally:
        cur.close()
        conn.close()

# Get API key from environment variables
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')

# Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    convert_system_message_to_human=True,
    max_tokens=None,
    top_p=0.8,
    top_k=40,
    max_retries=2
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Log the incoming message
        logging.info(f"Received message: {user_message}")

        # Create the messages list for the LLM - simplified format
        messages = [
            ("human", user_message)
        ]

        # Get response from LLM
        response = llm.invoke(messages)
        bot_response = response.content
        
        # Log the response
        logging.info(f"LLM response: {bot_response}")

        # Save to database
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO chat_history (user_message, bot_response)
                VALUES (%s, %s)
                RETURNING id, timestamp;
            """, (user_message, bot_response))
            
            result = cur.fetchone()
            chat_id, timestamp = result
            conn.commit()
            
            return jsonify({
                'response': bot_response,
                'status': 'success',
                'timestamp': timestamp.isoformat()
            })
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        # Log the error
        logging.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)  # This will return results as dictionaries
        
        cur.execute("""
            SELECT id, user_message, bot_response, timestamp 
            FROM chat_history 
            ORDER BY timestamp DESC;
        """)
        
        history = cur.fetchall()
        
        # Convert datetime objects to ISO format strings
        for chat in history:
            chat['timestamp'] = chat['timestamp'].isoformat()
        
        return jsonify({
            'history': history,
            'status': 'success'
        })
    except Exception as e:
        logging.error(f"Error fetching chat history: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    init_db()  # Initialize database tables
    app.run(debug=True) 