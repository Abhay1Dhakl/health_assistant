# AI/ML Engineer Assignment

A medical information system with Model Context Protocol (MCP) servers for document-based question answering using azithromycin pharmaceutical documents.

## Features

- **Multi-document Medical Knowledge Base**: Access to 3 specialized medical documents
  - Document1: Azithromycin StatPearls/NCBI (comprehensive drug information)
  - Document2: Azithromycin clinical data and research findings
  - Document3: JCLA medical journal article (clinical laboratory analysis)
- **Dynamic Tool Selection**: AI automatically selects the most relevant document(s) based on user queries
- **FastAPI Backend**: RESTful API for medical information queries
- **Interactive Web UI**: User-friendly web interface for easy interaction
- **MCP Integration**: Model Context Protocol for document retrieval
- **PDF Processing**: Automated PDF to JSON conversion for document indexing
- **Real-time Responses**: Live chat interface with streaming responses
- **Citation Management**: Automatic source attribution and reference formatting

## Prerequisites

- Python 3.10 or higher
- Git
- UV package manager (recommended) or pip
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation

### Option 1: Using UV (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abhay1Dhakl/health_assistant.git
   cd AI_ML_Engineer_Assignment
   ```

2. **Create virtual environment with UV**
   ```bash
   uv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   uv sync
   ```


### Option 2: Using pip

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abhay1Dhakl/health_assistant.git
   cd AI_ML_Engineer_Assignment
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

## Configuration

1. **Create environment file**
   ```bash
   # Create .env file in the root directory
   touch .env
   ```

2. **Add your API keys to .env**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1/
   ```

3. **Configure MCP server** (if needed)
   - Update `health_agent/mcp_server_config.json` with your MCP server settings

## Document Processing

### Convert PDF documents to JSON (if needed)

1. **Navigate to the MCP server directory**
   ```bash
   cd mcp_server1
   ```

2. **Run the data conversion script**
   ```bash
   python data_conversion.py
   ```

This will process the PDF documents and create JSON files for the MCP servers.

## Running the Application

### Quick Start (All Services)

To start all services at once, open 3 separate terminal windows:

**Terminal 1 - MCP Server:**
```bash
cd mcp_server
python doc_server.py
```

**Terminal 2 - Backend API:**
```bash
cd health_agent
python main.py
```

**Terminal 3 - Frontend UI:**
```bash
cd health_agent_ui
python -m http.server 8000
```

### Step-by-Step Setup

### 1. Start the MCP Server

First, navigate to the MCP server directory and start the document server:

```bash
cd mcp_server
python doc_server.py
```

The MCP server will start on `http://localhost:8001` with SSE transport.

### 2. Start the Health Agent API

Open a new terminal and start the backend:

```bash
cd health_agent
python main.py
```

The API will start on `http://localhost:8080`

### 3. Start the Web UI

Open a third terminal and start the frontend:

```bash
cd health_agent_ui
python -m http.server 8000
```

The UI will start on `http://localhost:8000`

### 4. Access the Application

- **Web Interface**: Open `http://localhost:8000` in your browser
- **API Documentation**: Visit `http://localhost:8080/docs` for interactive API docs
- **Health Check**: `http://localhost:8080/health` to verify API status

### Alternative UI Commands

If `python -m http.server 8000` doesn't work, try these alternatives:

```bash
# For different port
python -m http.server 8080

# For specific IP binding
python -m http.server 8000 --bind 127.0.0.1

# For Python 2 (if needed)
python -m SimpleHTTPServer 8000

# Using Node.js if available
npx http-server -p 8000
```

## API Usage

### Web Interface

The easiest way to interact with the system is through the web UI:

1. Open your browser and go to `http://localhost:8000`
2. Type your medical question in the chat interface
3. View the AI response with proper citations and references
4. Browse previous conversations in the chat history

### REST API

#### Query Endpoint

**POST** `/query`

**Request Body:**
```json
{
  "user_query": "What are the side effects of azithromycin?"
}
```

**Response:**
```json
{
  "response": "Azithromycin side effects include gastrointestinal disturbances, cardiac arrhythmias, and hepatotoxicity (StatPearls, Document1).\n\n**References:**\n1. Document1: Azithromycin StatPearls/NCBI Documentation"
}
```

### Example Queries

1. **Drug Information** (triggers document1):
   ```json
   {"user_query": "What is the mechanism of action of azithromycin?"}
   ```

2. **Clinical Data** (triggers document2):
   ```json
   {"user_query": "What are the recommended dosage guidelines for azithromycin?"}
   ```

3. **Laboratory Analysis** (triggers document3):
   ```json
   {"user_query": "What laboratory parameters should be monitored during azithromycin therapy?"}
   ```

4. **Multi-source Query**:
   ```json
   {"user_query": "What are the complete prescribing guidelines for azithromycin including dosage, contraindications, and monitoring requirements?"}
   ```

## Testing

### Sample Questions

For a comprehensive list of sample questions you can ask, see the `sample_questions.txt` file in the project root. This file contains:
- Document-specific questions for each of the 3 medical documents
- Multi-document queries that trigger multiple sources
- Tips for asking effective questions
- Question categories and examples

### Web UI Testing

1. **Open the application**: Navigate to `http://localhost:8000`
2. **Test basic functionality**: Ask "What is azithromycin?"
3. **Test document selection**: Try specific queries to trigger different documents
4. **Verify citations**: Check that responses include proper source citations
5. **Test multi-document queries**: Ask comprehensive questions requiring multiple sources
6. **Use sample questions**: Refer to `sample_questions.txt` for tested question examples

### API Testing

#### Using curl
```bash
curl -X POST "http://localhost:8080/query" \
     -H "Content-Type: application/json" \
     -d '{"user_query": "What are the contraindications of azithromycin?"}'
```

#### Using Python requests
```python
import requests

response = requests.post(
    "http://localhost:8080/query",
    json={"user_query": "What is the pharmacokinetics of azithromycin?"}
)
print(response.json())
```

#### Testing Different Document Sources

```bash
# Test Document1 (StatPearls) - Basic drug information
curl -X POST "http://localhost:8080/query" \
     -H "Content-Type: application/json" \
     -d '{"user_query": "What is the mechanism of action of azithromycin?"}'

# Test Document2 (Clinical Data) - Prescribing information
curl -X POST "http://localhost:8080/query" \
     -H "Content-Type: application/json" \
     -d '{"user_query": "What are the dosage guidelines for azithromycin?"}'

# Test Document3 (JCLA) - Laboratory analysis
curl -X POST "http://localhost:8080/query" \
     -H "Content-Type: application/json" \
     -d '{"user_query": "What laboratory parameters should be monitored?"}'
```

## Troubleshooting

### Common Issues

1. **MCP Connection Error**
   - Ensure MCP server is running: `python mcp_server/doc_server.py`
   - Check if port 8001 is available
   - Verify `mcp_server_config.json` configuration
   - Check network connectivity

2. **Missing API Key**
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - Check API key permissions and quota
   - Verify `OPENAI_BASE_URL` is correct

3. **Port Already in Use**
   - Backend (8080): `netstat -ano | findstr :8080` on Windows
   - Frontend (8000): `netstat -ano | findstr :8000` on Windows
   - MCP Server (8001): `netstat -ano | findstr :8001` on Windows
   - Kill the process or change the port in respective config files

4. **UI Not Loading**
   - Check if Python is installed: `python --version`
   - Verify static files are in the ui directory
   - Check browser console for JavaScript errors
   - Ensure backend API is running and accessible
   - Try a different port: `python -m http.server 8080`

5. **CORS Issues**
   - Verify CORS settings in `main.py`
   - Check if frontend URL is in `allow_origins`
   - Use browser dev tools to inspect network requests

6. **Package Installation Issues**
   - Ensure Python 3.10+ is installed
   - Try upgrading pip: `pip install --upgrade pip`
   - For UV issues, reinstall UV: `pip install --upgrade uv`
   - For UI issues, ensure static files are properly placed in ui directory

### Debug Mode

#### Backend Debug
```bash
cd health_agent
python main.py --debug
```

#### Frontend Debug
```bash
cd ui
python -m http.server 8000 --bind 127.0.0.1
```

### Logs and Monitoring

- **Backend logs**: Check terminal output where `main.py` is running
- **MCP Server logs**: Check terminal output where `doc_server.py` is running
- **Frontend logs**: Open browser developer tools (F12) → Console tab
- **Network requests**: Browser developer tools → Network tab


## Design Documentation

For detailed information about design choices, libraries used, and how hallucinations are addressed, see `DESIGN_NOTES.md`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please:
1. Check the troubleshooting section above
2. Review the API documentation
3. Create an issue in the repository