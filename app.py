from fastapi import FastAPI, Request
from backend.mode_controller import handle_request

# -----------------------------
# FastAPI backend for Streamlit
# -----------------------------
api = FastAPI()

@api.post("/teaching")
async def teaching(request: Request):
    data = await request.json()
    topic = data.get("topic", "")
    response = handle_request("Teaching", topic)
    # Teaching mode returns only explanation, no follow-up question
    return {"explanation": response}

@api.post("/viva")
async def viva(request: Request):
    data = await request.json()
    topic = data.get("topic", "")

    response = handle_request("Viva", topic)

    return {
        "question": response
    }

@api.post("/viva_continue")
async def viva_continue(request: Request):
    data = await request.json()
    topic = data.get("topic", "")
    answer = data.get("answer", "")

    response = handle_request("Viva", answer, topic)

    return {
        "feedback": response
    }

@api.post("/case")
async def case(request: Request):
    data = await request.json()
    topic = data.get("topic", "")

    response = handle_request("Clinical Case", topic)

    return {
        "question": response,
        "explanation": response
    }

@api.post("/mcq")
async def mcq(request: Request):
    data = await request.json()
    topic = data.get("topic", "")
    response = handle_request("mcq", topic)

    if isinstance(response, dict):
        # If handle_request already returns structured dict
        return response
    else:
        # Fallback structure
        return {
            "question": response,
            "options": ["A", "B", "C", "D"],
            "explanation": ""
        }

@api.post("/mcq_continue")
async def mcq_continue(request: Request):
    data = await request.json()
    topic = data.get("topic", "")
    answer = data.get("answer", "")

    response = handle_request("mcq", answer, topic)

    return response

# -----------------------------
# CLI runner (your original code)
# -----------------------------
if __name__ == "__main__":

    print("Select Mode:")
    print("1. Teaching Mode")
    print("2. Viva Mode")
    print("3. Clinical Case Mode")
    print("4. MCQ Mode")

    mode_choice = input("Enter choice number: ")

    if mode_choice == "1":
        topic = input("\nEnter medical topic: ")
        response = handle_request("Teaching", topic)
        print("\nAI Professor Response:\n")
        print(response)

    elif mode_choice == "2":
        topic = input("\nEnter viva topic: ")
        response = handle_request("Viva", topic)
        print("\nExaminer:\n")
        print(response)

        while True:
            student_answer = input("\nYour Answer (type 'exit' to stop): ")
            if student_answer.lower() == "exit":
                print("Viva ended.")
                break
            response = handle_request("viva_continue", student_answer, topic)
            print("\nExaminer:\n")
            print(response)

    elif mode_choice == "3":
        topic = input("\nEnter case topic: ")
        response = handle_request("Case", topic)
        print("\nClinical Professor:\n")
        print(response)

        while True:
            student_answer = input("\nYour Answer (type 'exit' to stop): ")
            if student_answer.lower() == "exit":
                print("Case discussion ended.")
                break
            response = handle_request("case_continue", student_answer, topic)
            print("\nClinical Professor:\n")
            print(response)

    elif mode_choice == "4":
        topic = input("\nEnter topic for MCQ: ")
        response = handle_request("MCQ", topic)
        print("\nAI Professor MCQ:\n")
        print(response)

        while True:
            student_answer = input("\nEnter your option (A/B/C/D) or type 'exit': ")
            if student_answer.lower() == "exit":
                print("MCQ session ended.")
                break
            response = handle_request("mcq_continue", student_answer, topic)
            print("\nAI Professor:\n")
            print(response)

    else:
        print("Invalid choice")