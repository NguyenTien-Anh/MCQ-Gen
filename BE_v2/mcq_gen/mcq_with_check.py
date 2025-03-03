from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core import PromptTemplate
import json
import sys
import os

# Lấy đường dẫn folder cha của file hiện tại
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Thêm folder cha vào sys.path
sys.path.append(parent_folder)
print("Folder cha đã được thêm vào sys.path:", parent_folder)

from read_data import read_docx_file, read_pdf_file, read_txt_file
from ops import get_react_system_header_str, get_bloom_evaluation, select_topic, format_mcq
from tools import gen_mcq, check_mcq
def mcqGen_with_check(topic, quantity, difficulty, file, inputText, status, type, number_of_answers=4, model="gpt-4o-mini" ):
    print("NUM ANSWERS: ", number_of_answers)
    if status == 'true':
        print('ĐANG TẠO DATA ...')
        file_content = read_pdf_file(file)
        # if file is not None:
        #     print("ĐANG ĐỌC FILE ...")
        #     ext_file = file.filename.split('.')[-1]
        #     if ext_file == 'pdf':
        #         file_content = read_pdf_file(file)
        #     elif ext_file == 'docx':
        #         file_content = read_docx_file(file)
        #     elif ext_file == 'txt':
        #         file_content = read_txt_file(file)
        #     else:
        #         raise ValueError("Unsupported file type")
        #     print("ĐỌC FILE THÀNH CÔNG !!!")

        text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
        content = file_content if file is not None else inputText
        gpt_documents = [Document(text=content)]
        data = VectorStoreIndex.from_documents(documents=gpt_documents, transformations=[text_splitter])
        print("TẠO DATA THÀNH CÔNG !!!")

    bloom_dict = {
    "Nhớ": "Câu hỏi yêu cầu người học ghi nhớ hoặc nhận diện thông tin đã học trước đó. Câu hỏi chỉ yêu cầu người học có thể nhớ lại các sự kiện, khái niệm, thuật ngữ, hoặc định nghĩa mà họ đã học. Câu hỏi ở cấp độ này chỉ yêu cầu nhớ lại thông tin, không yêu cầu giải thích hay phân tích gì thêm. Ví dụ: 'Đâu là năm diễn ra Cách mạng Tháng Tám ở Việt Nam?' \nA. 1945 \nB. 1954 \nC. 1975 \nD. 1986",
    
    "Hiểu": "Câu hỏi yêu cầu người học giải thích hoặc diễn giải ý nghĩa của thông tin đã học. Người học phải hiểu và nắm vững ý nghĩa của thông tin trước khi có thể diễn đạt lại bằng từ ngữ của mình. Câu hỏi này yêu cầu người học phải làm rõ những gì họ đã học thay vì chỉ đơn giản là nhớ thông tin. Ví dụ: 'Chọn câu trả lời đúng nhất để giải thích tại sao lá cây có màu xanh?' \nA. Do chứa diệp lục hấp thụ ánh sáng xanh \nB. Do chứa diệp lục phản xạ ánh sáng xanh \nC. Do chứa nước trong tế bào lá \nD. Do chứa các sắc tố hấp thụ tất cả ánh sáng ngoại trừ xanh",
    
    "Áp dụng": "Câu hỏi yêu cầu sử dụng kiến thức đã học trong các tình huống thực tế. Người học cần phải áp dụng các lý thuyết hoặc nguyên lý vào một tình huống mới. Đây là cấp độ yêu cầu người học sử dụng các công cụ hoặc quy tắc đã học để giải quyết vấn đề. Ví dụ: 'Nếu một tam giác có hai cạnh là 3 cm và 4 cm, đâu là độ dài cạnh huyền?' \nA. 5 cm \nB. 6 cm \nC. 7 cm \nD. 8 cm",
    
    "Phân tích": "Câu hỏi yêu cầu người học phân tích thông tin, chia nhỏ thành các phần và hiểu mối quan hệ giữa chúng. Người học cần phải xem xét các yếu tố chi tiết và hiểu cách chúng liên kết hoặc tác động với nhau. Đây là cấp độ đòi hỏi tư duy phức tạp và khả năng phân tích sâu sắc. Ví dụ: 'Trong bài thơ “Tây Tiến” của Quang Dũng, chi tiết nào sau đây thể hiện tinh thần hào hùng của người lính?' \nA. 'Sông Mã xa rồi Tây Tiến ơi!' \nB. 'Đêm mơ Hà Nội dáng kiều thơm' \nC. 'Rải rác biên cương mồ viễn xứ' \nD. 'Áo bào thay chiếu anh về đất'",
    
    "Đánh giá": "Câu hỏi yêu cầu đưa ra phán đoán hoặc nhận xét về một ý tưởng, quan điểm dựa trên tiêu chí hoặc bằng chứng học được. Người học cần phải sử dụng lý thuyết và các dữ liệu có sẵn để đánh giá một vấn đề hoặc giải pháp. Đây là cấp độ yêu cầu đưa ra quan điểm cá nhân dựa trên các lý lẽ vững chắc. Ví dụ: 'Đánh giá ý kiến sau: Biến đổi khí hậu là thách thức lớn nhất đối với nhân loại hiện nay. Bạn đồng ý với nhận định này không?' \nA. Hoàn toàn đồng ý \nB. Phần nào đồng ý \nC. Không đồng ý \nD. Không có ý kiến",
    
    "Sáng tạo": "Câu hỏi yêu cầu người học tạo ra một sản phẩm mới, ý tưởng mới hoặc giải pháp sáng tạo dựa trên những kiến thức đã học. Đây là cấp độ yêu cầu người học không chỉ tái tạo lại thông tin mà còn phải sáng tạo, phát triển những điều mới mẻ từ kiến thức hiện có. Ví dụ: 'Bạn được giao nhiệm vụ tổ chức một sự kiện tuyên truyền bảo vệ môi trường tại trường học. Đâu là ý tưởng phù hợp nhất?' \nA. Trồng cây xanh tại khuôn viên trường \nB. Tổ chức buổi hội thảo về môi trường \nC. Thiết kế áp phích tuyên truyền bảo vệ môi trường \nD. Cả A, B, và C đều đúng"
    }
    print('ĐANG TẠO CÂU HỎI ...')
    llm = OpenAI(model=model)
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
    Settings.text_splitter = text_splitter
    query_engine1 = gen_mcq(data, number_of_answers, model)
    query_engine2 = check_mcq(data, difficulty, number_of_answers, type, model)

    query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine1,
            metadata=ToolMetadata(
                name="Create",
                description=(
                    "Đầu vào là một yêu cầu. Đầu ra là một câu hỏi trắc nghiệm và có chỉ rõ đáp án đúng. "
                    "Tạo câu hỏi trắc nghiệm về nội dung được yêu cầu. "
                    "Sử dụng các công cụ khác để đánh giá câu hỏi."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=query_engine2,
            metadata=ToolMetadata(
                name="Check1",
                description=(
                    "Đầu vào là một câu hỏi trắc nghiệm. Đầu ra là 1 câu đánh giá và 1 câu hỏi trắc nghiệm. Hãy chỉ rõ câu trả lời đúng.  "
                    "Tiến hành đánh giá câu hỏi. Giải thích câu trả lời đúng, nếu câu hỏi hoặc câu trả lời sai thì thực hiện chỉnh sửa lại. "
                    "Nếu độ khó không đạt yêu cầu thì thực hiện chỉnh sửa lại độ khó. "
                     "Nếu không có câu trả lời đúng thì hãy sửa lại câu trả lời. "
                    "Nếu các đáp án tương tự nhau thì hãy sửa lại. "
                    "Cải thiện câu hỏi trắc nghiệm. "
                    "Kết quả cuối cùng là 1 câu hỏi trắc nghiệm."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=query_engine2,
            metadata=ToolMetadata(
                name="Check2",
                description=(
                    "Đầu vào là một câu hỏi trắc nghiệm. Đầu ra là 1 câu đánh giá và 1 câu hỏi trắc nghiệm. Hãy chỉ rõ câu trả lời đúng. "
                    "Tiến hành đánh giá câu hỏi. Giải thích câu trả lời đúng, nếu câu hỏi hoặc câu trả lời sai thì thực hiện chỉnh sửa lại. "
                    "Nếu độ khó không đạt yêu cầu thì thực hiện chỉnh sửa lại độ khó. "
                    "Nếu không có câu trả lời đúng thì hãy sửa lại câu trả lời. "
                    "Nếu các đáp án tương tự nhau thì hãy sửa lại. "
                    "Cải thiện câu hỏi trắc nghiệm. "
                    "Kết quả cuối cùng là 1 câu hỏi trắc nghiệm."
                ),
            ),
        ),
    ]

    agent = ReActAgent.from_tools(
        query_engine_tools,
        llm=llm,
        verbose=True,
    )
    react_system_header_str = get_react_system_header_str()
    react_system_prompt = PromptTemplate(react_system_header_str)
    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
    agent.reset()



    subTopics = select_topic(data, topic, quantity, model)
    print(f"\n\n\n----------------subTopics----------------\n{subTopics}")
    list_topic = subTopics.split(", ")
    print(f"\n\n\n-----------------list_topic---------------\n{list_topic}")
    notify = ""
    # exit()
    if len(list_topic) < int(quantity):
        notify = "XIN LỖI CHÚNG TÔI KHÔNG THỂ SINH ĐỦ CÂU HỎI CHO CHỦ ĐỀ NÀY"
        print(notify)
    type_dict = {
        "MultipleChoice": "Tạo 1 câu hỏi trắc nghiệm MultipleChoice gồm " + str(
            number_of_answers) + " đáp án và có ít nhất 2 đáp án đúng.",
        "SingleChoice": "Tạo 1 câu hỏi trắc nghiệm singlechoice gồm " + str(
            number_of_answers) + " đáp án và có 1 đáp án đúng, " + str(number_of_answers - 1) + " đáp án sai.",
        "TrueFalse": "Tạo 1 câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án đúng hoặc sai và có 1 đáp án đúng, 1 đáp án sai.",
    }
    # mcqs = []
    for i in range(0, int(quantity)):
        if i > len(list_topic) - 1:
            continue
        genned_topic = list_topic[i]
        print(f"\n\n\n----------------------gened_topic-----------------\n{genned_topic}")
        if genned_topic[2] == '.':
            genned_topic = genned_topic[4:]
        if genned_topic[-2] == '.':
            genned_topic = genned_topic[:-2] + genned_topic[-1]
        kq = ""
        if topic != "":
            prompt = type_dict[
                     type] + " Câu hỏi có nội dung liên quan đến " + genned_topic + " trong chủ đề \"" + topic + "\". " + \
                 bloom_dict[difficulty]
        else:
            prompt = type_dict[
                         type] + " Câu hỏi có nội dung liên quan đến " + genned_topic + ". " + \
                     bloom_dict[difficulty]
        prompt = prompt + " Sau khi tạo câu hỏi sử dụng công cụ kiểm tra lại."
        print(f"\n\n\n-------------------prompt------------------------\n{prompt}")
        question = agent.chat(prompt)
        kq = str(question.response)
        eval_question = get_bloom_evaluation(data, kq)
        kq= str("topic: ")+str(topic)+"\n"+ str("difficulty fist: ")+str(difficulty)+"\n"+ str("eval_question_with_bloom: ")+str(eval_question)+"\n"+str("Câu hỏi trắc nghiệm: ")+str(kq)
        print(kq)
        # with open("kq_check.txt", "a", encoding="utf-8") as file:
        #     file.write(kq)
        #     file.write("\n\n\n")
            # mcqs.append(kq)
    # print("TẠO CÂU HỎI THÀNH CÔNG !!!")
    # print("ĐANG FORMAT CÂU HỎI ...")
    # mcqs = format_mcq(mcqs)
    # print("FORMAT CÂU HỎI THÀNH CÔNG !!!")
    # return mcqs, notify
import random
bloom_list=["Nhớ", "Hiểu", "Áp dụng", "Phân tích", "Đánh giá", "Sáng tạo"]
topic = "Khái niệm cơ sở dữ liệu là gì"
file_path="E:/6. Agent_MCQ_gen/MCQ-Gen_thang_v2/BE/CSDL giáo trình.pdf"
quantity=3
bloom = random.choice(bloom_list)
difficulty=bloom
number_of_answers=4
type="SingleChoice"
mcqGen_with_check(topic, quantity, difficulty, file_path, "", "true", type, number_of_answers)