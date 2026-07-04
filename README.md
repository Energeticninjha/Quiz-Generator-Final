# 📚 Intelligent Quiz Generator

An AI-powered quiz generation tool built with **Python**, **Streamlit**, and the **Google Gemini API**. 

Upload any document (PDF, DOCX, TXT, MD, etc.), and this application will instantly analyze the text and generate a structured, interactive quiz based on the content. It supports multiple difficulty levels and question types.

## ✨ Features

- **Document Parsing**: Seamlessly extracts text from PDFs (`PyMuPDF`), Word documents (`python-docx`), and raw text files.
- **AI-Powered Generation**: Uses Google's `gemini-3.5-flash` model to intelligently understand the document context and formulate high-quality questions.
- **Customizable Quizzes**: Choose your desired number of questions, difficulty level (Easy, Medium, Hard), and question format (Multiple Choice, Short Answer, True/False, Coding).
- **Interactive Mode**: Take the quiz directly within the app! The interactive UI guides you question by question, providing instant grading and explanations for the correct answers.

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.8+ installed. You will also need a free [Google Gemini API Key](https://aistudio.google.com/app/apikey).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Energeticninjha/Quiz-Generator.git
   cd Quiz-Generator
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API Key:**
   Create a `.env` file in the root directory (you can copy `.env.example`) and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

### Running the App

Start the Streamlit server:
```bash
streamlit run app.py
```
The application will open in your default web browser at `http://localhost:8501`.

## 📂 Project Structure
- `app.py`: The main Streamlit user interface and interactive state machine.
- `utils/document.py`: Logic for extracting text from PDF/Docx/TXT files.
- `utils/ai_generation.py`: Handles Gemini API integration, prompt formatting, and structured JSON parsing.

## 👤 Author
Built by **D M Dharshini Sree**
