def generate_case_prompt(topic, student_answer=None):

    if student_answer is None:
        prompt = f"""
You are a clinical professor conducting final year MBBS case discussion.

Create a realistic clinical case scenario related to: {topic}

Include:
- Age
- Gender
- Chief complaints
- Important history
- Relevant physical findings

Then ask:
"What is your provisional diagnosis?"

Do NOT reveal diagnosis.
Only present case and ask question.
"""
    else:
        prompt = f"""
You are a clinical professor conducting case discussion.

The topic is: {topic}

Student answered:
{student_answer}

1. Evaluate the answer briefly.
2. Correct mistakes if any.
3. Ask next logical clinical reasoning question
   (e.g., differential diagnosis / investigation / management).

Keep discussion stepwise and exam-oriented.
Do NOT reveal full answer immediately.
"""

    return prompt