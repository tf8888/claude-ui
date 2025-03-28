## Claude UI
A simple and intuitive web interface for interacting with Anthropic's Claude AI models. This application allows you to chat with Claude, upload documents for analysis, and maintain conversation history.

## Features
- 💬 Chat interface with conversation history
- 📄 Document upload support (PDFs, images, etc.)
- 🔄 Continuous conversation with context retention
- ✨ Markdown rendering for formatted responses
- 🧩 Simple and clean user interface
- 🔑 API key management via environment variables

## Installation
### Prerequisites
- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/claude-ui.git
cd claude-ui
```
2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
3. Install the required packages:
```bash
uv pip install flask anthropic python-dotenv

