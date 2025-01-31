# Project Upgrade Plan: Text-to-SQL Enhancement

## **Objective**
Upgrade the existing Text-to-SQL project by:
1. Replacing CSV uploads with direct SQL database connections.
2. Migrating from Streamlit to Flask to enhance the frontend using HTML, CSS, and JavaScript.

---

## **Proposed Technology Stack**

### **Backend:**
- **Flask:** Web framework for building RESTful APIs.
- **SQLAlchemy:** ORM for managing database connections.
- **MySQL/PostgreSQL/SQLite:** Database options for structured data storage.
- **Google Generative AI API (Gemini):** AI model for converting natural language to SQL.
- **python-dotenv:** For managing environment variables securely.

### **Frontend:**
- **HTML5:** Structuring the web pages.
- **CSS3:** Styling and layout.
- **JavaScript (Vanilla/React.js):** Interactive UI and dynamic data handling.
- **Bootstrap/Tailwind CSS:** Responsive design.

### **Other Tools:**
- **Postman:** API testing.
- **Gunicorn:** Deployment server for Flask.
- **Docker (Optional):** Containerization for deployment.
- **GitHub:** Version control and collaboration.

---

## **Project Workflow**

1. **Database Setup:**
    - Choose and set up a relational database (MySQL/PostgreSQL/SQLite).
    - Design tables for storing and querying data.
    - Configure SQLAlchemy to connect Flask with the database.

2. **Backend Development:**
    - Set up Flask project structure.
    - Create API routes for handling:
      - User authentication (optional)
      - Data querying
      - Query execution
    - Implement AI query processing with Google Gemini.

3. **Frontend Development:**
    - Design HTML/CSS-based web pages.
    - Use JavaScript to interact with Flask APIs.
    - Implement AJAX calls for dynamic interactions.

4. **Integration and Testing:**
    - Connect the frontend with the backend API.
    - Test API responses and frontend interactions.
    - Validate SQL query execution and error handling.

5. **Deployment:**
    - Configure production environment.
    - Use Gunicorn for serving the Flask app.
    - Deploy using cloud platforms (Heroku, AWS, or DigitalOcean).

---

## **Step-by-Step Implementation Plan**

### **Step 1: Set Up the Flask Project**
1. Install dependencies:
    ```bash
    pip install flask flask_sqlalchemy python-dotenv google-generativeai
    ```
2. Create project structure:
    ```
    text-to-sql-flask/
    |-- app/
    |   |-- __init__.py
    |   |-- routes.py
    |   |-- models.py
    |   |-- services.py
    |-- templates/
    |-- static/
    |-- .env
    |-- config.py
    |-- run.py
    ```
3. Configure Flask in `app/__init__.py`.

### **Step 2: Database Connection**
1. Configure database URI in `.env`:
    ```
    DATABASE_URL=mysql+pymysql://user:password@localhost/db_name
    ```
2. Define SQLAlchemy models in `app/models.py`.

### **Step 3: Backend API Development**
1. Define routes for handling user input and AI processing.
2. Write functions to convert text to SQL and execute queries.

### **Step 4: Frontend Development**
1. Create HTML templates in `templates/`.
2. Add CSS and JS in `static/`.
3. Implement AJAX calls to Flask API.

### **Step 5: Testing and Debugging**
1. Use Postman to test API routes.
2. Perform unit testing on database queries.

### **Step 6: Deployment**
1. Configure Gunicorn for Flask.
2. Deploy on a cloud platform.

---

## **Expected Outcome**
- A fully functional Flask-based web application that allows users to query databases via natural language input.
- Improved UI/UX with HTML, CSS, and JavaScript.
- Enhanced performance with direct SQL connections instead of CSV uploads.

---

## **Next Steps**
1. Set up the Flask project structure.
2. Establish database connectivity.
3. Implement Flask API routes.
4. Develop frontend templates.
5. Deploy and optimize the application.

---

## **Comprehensive Project Documentation**

### **Project Overview**
A Flask-based application that converts natural language to SQL queries using Google's Gemini AI, with a modern web interface and MySQL database backend.

### **Development Process**

#### 1. Initial Setup
- Set up Flask application structure
- Created virtual environment
- Installed necessary dependencies:
  - Flask for web framework
  - Flask-SQLAlchemy for database ORM
  - python-dotenv for environment variables
  - PyMySQL for MySQL connection
  - google-generativeai for Gemini AI integration

#### 2. Database Design
- Created MySQL database schema
- Designed four main tables:
  1. customers (personal info, contact details)
  2. bank_branches (branch info, location)
  3. accounts (account details, balances)
  4. transactions (transaction history)
- Implemented foreign key relationships
- Added sample data for testing

#### 3. Backend Development
- Implemented database connection with SQLAlchemy
- Created routes for:
  - Main page (/)
  - Database test (/test-db)
  - Query processing (/api/query)
- Added error handling and logging
- Implemented natural language to SQL conversion using Gemini AI
- Added query safety checks and cleaning

#### 4. Frontend Development
- Created clean, minimalist interface
- Added query input form
- Implemented results display
- Added error message handling
- Made UI responsive

#### 5. Integration with Gemini AI
- Set up Gemini AI configuration
- Created prompt engineering for SQL conversion
- Added context about database schema
- Implemented query cleaning and safety checks
- Added support for various query types

#### 6. Debugging & Optimization
- Fixed MySQL connection issues
- Improved error handling
- Enhanced SQL query generation
- Added query cleaning for MySQL compatibility
- Implemented better logging

#### 7. Security Implementation
- Added environment variable configuration
- Implemented SQL injection prevention
- Limited queries to SELECT statements only
- Added database connection error handling
- Protected sensitive credentials

### **Technical Implementation Details**

#### Database Connection
```python
app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

#### Natural Language Processing
```python
def natural_to_sql(query):
    prompt = f"""
    Given the following database schema:
    {SCHEMA_INFO}
    Convert this natural language query to SQL...
    """
    response = model.generate_content(prompt)
    return clean_sql_query(response.text)
```

#### Query Processing
- Input validation
- Query generation using Gemini AI
- SQL query cleaning and safety checks
- Error handling and logging
- Result formatting and JSON response

#### Environment Configuration
```
DATABASE_URL=mysql+pymysql://root:admin5@127.0.0.1:3306/sql_chatbot
GEMINI_API_KEY=your_api_key
FLASK_ENV=development
```

### **Challenges Faced & Solutions**

1. **MySQL Connection Issues**
   - Problem: Access denied errors
   - Solution: Proper credential configuration and connection string formatting

2. **SQL Query Generation**
   - Problem: Incompatible SQL syntax
   - Solution: Added query cleaning and formatting

3. **Database Setup**
   - Problem: Table creation and sample data
   - Solution: Created comprehensive setup script

4. **Error Handling**
   - Problem: Unclear error messages
   - Solution: Added detailed logging and user-friendly errors

### **Future Improvements**

1. **Query Enhancement**
   - Query history
   - Query suggestions
   - Complex joins support

2. **UI Improvements**
   - Dark/Light mode
   - Export results
   - Visual query builder

3. **Security Features**
   - User authentication
   - Role-based access
   - Query restrictions

4. **Advanced Features**
   - Query templates
   - Data visualization
   - Scheduled queries

### **Learning Outcomes**

1. Integration of AI with traditional databases
2. Proper error handling in Flask applications
3. Secure database connection management
4. Effective prompt engineering for AI
5. Clean code organization and documentation

### **Resources Used**

1. Flask Documentation
2. SQLAlchemy Documentation
3. Google Gemini AI Documentation
4. MySQL Documentation
5. Python Best Practices Guide
