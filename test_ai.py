import ai

result = ai.interview_questions("Infosys", "Python Developer", "Python, SQL, REST APIs")
for q in result["questions"]:
    print("Q:", q["question"])
    print("Tip:", q["tip"])
    print()