import streamlit as st
from backend.llm_engine import get_llm_response, get_llm_json_response

class VivaSession:
    def __init__(self, topic):
        self.topic = topic
        if 'viva_history' not in st.session_state:
            st.session_state.viva_history = []
            st.session_state.current_score = 0
            st.session_state.question_count = 0

    def get_next_question(self):
        prompt = f"Ask a challenging final year MBBS viva question about {self.topic}. Keep it concise."
        question = get_llm_response(prompt, mode="examiner")
        return question

    def evaluate_answer(self, question, student_answer):
        eval_prompt = (
            f"Question: {question}\n"
            f"Student Answer: {student_answer}\n"
            "Evaluate strictly. Provide a score out of 10 and brief constructive feedback."
        )
        result = get_llm_json_response(eval_prompt)
        
        # Update session state
        st.session_state.viva_history.append({
            "question": question,
            "answer": student_answer,
            "score": result.get("score", 0),
            "feedback": result.get("feedback", "")
        })
        st.session_state.current_score += result.get("score", 0)
        st.session_state.question_count += 1
        return result

def handle_clinical_case(case_input):
    """Logic for branching clinical case discussion."""
    system_instruction = "You are a lead consultant. Guide the student through this case step-by-step."
    return get_llm_response(case_input, system_instruction)