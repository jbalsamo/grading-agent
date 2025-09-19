# Azure AI Agent Jupyter Notebook

A complete setup for building AI agents using Azure OpenAI and LangChain in Jupyter notebooks.

## 🚀 Quick Start

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Azure OpenAI

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` with your Azure OpenAI credentials:
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI resource endpoint
   - `AZURE_OPENAI_API_KEY`: Your API key
   - `AZURE_OPENAI_CHAT_DEPLOYMENT`: Your GPT model deployment name
   - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Your embedding model deployment name (optional)

### 4. Start Jupyter

```bash
jupyter lab
# or
jupyter notebook
```

### 5. Open the Notebook

Open `azure_agent_notebook.ipynb` and run the cells to start building your AI agent!

## 📋 What's Included

### Core Components

- **Virtual Environment**: Python 3.13 environment in `.venv/`
- **Jupyter Setup**: JupyterLab, notebook, and ipywidgets
- **Azure AI Integration**: Azure OpenAI and Cognitive Services
- **Agent Framework**: LangChain with LangGraph for advanced agents
- **Interactive UI**: ipywidgets for chat interfaces

### Key Libraries

#### AI & Agents
- **LangChain**: The best framework for building AI agents in Python
- **LangGraph**: For complex, stateful agent workflows
- **Azure OpenAI**: Direct integration with Azure AI services
- **OpenAI**: Fallback for direct OpenAI API usage

#### Data & Analysis
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib/seaborn**: Data visualization
- **scikit-learn**: Machine learning utilities

#### Utilities
- **python-dotenv**: Environment variable management
- **httpx/aiohttp**: Async HTTP clients
- **rich**: Beautiful terminal output
- **pydantic**: Data validation and settings

## 🤖 Why LangChain?

LangChain is recommended as the best agent framework because:

1. **Mature Ecosystem**: Extensive documentation and community support
2. **Azure Integration**: Native Azure OpenAI support
3. **Tool Integration**: Easy to add custom tools and external APIs
4. **Memory Management**: Built-in conversation memory and context handling
5. **Agent Types**: Multiple agent architectures (ReAct, OpenAI Functions, etc.)
6. **Production Ready**: Used by thousands of production applications

## 🛠️ Agent Features

The notebook includes:

- **Azure OpenAI Chat**: Direct integration with your Azure deployments
- **Custom Tools**: Calculator, time, and web search tools
- **Interactive Chat**: Widget-based chat interface
- **Memory**: Conversation history management
- **Error Handling**: Robust error handling and validation

## 📁 Project Structure

```
.
├── .venv/                          # Python virtual environment
├── .env                           # Your Azure configuration (keep private!)
├── .env.template                  # Template for environment variables
├── requirements.txt               # Python dependencies
├── azure_agent_notebook.ipynb    # Main Jupyter notebook
└── README.md                      # This file
```

## 🔧 Configuration Options

### Azure OpenAI Models

Recommended deployments:
- **Chat**: `gpt-4o`, `gpt-4`, or `gpt-35-turbo`
- **Embeddings**: `text-embedding-ada-002` or `text-embedding-3-small`

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Your Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Yes | Your Azure OpenAI API key |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Yes | Name of your chat model deployment |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | No | Name of your embedding model deployment |
| `LANGCHAIN_TRACING_V2` | No | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | No | LangSmith API key for monitoring |

## 🚨 Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and rotate them regularly
- Use Azure Key Vault for production deployments
- Consider using managed identities in Azure environments

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated the virtual environment and installed requirements
2. **Azure Connection Failed**: Check your endpoint URL and API key in `.env`
3. **Model Not Found**: Verify your deployment names match what's configured in Azure
4. **Rate Limits**: Azure OpenAI has rate limits; consider implementing retry logic

### Getting Help

- Check the [LangChain documentation](https://python.langchain.com/)
- Review [Azure OpenAI documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- Open an issue if you encounter problems with this setup

## 🎯 Next Steps

1. **Customize Tools**: Add your own custom tools for specific tasks
2. **Add Memory**: Implement persistent conversation memory
3. **Create Workflows**: Use LangGraph for complex multi-step processes
4. **Deploy**: Move to production with Azure Container Apps or Functions
5. **Monitor**: Set up LangSmith for agent performance monitoring

Happy coding! 🎉
