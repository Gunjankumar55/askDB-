# Text-to-SQL Chatbot

A Flask-based application that converts natural language queries to SQL using Google's Gemini AI.

## Prerequisites

1. Python 3.8 or higher
2. MySQL Server and MySQL Workbench
3. Google Gemini API key

## Setup Instructions

1. **Clone/Download the Project**
   - Download and extract the project folder

2. **Set Up Python Environment**
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set Up MySQL Database**
   - Install MySQL Server and MySQL Workbench
   - Open MySQL Workbench
   - Create a new connection if you don't have one
   - Use the following credentials:
     - Username: root
     - Password: admin5
     - Host: 127.0.0.1
     - Port: 3306
   - Open a new query tab
   - Copy and paste the contents of `database_setup.sql`
   - Execute the script (lightning bolt icon)

4. **Configure Environment Variables**
   - Create a copy of `.env.example` and rename it to `.env`
   - Update the following variables:
     ```
     DATABASE_URL=mysql+pymysql://root:admin5@127.0.0.1:3306/sql_chatbot
     GEMINI_API_KEY=your_gemini_api_key_here
     FLASK_ENV=development
     FLASK_APP=app.py
     ```
   - Replace `your_gemini_api_key_here` with your actual Gemini API key

5. **Run the Application**
   ```bash
   # Make sure your virtual environment is activated
   python app.py
   ```

6. **Access the Application**
   - Open a web browser
   - Go to: http://localhost:5000
   - Test the connection at: http://localhost:5000/test-db

## Example Queries

Try these natural language queries:
- "Show me all customers"
- "List all bank branches"
- "Show me customers from Mumbai"
- "List all accounts with balance more than 50000"

## Troubleshooting

1. **Database Connection Issues**
   - Verify MySQL is running
   - Check credentials in `.env` file
   - Ensure database and tables are created

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Make sure virtual environment is activated

3. **API Key Issues**
   - Verify Gemini API key in `.env`
   - Check for any spaces/typos

## Support

For any issues or questions, please:
1. Check the troubleshooting section
2. Verify all setup steps are completed
3. Ensure MySQL service is running

## License

MIT License - Feel free to use and modify!
