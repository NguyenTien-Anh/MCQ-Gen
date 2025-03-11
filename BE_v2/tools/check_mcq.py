from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
import json
def check_mcq(data, number_of_answers, type, model):
    PROMPT_TEMPLATE_EVA = (
        "Bạn là một chuyên gia về câu hỏi trắc nghiệm, hãy kiểm tra lại độ chính xác của câu hỏi và chỉnh sửa lại chúng tốt hơn. "
        "Nếu độ khó không đạt yêu cầu thì thực hiện chỉnh sửa lại độ khó. "
        "Đầu vào là 1 câu hỏi trắc nghiệm về môn học. "
        "Dữ liệu đưa vào là tài liệu về môn học."
        "\n-----------------------------\n"
        "{context_str}"
        "\n-----------------------------\n"
        "Hãy thực hiện step by step các bước theo quy trình để đánh giá câu hỏi trắc nghiệm."
        "\n{prompt_step_by_step}\n"
        "Ví dụ cho cách thực hiện quy trình trên.\n"
        "{prompt_example}"
        "\n-----------------------------\n"
        "Định dạng của câu hỏi cần đánh giá là:\n"
        "**{attention_eva}**"
        "\n-----------------------------\n"
        "Đầu ra là 1 lời đánh giá và một câu hỏi trắc nghiệm. Hãy đánh giá và cập nhật câu hỏi:  {query_str}. "
        "Đảm bảo định dạng phản hồi là 1 lời đánh giá và 1 câu hỏi trắc nghiệm, sau đó chỉ rõ đáp án đúng."
    )
    print(f"\n\n\n---------------PROMPT_TEMPLATE_EVA-----------------\n{PROMPT_TEMPLATE_EVA}")
    QA_PROMPT_EVA = PromptTemplate(PROMPT_TEMPLATE_EVA)
    eva_prompt_step_by_step = "Bước 1: Kiểm tra độ rõ ràng của câu hỏi và các đáp án.\nBước 2: Đánh giá tính liên quan của câu hỏi đến nội dung đã học.\nBước 3: Xác minh tính đúng đắn của đáp án đúng và sai.\nBước 4: Đánh giá độ khó của câu hỏi.\nBước 5: Đánh giá tính khách quan của câu hỏi.\nBước 6: Sửa đổi câu hỏi nếu cần thiết dựa trên các đánh giá.\nBước 7: Trả về câu hỏi đã được sửa đổi hoặc câu hỏi ban đầu."
    eva_prompt_example = "Bước 1: Câu hỏi \"Trong các loại khóa sau, loại nào được sử dụng để xác định duy nhất một bản ghi trong bảng?\" là rõ ràng và dễ hiểu.\nBước 2: Câu hỏi này liên quan trực tiếp đến nội dung đã học về cơ sở dữ liệu và các loại khóa.\nBước 3: Đáp án A) Khóa chính (Primary Key) là đúng. Các đáp án B) Khóa ngoại (Foreign Key), C) Khóa duy nhất (Unique Key), D) Khóa kết hợp (Composite Key), và E) Khóa tạm thời (Temporary Key) đều không phải là đáp án đúng cho câu hỏi này.\nBước 4: Độ khó của câu hỏi được đánh giá là trung bình vì nó yêu cầu người học hiểu rõ về các loại khóa trong cơ sở dữ liệu.\nBước 5: Câu hỏi này là khách quan, không thiên vị và không dẫn đến bất kỳ sự nhầm lẫn nào cho người trả lời.\nBước 6: Không cần sửa đổi câu hỏi, vì nó đã đạt yêu cầu và rõ ràng.\nCâu hỏi trắc nghiệm cuối cùng: \"Trong các loại khóa sau, loại nào được sử dụng để xác định duy nhất một bản ghi trong bảng?\" A) Khóa chính (Primary Key) B) Khóa ngoại (Foreign Key) C) Khóa duy nhất (Unique Key) D) Khóa kết hợp (Composite Key) E) Khóa tạm thời (Temporary Key) Đáp án đúng: A) Khóa chính (Primary Key)."
    attention_eva_dict = {
        "MultipleChoice": "Câu hỏi trắc nghiệm MultipleChoice gồm " + str(number_of_answers) + " đáp án và có ít nhất 2 đáp án đúng.",
        "SingleChoice": "Câu hỏi trắc nghiệm SingleChoice gồm " + str(number_of_answers) + " đáp án và có 1 đáp án đúng, " + str(number_of_answers - 1) + " đáp án sai.",
        "TrueFalse": "Câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án là 'đúng' và 'sai'.",
    }
    # print(f"\n\n\n---------------eva_prompt_step_by_step-------------------\n{eva_prompt_step_by_step}")
    # print(f"\n\n\n---------------eva_prompt_example----------------------\n{eva_prompt_example}")
    # print(f"\n\n\n---------------attention_eva_dict[type]----------------\n{attention_eva_dict[type]}")
    QA_PROMPT_EVA_FORMAT = QA_PROMPT_EVA.partial_format(prompt_step_by_step=eva_prompt_step_by_step,
                                                        prompt_example=eva_prompt_example,
                                                        attention_eva=attention_eva_dict[type])
    # print(QA_PROMPT_EVA_FORMAT)

    # GPT

    query_engine2 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_EVA_FORMAT,
                                         llm=OpenAI(model= model, temperature=0.1, max_tokens=512),
                                         max_tokens=-1)
    return query_engine2