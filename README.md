# Multiple Choice Question Generation Tool

A powerful tool that automatically generates high-quality multiple choice questions from uploaded documents or entered text, using AI to create educational assessment content.

![MCQ Generator Interface](public\ui.png)

## Overview

This application allows educators, trainers, and content creators to easily generate multiple choice questions from their learning materials. The system supports various question types (single choice, multiple choice, true/false), difficulty levels, and customizable parameters.

## Features

- **Multiple Input Methods**: Upload PDF files or directly enter text
- **Question Type Options**: Generate single choice, multiple choice, or true/false questions
- **Customizable Parameters**: Specify topic focus, quantity, number of answer options, and difficulty level
- **Quality Assurance**: Built-in recheck functionality to ensure high-quality questions
- **AI-Powered**: Leverages advanced language models to create contextually relevant questions

## Technology Stack

### Backend
- Flask (Python web framework)
- LlamaIndex (for document indexing and processing)
- OpenAI Language Models (for question generation)
- Llama Parse (document parsing tool)

### Frontend
- Node.js
- Vite (build tool)
- React
- TypeScript

## Workflow Architecture

![MCQ Generator Pipeline](public\pipeline.png)

The MCQ generation process follows this workflow:

1. **Input Processing**:
   - Text extraction from PDF files
   - Text splitting into manageable chunks

2. **Question Generation**:
   - In-context learning with the document content
   - Instruction prompting with MCQ format requirements
   - Application of Bloom's taxonomy for educational alignment
   - User requirement integration (topic, difficulty)

3. **Quality Control**:
   - Creation agent generates initial MCQs
   - Evaluation agent validates questions
   - Iterative improvement until quality standards are met

4. **Output**:
   - Completed MCQs delivered in structured format

## Installation

### Backend Setup

For detailed backend installation instructions, please refer to `BE/README.md`

### Frontend Setup

For detailed frontend installation instructions, please refer to `FE/README.md`


## Usage

1. Choose your input method (upload file or enter text)
2. Select question type (single choice, multiple choice, true/false)
3. Configure MCQ parameters:
   - Topic focus (optional)
   - Quantity of questions
   - Number of answer options
   - Difficulty level
4. Click Submit to generate questions
5. Review and export your MCQs

## Development

Please refer to the respective README files in the BE and FE directories for detailed development guidelines.

## License

[Specify your license here]

## Contributors

[List contributors here]