import string
def format_mcq(mcqs):
    def parse_question(mcq):
        print("**CÂU HỎI TRƯỚC KHI FORMAT****************************")
        print(mcq)
        print("******************************************************")
        lines = mcq.split("\n")
        question = lines[0].strip()
        answers = []
        try:
            correct_answer = lines[-1].split(": ")[1].strip()
        except:
            correct_answer = ""

        print("ĐÁP ÁN ĐÚNG: ", correct_answer)

        for line in lines[1:-1]:
            answer_text = line.strip(string.punctuation)

            if answer_text == "":
                continue

            is_correct = "true" if (correct_answer.lower().find(answer_text.lower()) != -1 or
                                    answer_text.lower().find(correct_answer.lower()) != -1) else "false"
            print(f"CÂU TRẢ LỜI: {answer_text} - IS_CORRECT: {is_correct}")
            answers.append({"answer": answer_text, "isCorrectAnswer": is_correct})

        question_dict = {
            "question": question,
            "answers": answers
        }
        return question_dict

    return [parse_question(mcq) for mcq in mcqs]