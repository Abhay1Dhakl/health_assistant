# AI/ML Engineer Assignment

A medical information system with Model Context Protocol (MCP) servers for document-based question answering using azithromycin pharmaceutical documents.

## Features

- **Multi-document Medical Knowledge Base**: Access to 3 specialized medical documents
  - Document1: Azithromycin StatPearls/NCBI (comprehensive drug information)
  - Document2: Azithromycin clinical data and research findings
  - Document3: JCLA medical journal article (clinical laboratory analysis)
- **Dynamic Tool Selection**: AI automatically selects the most relevant document(s) based on user queries
- **FastAPI Backend**: RESTful API for medical information queries
- **MCP Integration**: Model Context Protocol for document retrieval
- **PDF Processing**: Automated PDF to JSON conversion for document indexing

## Prerequisites

- Python 3.10 or higher
- Git
- UV package manager (recommended) or pip

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

### 1. Start the MCP Server (if running locally)

First, ensure your MCP server is running on the configured port (usually 8081).

### 2. Start the Health Agent API

```bash
cd health_agent
python main.py
```

The API will start on `http://localhost:8080`

## API Usage

### Query Endpoint

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
  "response": "Based on StatPearls documentation, azithromycin side effects include..."
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

## 🧪 Testing

### Using curl
```bash
curl -X POST "http://localhost:8080/query" \
     -H "Content-Type: application/json" \
     -d '{"user_query": "What are the contraindications of azithromycin?"}'
```

### Using Python requests
```python
import requests

response = requests.post(
    "http://localhost:8080/query",
    json={"user_query": "What is the pharmacokinetics of azithromycin?"}
)
print(response.json())
```

## Troubleshooting

### Common Issues

1. **MCP Connection Error**
   - Ensure MCP server is running on the correct port
   - Check `mcp_server_config.json` configuration
   - Verify network connectivity

2. **Missing API Key**
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - Check API key permissions and quota

3. **Port Already in Use**
   - Check if another process is using port 8080
   - Use `netstat -ano | findstr :8080` on Windows
   - Kill the process or change the port in `main.py`

4. **Package Installation Issues**
   - Ensure Python 3.10+ is installed
   - Try upgrading pip: `pip install --upgrade pip`
   - For UV issues, reinstall UV: `pip install --upgrade uv`

### Debug Mode

To run with debug information:
```bash
cd health_agent
python main.py --debug
```

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
