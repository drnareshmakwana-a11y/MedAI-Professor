def generate_viva_prompt(topic, student_answer=None):

    if student_answer is None:
        # First question
        prompt = f"""
You are a strict final year MBBS examiner.

Start viva on the topic: {topic}

Ask ONE fundamental question first.
Do not give explanation.
Do not give answer.
Only ask question.
"""
    else:
        # Evaluate student answer
        prompt = f"""
You are a strict final year MBBS examiner.

The viva topic is: {topic}

Student answered:
{student_answer}

1. Briefly evaluate the answer (Correct / Partially correct / Incorrect).
2. Add missing important points.
3. Ask the next deeper viva question.

Keep response concise.
"""

    return prompt