from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
import json
def check_mcq(data, difficulty, number_of_answers, type, model):
    bloom_dict = {
    "Nhớ": "Câu hỏi yêu cầu người học ghi nhớ hoặc nhận diện thông tin đã học trước đó. Câu hỏi chỉ yêu cầu người học có thể nhớ lại các sự kiện, khái niệm, thuật ngữ, hoặc định nghĩa mà họ đã học. Câu hỏi ở cấp độ này chỉ yêu cầu nhớ lại thông tin, không yêu cầu giải thích hay phân tích gì thêm. Ví dụ: 'Đâu là năm diễn ra Cách mạng Tháng Tám ở Việt Nam?' \nA. 1945 \nB. 1954 \nC. 1975 \nD. 1986",
    
    "Hiểu": "Câu hỏi yêu cầu người học giải thích hoặc diễn giải ý nghĩa của thông tin đã học. Người học phải hiểu và nắm vững ý nghĩa của thông tin trước khi có thể diễn đạt lại bằng từ ngữ của mình. Câu hỏi này yêu cầu người học phải làm rõ những gì họ đã học thay vì chỉ đơn giản là nhớ thông tin. Ví dụ: 'Chọn câu trả lời đúng nhất để giải thích tại sao lá cây có màu xanh?' \nA. Do chứa diệp lục hấp thụ ánh sáng xanh \nB. Do chứa diệp lục phản xạ ánh sáng xanh \nC. Do chứa nước trong tế bào lá \nD. Do chứa các sắc tố hấp thụ tất cả ánh sáng ngoại trừ xanh",
    
    "Áp dụng": "Câu hỏi yêu cầu sử dụng kiến thức đã học trong các tình huống thực tế. Người học cần phải áp dụng các lý thuyết hoặc nguyên lý vào một tình huống mới. Đây là cấp độ yêu cầu người học sử dụng các công cụ hoặc quy tắc đã học để giải quyết vấn đề. Ví dụ: 'Nếu một tam giác có hai cạnh là 3 cm và 4 cm, đâu là độ dài cạnh huyền?' \nA. 5 cm \nB. 6 cm \nC. 7 cm \nD. 8 cm",
    
    "Phân tích": "Câu hỏi yêu cầu người học phân tích thông tin, chia nhỏ thành các phần và hiểu mối quan hệ giữa chúng. Người học cần phải xem xét các yếu tố chi tiết và hiểu cách chúng liên kết hoặc tác động với nhau. Đây là cấp độ đòi hỏi tư duy phức tạp và khả năng phân tích sâu sắc. Ví dụ: 'Trong bài thơ “Tây Tiến” của Quang Dũng, chi tiết nào sau đây thể hiện tinh thần hào hùng của người lính?' \nA. 'Sông Mã xa rồi Tây Tiến ơi!' \nB. 'Đêm mơ Hà Nội dáng kiều thơm' \nC. 'Rải rác biên cương mồ viễn xứ' \nD. 'Áo bào thay chiếu anh về đất'",
    
    "Đánh giá": "Câu hỏi yêu cầu đưa ra phán đoán hoặc nhận xét về một ý tưởng, quan điểm dựa trên tiêu chí hoặc bằng chứng học được. Người học cần phải sử dụng lý thuyết và các dữ liệu có sẵn để đánh giá một vấn đề hoặc giải pháp. Đây là cấp độ yêu cầu đưa ra quan điểm cá nhân dựa trên các lý lẽ vững chắc. Ví dụ: 'Đánh giá ý kiến sau: Biến đổi khí hậu là thách thức lớn nhất đối với nhân loại hiện nay. Bạn đồng ý với nhận định này không?' \nA. Hoàn toàn đồng ý \nB. Phần nào đồng ý \nC. Không đồng ý \nD. Không có ý kiến",
    
    "Sáng tạo": "Câu hỏi yêu cầu người học tạo ra một sản phẩm mới, ý tưởng mới hoặc giải pháp sáng tạo dựa trên những kiến thức đã học. Đây là cấp độ yêu cầu người học không chỉ tái tạo lại thông tin mà còn phải sáng tạo, phát triển những điều mới mẻ từ kiến thức hiện có. Ví dụ: 'Bạn được giao nhiệm vụ tổ chức một sự kiện tuyên truyền bảo vệ môi trường tại trường học. Đâu là ý tưởng phù hợp nhất?' \nA. Trồng cây xanh tại khuôn viên trường \nB. Tổ chức buổi hội thảo về môi trường \nC. Thiết kế áp phích tuyên truyền bảo vệ môi trường \nD. Cả A, B, và C đều đúng"
    }
    # print(QA_PROMPT_GEN_FORMAT)
    PROMPT_TEMPLATE_EVA = (
        "Bạn là một chuyên gia về câu hỏi trắc nghiệm, hãy kiểm tra lại độ chính xác của câu hỏi và chỉnh sửa lại chúng tốt hơn. "
        "Nếu độ khó không đạt yêu cầu thì thực hiện chỉnh sửa lại độ khó. "
        "Mức độ khó yêu cầu là:" 
        "{difficulty_bloom}"
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
    print(difficulty)
    # print(f"\n\n\n---------------eva_prompt_step_by_step-------------------\n{eva_prompt_step_by_step}")
    # print(f"\n\n\n---------------eva_prompt_example----------------------\n{eva_prompt_example}")
    # print(f"\n\n\n---------------attention_eva_dict[type]----------------\n{attention_eva_dict[type]}")
    QA_PROMPT_EVA_FORMAT = QA_PROMPT_EVA.partial_format(difficulty_bloom=bloom_dict[difficulty],
                                                        prompt_step_by_step=eva_prompt_step_by_step,
                                                        prompt_example=eva_prompt_example,
                                                        attention_eva=attention_eva_dict[type])
    # print(QA_PROMPT_EVA_FORMAT)

    # GPT

    query_engine2 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_EVA_FORMAT,
                                         llm=OpenAI(model= model, temperature=0.1, max_tokens=512),
                                         max_tokens=-1)
    return query_engine2