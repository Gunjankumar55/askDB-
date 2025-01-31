from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import google.generativeai as genai
import pymysql
import json
from sqlalchemy import text, engine_from_config
import logging
import traceback
from decimal import Decimal
import re
import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure handlers if they don't exist
if not logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Initialize Gemini API
genai.configure(api_key=config('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
logger.info("✅ Gemini API initialized successfully!")

app = Flask(__name__)
CORS(app)

# Database configuration
try:
    db_url = config('DATABASE_URL')
    logger.info(f"Configuring database with URL: {db_url}")
    
    # Configure Flask-SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # This will log all SQL queries
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    
    # Test connection
    with app.app_context():
        # Test database connection
        result = db.session.execute(text('SELECT 1')).scalar()
        logger.info("✅ Database connection test successful!")
        
        # Test if tables exist
        result = db.session.execute(text("SHOW TABLES")).fetchall()
        logger.info(f"Found tables: {[r[0] for r in result]}")
        
except Exception as e:
    logger.error("❌ Database configuration failed!")
    logger.error(str(e))
    logger.error(traceback.format_exc())
    raise

# Database schema information for context
SCHEMA_INFO = """
Available tables and their structures:
1. customers
   - customer_id (INT, Primary Key, Auto Increment)
   - first_name, last_name (VARCHAR)
   - email (VARCHAR, Unique)
   - phone (VARCHAR)
   - registration_date (DATE)
   - last_activity (TIMESTAMP)

2. customer_addresses
   - address_id (INT, Primary Key, Auto Increment)
   - customer_id (INT, Foreign Key to customers)
   - address_type (ENUM: 'Home', 'Work', 'Billing', 'Other')
   - street_address (VARCHAR)
   - city (VARCHAR)
   - state (VARCHAR)
   - postal_code (VARCHAR)
   - country (VARCHAR)

3. credit_scores
   - score_id (INT, Primary Key, Auto Increment)
   - customer_id (INT, Foreign Key to customers)
   - credit_score (INT)
   - score_status (ENUM: 'Low', 'Medium', 'High')
   - last_updated (TIMESTAMP)

4. customer_transactions
   - transaction_id (INT, Primary Key, Auto Increment)
   - customer_id (INT, Foreign Key to customers)
   - transaction_date (DATE)
   - amount (DECIMAL)
   - transaction_type (ENUM: 'Credit', 'Debit')
   - description (VARCHAR)
   - category (ENUM: 'Salary', 'Investment', 'Purchase', 'Utility', 'Transfer', 'Other')

5. customer_loans
   - loan_id (INT, Primary Key, Auto Increment)
   - customer_id (INT, Foreign Key to customers)
   - principal_amount (DECIMAL)
   - interest_rate (DECIMAL)
   - start_date (DATE)
   - duration_months (INT)
   - monthly_payment (DECIMAL)
   - loan_status (ENUM: 'Active', 'Closed', 'Default')
"""

def get_relevant_schema(query):
    """Get relevant table schemas based on query context"""
    query_lower = query.lower()
    schema_parts = []
    
    # Add core tables that are almost always needed
    schema_parts.append("1. customers (customer_id, first_name, last_name, email, phone, registration_date)")
    
    # Add context-specific tables
    if any(word in query_lower for word in ['address', 'city', 'location', 'state', 'country']):
        schema_parts.append("2. customer_addresses (address_id, customer_id, address_type, street_address, city, state, postal_code, country)")
    
    if any(word in query_lower for word in ['credit', 'score', 'rating']):
        schema_parts.append("3. credit_scores (score_id, customer_id, credit_score, score_status)")
    
    if any(word in query_lower for word in ['transaction', 'payment', 'amount', 'debit', 'credit', 'purchase']):
        schema_parts.append("4. customer_transactions (transaction_id, customer_id, transaction_date, amount, transaction_type, category)")
    
    if any(word in query_lower for word in ['loan', 'borrow', 'interest', 'emi', 'payment']):
        schema_parts.append("5. customer_loans (loan_id, customer_id, principal_amount, interest_rate, start_date, duration_months, monthly_payment, loan_status)")
    
    # If no specific tables are matched, return all tables
    if len(schema_parts) <= 1:
        schema_parts = [
            "1. customers (customer_id, first_name, last_name, email, phone, registration_date)",
            "2. customer_addresses (address_id, customer_id, address_type, street_address, city, state, postal_code, country)",
            "3. credit_scores (score_id, customer_id, credit_score, score_status)",
            "4. customer_transactions (transaction_id, customer_id, transaction_date, amount, transaction_type, category)",
            "5. customer_loans (loan_id, customer_id, principal_amount, interest_rate, start_date, duration_months, monthly_payment, loan_status)"
        ]
    
    return "\n".join(schema_parts)

def get_sql_from_gemini(query):
    """Get SQL query from Gemini AI"""
    try:
        # Get relevant schema based on query context
        schema_info = get_relevant_schema(query)
        
        prompt = f"""
        You are an expert SQL database assistant specializing in banking operations. Your task is to generate optimized, secure MySQL queries based on user queries.

        ### Database Schema:
        {schema_info}

        ### Query Requirements:
        1. Generate clean, readable MySQL queries
        2. Always use proper table aliases:
           - customers as c
           - customer_addresses as ca
           - credit_scores as cs
           - customer_transactions as ct
           - customer_loans as cl
        3. Include all necessary JOINs with proper ON conditions
        4. Use appropriate columns in WHERE clauses
        5. Format dates as 'YYYY-MM-DD'
        6. Always quote string values with single quotes
        7. Use appropriate aggregations (COUNT, SUM, AVG) when needed
        8. DO NOT include the word 'sql' at the start of your query
        9. Use DISTINCT when selecting customer information to avoid duplicates from JOINs
        10. When joining with customer_addresses, use WHERE or GROUP BY to avoid duplicates

        ### Example Queries:
        1. For credit scores above 700:
        SELECT DISTINCT
            c.customer_id,
            c.first_name,
            c.last_name,
            cs.credit_score,
            cs.score_status
        FROM customers c
        JOIN credit_scores cs ON cs.customer_id = c.customer_id
        WHERE cs.credit_score > 700
        ORDER BY cs.credit_score DESC;

        2. For loan details with customer info:
        SELECT DISTINCT
            c.first_name,
            c.last_name,
            cl.principal_amount,
            cl.monthly_payment,
            cl.loan_status
        FROM customers c
        JOIN customer_loans cl ON cl.customer_id = c.customer_id
        WHERE cl.loan_status = 'Active';

        Natural language query: {query}
        
        Return only the SQL query, nothing else. Do not include the word 'sql' at the start.
        """
        
        # Generate SQL using Gemini
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # Basic safety checks
        sql_lower = sql_query.lower()
        if any(word in sql_lower for word in ['insert', 'update', 'delete', 'drop', 'truncate', 'alter']):
            raise ValueError("Only SELECT statements are allowed")
        
        if not sql_lower.startswith('select'):
            raise ValueError("Query must start with SELECT")
        
        # Clean up the query
        sql_query = sql_query.replace('`', '')  # Remove backticks
        sql_query = sql_query.replace('"', "'")  # Replace double quotes with single quotes
        sql_query = sql_query.replace('\n', ' ')  # Remove newlines
        sql_query = ' '.join(sql_query.split())  # Remove extra spaces
        
        # Remove 'sql' prefix if present
        if sql_query.lower().startswith('sql'):
            sql_query = sql_query[3:].strip()
        
        logger.info(f"Generated SQL query: {sql_query}")
        return sql_query
        
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValueError(f"Error generating SQL query: {str(e)}")

def determine_query_type(sql):
    """Determine the type of SQL query"""
    sql = sql.strip().lower()
    if sql.startswith('select'):
        return 'select'
    elif sql.startswith('insert'):
        return 'insert'
    elif sql.startswith('update'):
        return 'update'
    elif sql.startswith('delete'):
        return 'delete'
    return 'unknown'

def is_safe_query(sql):
    """Validate if the query is safe to execute"""
    # Add your security checks here
    unsafe_keywords = ['drop', 'truncate', 'alter', 'grant', 'revoke']
    sql_lower = sql.lower()
    return not any(keyword in sql_lower for keyword in unsafe_keywords)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query')
def query_page():
    return render_template('query.html')

@app.route('/database')
def database_page():
    # Get actual database stats
    try:
        with db.engine.connect() as conn:
            # Get total customers
            customer_count = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
            
            # Get total transactions
            transaction_count = conn.execute(text("SELECT COUNT(*) FROM customer_transactions")).scalar()
            
            # Get active loans
            active_loans = conn.execute(text("SELECT COUNT(*) FROM customer_loans WHERE loan_status = 'Active'")).scalar()
            
            # Get total tables
            table_count = 5  # We know we have 5 tables
            
            return render_template('database.html', 
                                stats={
                                    'customers': customer_count,
                                    'transactions': transaction_count,
                                    'active_loans': active_loans,
                                    'tables': table_count
                                })
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return render_template('database.html', 
                            stats={
                                'customers': 50,
                                'transactions': 100,
                                'active_loans': 30,
                                'tables': 5
                            })

@app.route('/test-db')
def test_db_counts():
    try:
        # Test basic customer query
        with db.engine.connect() as conn:
            # Test customers
            result = conn.execute(text("SELECT COUNT(*) FROM customers"))
            customer_count = result.scalar()
            
            # Test Mumbai customers
            result = conn.execute(text("SELECT COUNT(*) FROM customer_addresses WHERE city = 'Mumbai'"))
            mumbai_count = result.scalar()
            
            # Test phone numbers
            result = conn.execute(text("SELECT COUNT(*) FROM customers WHERE phone LIKE '98%'"))
            phone_count = result.scalar()
            
            return jsonify({
                'success': True,
                'total_customers': customer_count,
                'mumbai_customers': mumbai_count,
                'customers_with_98': phone_count
            })
            
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/query', methods=['POST'])
def query():
    try:
        data = request.json
        user_query = data.get('query', '')
        logger.info(f"Received user query: {user_query}")

        # Get SQL from Gemini API
        sql_query = get_sql_from_gemini(user_query)
        logger.info(f"Generated SQL query: {sql_query}")
        
        # Execute the query
        with db.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            if not rows:
                logger.warning("Query returned no results")
                return jsonify({
                    'success': True,
                    'sql_query': sql_query,
                    'data': []
                })
            
            # Get column names from keys
            columns = list(rows[0]._mapping.keys())
            logger.info(f"Columns in result: {columns}")
            
            # Convert rows to list of dicts
            data = []
            for row in rows:
                # Convert any non-serializable objects to strings
                processed_row = {}
                for idx, col in enumerate(columns):
                    value = row[idx]
                    if isinstance(value, datetime.date):
                        processed_row[col] = value.isoformat()
                    elif isinstance(value, Decimal):
                        processed_row[col] = float(value)
                    else:
                        processed_row[col] = value
                data.append(processed_row)
            
            logger.info(f"Query returned {len(data)} results")
            
            return jsonify({
                'success': True,
                'sql_query': sql_query,
                'data': data
            })
            
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'sql_query': sql_query if 'sql_query' in locals() else None
        }), 500

if __name__ == '__main__':
    # Test SQLAlchemy connection before starting
    with app.app_context():
        try:
            result = db.session.execute(text('SELECT 1')).scalar()
            logger.debug("SQLAlchemy connection test successful!")
        except Exception as e:
            logger.error(f"SQLAlchemy connection test failed: {str(e)}")
            raise
    
    app.run(debug=True)
