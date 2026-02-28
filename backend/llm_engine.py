from groq import Groq
import json
from backend.config import GROQ_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)

# Personas for different session types
SYSTEM_PROMPTS = {
    "professor": "You are a senior MBBS Medical Professor. Provide evidence-based clinical explanations.",
    "examiner": "You are a strict MBBS Medical Examiner. Ask pointed questions and evaluate clinical reasoning."
}

def get_llm_response(prompt, context="", mode="professor"):
    """Standard conversational response, grounded in RAG context if provided."""
    system_content = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["professor"])
    
    # If RAG context is provided, inject it into the prompt
    full_prompt = prompt
    if context:
        full_prompt = f"Context from Medical Textbooks:\n{context}\n\nStudent Query: {prompt}"

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": full_prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error in LLM Engine: {str(e)}"

def get_llm_json_response(prompt):
    """
    STRICT JSON MODE: Used for grading and structured feedback.
    Ensures the UI can parse scores and specific points.
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a medical examiner. Respond ONLY in valid JSON format. Structure: {'score': int, 'feedback': str, 'next_question': str}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1, # Low temperature for structural stability
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        # Fallback if JSON parsing fails
        return {
            "score": 0, 
            "feedback": f"Parsing Error: {str(e)}", 
            "next_question": "Can you try rephrasing that?"
        }