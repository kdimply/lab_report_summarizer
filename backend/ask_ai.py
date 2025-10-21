# backend/ask_ai.py
import google.generativeai as genai

# IMPORTANT: Make sure your API key is pasted here
# You can get one from Google AI Studio
genai.configure(api_key="AIzaSyAQGDtnLc_Hvjtp6LkcNyhH6WchrhU8bWQ") 

def get_ai_answer(report_context, user_question):
    """
    Sends the report context and user's question to the Gemini API for an answer.
    """
    
    # Using the standard, stable model name
    model = genai.GenerativeModel('models/gemini-2.5-pro') 
    
    prompt = f"""
    You are a helpful AI health assistant explaining lab reports in simple, clear terms.
    You are NOT a doctor and you MUST NOT give medical advice or a diagnosis.
    Your sole purpose is to explain what a test is and why a value might be high or low in general terms.
    
    Here is the user's lab report summary:
    ---
    {report_context}
    ---
    
    Here is the user's question: "{user_question}"

    Please answer the question based on the provided summary. Start your response with "Based on your report..."
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I couldn't process your question at the moment. Error: {e}"