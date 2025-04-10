# Multiple Choice Question Generation Tool

This project is a tool for automatically generating multiple choice questions using AI models.

## Installation

### Prerequisites

- Python 3.10+
- Internet connection

### Setup Instructions

1. **Install UV package manager**

   ```bash
   pip install uv
   ```

2. **Create a virtual environment**

   ```bash
   uv venv
   ```

3. **Activate the virtual environment**

   On Windows:
   ```bash
   .venv\Scripts\activate
   ```

   On macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. **Install required libraries**

   ```bash
   uv pip install llama-index llama-index-core llama-index-llms-openai openai python-dotenv Flask Flask-CORS
   ```

5. **Get API Keys**

   - Obtain an OpenAI API key from [OpenAI's website](https://platform.openai.com/)
   - Get a LlamaCloud API key from [LlamaIndex's website](https://cloud.llamaindex.ai/)

6. **Configure Environment Variables**

   Create a `.env` file in the root directory with the following content:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
   ```

## Usage

Run the application:

```bash
python app.py
```

The server will start, and you can access the application through your web browser.

## Features

- Generate multiple choice questions from text content
- Customize number and difficulty of questions
- Export questions in various formats

## License

[MIT License](LICENSE)