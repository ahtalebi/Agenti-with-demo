# Agenti: AI Agent App with Demo Interface

This project is a full-stack AI agent web application that allows users to interact with an intelligent system capable of retrieving, analyzing, and responding to queries based on domain-specific documents and stored data. It includes an admin interface, session tracking, token-based access control, and a simple frontend for demo purposes.

## 🚀 Features

- 🔐 **Admin Login** for secure access to protected areas  
- 🤖 **AI Agent API** with RAG (Retrieval-Augmented Generation) using local data  
- 🧠 **Token-based authentication** and usage tracking  
- 💾 **ChromaDB-backed storage** for document embeddings and semantic search  
- 📊 **Interaction logging** for monitoring usage patterns  
- 🌐 **Static frontend demo** in HTML/JavaScript  
- 🧪 **API Test Page** for trying out agent responses in the browser  

## 📁 Project Structure

app.py # Flask app entry point
main.py # Alternate app runner (legacy/test)
src/
├── routes.py # API and HTML routes
├── rag_engine.py # Core RAG logic
├── models.py # Data models and schema
├── admin_auth.py # Admin login and session handling
├── config.py # Environment/config setup
├── interaction_tracker.py # Logs queries and responses
├── token_store.py # Token-based access control
static/
├── index.html, app.js, demo.html, api-test.html
protected_templates/
├── admin.html # Admin-only UI
db/
├── chroma_db/ # Vector database (excluded from Git)
├── tokens.json # API token data
├── interactions.json # User interaction logs
data/
├── file.tex # Sample document
├── insurance_regulations.txt # Domain-specific source
.env # API keys and secrets (excluded from Git)
requirements.txt # Python dependencies

markdown
Copy
Edit

## 🌐 API Endpoints

| Route         | Method | Description                           |
|---------------|--------|---------------------------------------|
| `/`           | GET    | Landing page                          |
| `/ask`        | POST   | Submit a question to the AI agent     |
| `/admin`      | GET    | Admin dashboard (login required)      |
| `/api-test`   | GET    | Test the API via browser UI           |
| `/static/*`   | GET    | Serves static frontend files          |

## 🛡️ Admin & Token Auth

- **Admin login** requires credentials stored in environment variables or a config file.
- **Token-based auth**: Clients must provide a token to access the `/ask` endpoint.
- **Logs**: All interactions are saved in `db/interactions.json`.

## 🧪 How to Run Locally

1. **Clone the repo**
   ```bash
   git clone git@github.com:ahtalebi/Agenti-with-demo.git
   cd Agenti-with-demo
Create and activate virtual environment

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Set environment variables
Create a .env file:

ini
Copy
Edit
OPENAI_API_KEY=your-api-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=securepassword
Run the app

bash
Copy
Edit
python app.py
Visit http://localhost:5000 in your browser.

🔒 .gitignore
The following are excluded from Git:

venv/

__pycache__/

.env

db/chroma_db/ (local vector DB)

data/ (document sources)

📄 License
This project is for research/demo purposes and does not yet include a formal license.

🙋‍♂️ Author
Created by @ahtalebi
