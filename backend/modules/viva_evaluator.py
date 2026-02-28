from backend.llm_engine import get_llm_json_response

def evaluate_answer(mode, question_data, user_answer):

    if mode == "MCQ":
        is_correct = user_answer == question_data["correct_answer"]

        return {
            "is_correct": is_correct,
            "explanation": question_data["explanation"]
        }

    elif mode in ["Viva", "Clinical Case"]:
        keywords = question_data["expected_keywords"]
        score = sum(1 for k in keywords if k.lower() in user_answer.lower())

        is_correct = score >= len(keywords) // 2

        return {
            "is_correct": is_correct,
            "explanation": question_data["explanation"]
        }
