import google.generativeai as genai
import json

def generate_quiz(api_key, document_text, num_q, difficulty, q_types):
    """
    Calls the Gemini API to generate a structured JSON quiz.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash')
    
    prompt = f"""
    You are an expert educator. Create a quiz based on the following text.
    
    Number of Questions: {num_q}
    Difficulty: {difficulty}
    Question Types: {', '.join(q_types)}
    
    Document Text:
    {document_text}
    
    Please format the output strictly as a JSON array of objects.
    Each object must have:
    - "question": The question text
    - "options": An array of strings for multiple choice (or true/false). Leave empty for short answer/coding.
    - "answer": The correct answer (must match one of the options exactly if options are provided).
    - "explanation": A brief explanation of the correct answer.
    
    Respond ONLY with valid JSON.
    """
    
    response = model.generate_content(prompt)
    
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:-3]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:-3]
        
    return json.loads(raw_text)
