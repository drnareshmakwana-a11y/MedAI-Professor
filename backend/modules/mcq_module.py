import re
from backend.llm_engine import get_llm_response


def start_mcq(topic):

    prompt = f"""
    Generate ONE postgraduate-level medical MCQ on the topic: {topic}

    Format STRICTLY as:

    Question:
    <question>

    A) <option>
    B) <option>
    C) <option>
    D) <option>

    Correct Answer: <A/B/C/D>

    Explanation:
    <brief explanation>
    """

    response = get_llm_response(prompt)

    # -----------------------------
    # Extract question
    # -----------------------------
    question_match = re.search(r"Question:\s*(.*?)\n[A-D]\)", response, re.DOTALL)
    question = question_match.group(1).strip() if question_match else "MCQ generation error."

    # -----------------------------
    # Extract options
    # -----------------------------
    options = re.findall(r"([A-D]\)\s.*)", response)

    # -----------------------------
    # Extract correct answer letter
    # -----------------------------
    correct_match = re.search(r"Correct Answer:\s*([A-D])", response)
    correct_letter = correct_match.group(1) if correct_match else None

    # -----------------------------
    # Extract explanation
    # -----------------------------
    explanation_match = re.search(r"Explanation:\s*(.*)", response, re.DOTALL)
    explanation = explanation_match.group(1).strip() if explanation_match else ""

    return {
        "question": question,
        "options": options,
        "correct_answer": correct_letter,
        "explanation": explanation
    }


def evaluate_mcq_answer(user_answer, correct_answer, explanation):

    # user_answer will be like "A) Option text"
    selected_letter = user_answer[0] if user_answer else ""

    if selected_letter == correct_answer:
        return {
            "result": "correct",
            "message": f"✅ Correct!\n\nExplanation:\n{explanation}"
        }
    else:
        return {
            "result": "incorrect",
            "message": f"❌ Incorrect.\n\nCorrect Answer: {correct_answer}\n\nExplanation:\n{explanation}"
        }