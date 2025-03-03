
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core import PromptTemplate

from dotenv import load_dotenv
# from docx import Document as DocxDocument
import json
import string
import fitz  # Thư viện PyMuPDF

load_dotenv()


data = None


def check(s):
    if s.startswith("Câu") and s.find("A.") != -1 and s.find("B.") != -1 and s.lower().find("đáp án") != -1:
        return True
    return False

def mcqGen(topic, quantity, difficulty, file, inputText, status, type, number_of_answers=4, is_check=True):
    print("TOPIC: ", topic)
    print("QUANTITY: ", quantity)
    print("DIFFICULTY: ", difficulty)
    print("STATUS: ", status)
    print("TYPE: ", type)
    if is_check:
        print("CÓ KIỂM TRA LẠI !!!")
        return mcqGen_with_check(topic, quantity, difficulty, file, inputText, status, type, number_of_answers)
    else:
        print("KHÔNG KIỂM TRA LẠI !!!")
        return mcqGen_without_check(topic, quantity, difficulty, file, inputText, status, type, number_of_answers)







    


def mcqGen_without_check(topic, quantity, difficulty, file, inputText, status, type, number_of_answers=4):
    print("NUM ANSWERS: ", number_of_answers)
    global data, file_content
    if file is None:
        print("File IS NONE. USE INPUT TEXT !!!")
    else:
        print("USING FILE !!!")
    if status == 'true':
        print('ĐANG TẠO DATA ...')
        # file_content = ""
        # if file is not None:
            # file_path = file
        # ext_file = file_path.split('.')[-1]
        # ext_file = file.filename.split('.')[-1]
        # if ext_file == 'pdf':
            # file_content = read_pdf_file(file)
            # elif ext_file == 'docx':
                # file_content = read_docx_file(file)
            # elif ext_file == 'txt':
                # file_content = read_txt_file(file)
            # else:
            # raise ValueError("Unsupported file type")
        # file_content = read_pdf_file(file)
        text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
        content = file_content if file is not None else inputText
        gpt_documents = [Document(text=content)]
        data = VectorStoreIndex.from_documents(documents=gpt_documents, transformations=[text_splitter])
        print("TẠO DATA THÀNH CÔNG !!!")

    print('ĐANG TẠO CÂU HỎI ...')
    llm = OpenAI(model="gpt-3.5-turbo-0125")
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
    Settings.text_splitter = text_splitter
    bloom_dict = {
    "Nhớ": "Câu hỏi yêu cầu người học ghi nhớ hoặc nhận diện thông tin đã học trước đó. Đây là cấp độ cơ bản nhất, chỉ yêu cầu người học có thể nhớ lại các sự kiện, khái niệm, thuật ngữ, hoặc định nghĩa mà họ đã học. Câu hỏi ở cấp độ này chỉ yêu cầu nhớ lại thông tin, không yêu cầu giải thích hay phân tích gì thêm. Ví dụ: 'Đâu là năm diễn ra Cách mạng Tháng Tám ở Việt Nam?' \nA. 1945 \nB. 1954 \nC. 1975 \nD. 1986",
    
    "Hiểu": "Câu hỏi yêu cầu người học giải thích hoặc diễn giải ý nghĩa của thông tin đã học. Người học phải hiểu và nắm vững ý nghĩa của thông tin trước khi có thể diễn đạt lại bằng từ ngữ của mình. Câu hỏi này yêu cầu người học phải làm rõ những gì họ đã học thay vì chỉ đơn giản là nhớ thông tin. Ví dụ: 'Chọn câu trả lời đúng nhất để giải thích tại sao lá cây có màu xanh?' \nA. Do chứa diệp lục hấp thụ ánh sáng xanh \nB. Do chứa diệp lục phản xạ ánh sáng xanh \nC. Do chứa nước trong tế bào lá \nD. Do chứa các sắc tố hấp thụ tất cả ánh sáng ngoại trừ xanh",
    
    "Áp dụng": "Câu hỏi yêu cầu sử dụng kiến thức đã học trong các tình huống thực tế. Người học cần phải áp dụng các lý thuyết hoặc nguyên lý vào một tình huống mới. Đây là cấp độ yêu cầu người học sử dụng các công cụ hoặc quy tắc đã học để giải quyết vấn đề. Ví dụ: 'Nếu một tam giác có hai cạnh là 3 cm và 4 cm, đâu là độ dài cạnh huyền?' \nA. 5 cm \nB. 6 cm \nC. 7 cm \nD. 8 cm",
    
    "Phân tích": "Câu hỏi yêu cầu người học phân tích thông tin, chia nhỏ thành các phần và hiểu mối quan hệ giữa chúng. Người học cần phải xem xét các yếu tố chi tiết và hiểu cách chúng liên kết hoặc tác động với nhau. Đây là cấp độ đòi hỏi tư duy phức tạp và khả năng phân tích sâu sắc. Ví dụ: 'Trong bài thơ “Tây Tiến” của Quang Dũng, chi tiết nào sau đây thể hiện tinh thần hào hùng của người lính?' \nA. 'Sông Mã xa rồi Tây Tiến ơi!' \nB. 'Đêm mơ Hà Nội dáng kiều thơm' \nC. 'Rải rác biên cương mồ viễn xứ' \nD. 'Áo bào thay chiếu anh về đất'",
    
    "Đánh giá": "Câu hỏi yêu cầu đưa ra phán đoán hoặc nhận xét về một ý tưởng, quan điểm dựa trên tiêu chí hoặc bằng chứng học được. Người học cần phải sử dụng lý thuyết và các dữ liệu có sẵn để đánh giá một vấn đề hoặc giải pháp. Đây là cấp độ yêu cầu đưa ra quan điểm cá nhân dựa trên các lý lẽ vững chắc. Ví dụ: 'Đánh giá ý kiến sau: Biến đổi khí hậu là thách thức lớn nhất đối với nhân loại hiện nay. Bạn đồng ý với nhận định này không?' \nA. Hoàn toàn đồng ý \nB. Phần nào đồng ý \nC. Không đồng ý \nD. Không có ý kiến",
    
    "Sáng tạo": "Câu hỏi yêu cầu người học tạo ra một sản phẩm mới, ý tưởng mới hoặc giải pháp sáng tạo dựa trên những kiến thức đã học. Đây là cấp độ yêu cầu người học không chỉ tái tạo lại thông tin mà còn phải sáng tạo, phát triển những điều mới mẻ từ kiến thức hiện có. Ví dụ: 'Bạn được giao nhiệm vụ tổ chức một sự kiện tuyên truyền bảo vệ môi trường tại trường học. Đâu là ý tưởng phù hợp nhất?' \nA. Trồng cây xanh tại khuôn viên trường \nB. Tổ chức buổi hội thảo về môi trường \nC. Thiết kế áp phích tuyên truyền bảo vệ môi trường \nD. Cả A, B, và C đều đúng"
    }

    PROMPT_TEMPLATE_GEN = (
        "Bạn là một chuyên gia câu hỏi trắc nghiệm, hãy sinh ra câu hỏi trắc nghiệm trên nội dung đưa vào và chỉ ra đáp án đúng. "
        "Đầu vào là một nội dung môn học. "
        "Dữ liệu đưa vào là tài liệu về môn học."
        "\n-----------------------------\n"
        "{context_str}"
        "\n-----------------------------\n"
        "Quy trình thực hiện step by step để tạo câu hỏi trắc nghiệm."
        "\n{prompt_step_by_step}\n"
        "Ví dụ cho việc thực hiện quy trình là:"
        "\n{prompt_example}"
        "\n-----------------------------\n"
        "Bạn hãy thực hiện step by step quy trình trên và tạo 1 câu hỏi theo yêu cầu, đảm bảo định dạng câu trả lời:  {query_str}\n"
        "**Yêu cầu về định dạng câu trả lời là:**\n"
        "{attention}"
    )
    print(f"---------------PROMPT_TEMPLATE_GEN-----------------\n{PROMPT_TEMPLATE_GEN}")
    QA_PROMPT_GEN = PromptTemplate(PROMPT_TEMPLATE_GEN)
    with open('prompt.json', 'r', encoding='utf-8') as file:
        list_prompt_gen = json.load(file)
    gen_prompt_step_by_step = ""
    gen_prompt_example = ""
    gen_attention = ""
    for prompt_gen in list_prompt_gen['prompt_gen']:
        if prompt_gen['type'] == type and prompt_gen['number_of_answers'] == number_of_answers:
            gen_prompt_step_by_step = prompt_gen['prompt_step_by_step']
            gen_prompt_example = prompt_gen["prompt_example"]
            gen_attention = prompt_gen["attention"]
    QA_PROMPT_GEN_FORMAT = QA_PROMPT_GEN.partial_format(prompt_step_by_step=gen_prompt_step_by_step,
                                                        prompt_example=gen_prompt_example, attention=gen_attention)

    print(f"\n\n\n------------gen_prompt_step_by_step--------------------\n{gen_prompt_step_by_step}")
    print(f"\n\n\n------------gen_prompt_example-------------------------\n{gen_prompt_example}")
    print(f"\n\n\n------------gen_attention------------------------------\n{gen_attention}")

    # print(QA_PROMPT_GEN_FORMAT)
    # GPT
    query_engine1 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_GEN_FORMAT,
                                         llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.5, max_tokens=512),
                                         max_tokens=-1)
    subTopics = select_topic(topic, quantity)
    print(f"\n\n\n------------------subTopics----------------\n{subTopics}")
    list_topic = subTopics.split(", ")
    print(f"\n\n\n-------------------list_topic--------------\n{list_topic}")
    notify = ""
    if len(list_topic) < int(quantity):
        notify = "XIN LỖI CHÚNG TÔI KHÔNG THỂ SINH ĐỦ SỐ CÂU HỎI CHO CHỦ ĐỀ NÀY"
        print(notify)
    type_dict = {
        "MultipleChoice": "Tạo 1 câu hỏi trắc nghiệm MultipleChoice gồm " + str(
            number_of_answers) + " đáp án và có ít nhất 2 đáp án đúng.",
        "SingleChoice": "Tạo 1 câu hỏi trắc nghiệm singlechoice gồm " + str(
            number_of_answers) + " đáp án và có 1 đáp án đúng, " + str(number_of_answers - 1) + " đáp án sai.",
        "TrueFalse": "Tạo 1 câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án đúng hoặc sai và có 1 đáp án đúng, 1 đáp án sai.",
    }
    mcqs = []
    for i in range(0, int(quantity)):
        if i > len(list_topic):
            continue
        if i > len(list_topic) - 1:
            continue
        genned_topic = list_topic[i]
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
        print(f"\n\n\n----------------prompt--------------\n{prompt}")
        question = query_engine1.query(prompt)
        kq=str(question)
        eval_question = get_bloom_evaluation(kq)
        kq= str("topic: ")+str(topic)+"\n"+ str("difficulty fist: ")+str(difficulty)+"\n"+ str("eval_question_with_bloom: ")+str(eval_question)+"\n"+str(kq)
        with open("kq1.txt", "a", encoding="utf-8") as file:
            file.write(kq)
            file.write("\n\n\n")
        # mcqs.append(kq)
    # print("TẠO CÂU HỎI THÀNH CÔNG !!!")
    # print("ĐANG FORMAT CÂU HỎI ...")
    # mcqs = format_mcq(mcqs)
    # print("FORMAT CÂU HỎI THÀNH CÔNG !!!")
    # return mcqs, notify

bloom_list=["Nhớ", "Hiểu", "Áp dụng", "Phân tích", "Đánh giá", "Sáng tạo"]
topics = [
    "Khái niệm cơ sở dữ liệu là gì",
    "Sự cần thiết của các hệ cơ sở dữ liệu",
    "Mô hình kiến trúc 3 mức của cơ sở dữ liệu",
    "Mục tiêu của các hệ cơ sở dữ liệu",
    "Hệ quản trị cơ sở dữ liệu và người quản trị",
    "Tổ chức lưu trữ dữ liệu",
    "Các mô hình truy xuất dữ liệu",
    "Khái niệm về tính toàn vẹn dữ liệu",
    "Phụ thuộc hàm trong cơ sở dữ liệu",
    "Chuẩn hóa dữ liệu và các dạng chuẩn",
    "Ngôn ngữ SQL và truy vấn cơ sở dữ liệu",
    "Các phép toán trong đại số quan hệ",
    "Tối ưu hóa câu hỏi trong cơ sở dữ liệu",
    "Cơ sở dữ liệu phân tán",
    "Cơ sở dữ liệu hướng đối tượng",
    "Mô hình cơ sở dữ liệu mạng",
    "Mô hình cơ sở dữ liệu phân cấp",
    "Mô hình thực thể - liên kết",
    "Phân biệt các mô hình dữ liệu",
    "Cơ sở dữ liệu quan hệ và lý thuyết của E.F. Codd",
    "Mối quan hệ nhiều - nhiều trong cơ sở dữ liệu",
    "An toàn và bảo mật cơ sở dữ liệu",
    "Quản trị truy cập và quyền hạn trong cơ sở dữ liệu",
    "Phân loại dữ liệu trong cơ sở dữ liệu",
    "Vai trò của ánh xạ trong mô hình cơ sở dữ liệu",
    "Các chiến lược sao lưu và phục hồi dữ liệu",
    "Kiến trúc Client-Server trong cơ sở dữ liệu",
    "Ứng dụng cơ sở dữ liệu trên môi trường Internet/Intranet",
    "Cấu trúc lưu trữ vật lý của cơ sở dữ liệu",
    "Chức năng của các hệ quản trị cơ sở dữ liệu (DBMS)",
    "Hệ thống các ký hiệu biểu diễn dữ liệu",
    "Tập hợp các phép toán thao tác trên cơ sở dữ liệu",
    "Mô hình dữ liệu mạng",
    "Mô hình cơ sở dữ liệu phân cấp",
    "Mô hình cơ sở dữ liệu quan hệ",
    "Mô hình thực thể - liên kết",
    "Các đặc trưng của mô hình dữ liệu",
    "Sự ổn định trong thiết kế mô hình dữ liệu",
    "Tính đơn giản và tính dư thừa trong mô hình dữ liệu",
    "Tính đối xứng và cơ sở lý thuyết của mô hình dữ liệu",
    "Phân biệt giữa các mô hình dữ liệu",
    "Mô hình dữ liệu hướng đối tượng",
    "Mô hình dữ liệu phân tán",
    "Kiến trúc tổng quát hệ cơ sở dữ liệu 3 mức",
    "Các mô hình truy xuất dữ liệu",
    "Mô hình dữ liệu quan hệ và lý thuyết đại số quan hệ",
    "Chuẩn hóa dữ liệu và chuẩn 3NF",
    "Phương pháp khung nhìn trong tối ưu hóa câu hỏi truy vấn",
    "Quy trình tối ưu hóa câu hỏi truy vấn trong cơ sở dữ liệu",
    "Quản lý bộ đệm và bộ nhớ trong hệ quản trị cơ sở dữ liệu",
    "Quản lý các thao tác trên cơ sở dữ liệu",
    "Môi trường giao tiếp giữa người sử dụng và hệ cơ sở dữ liệu",
    "Quản lý quyền hạn truy nhập trong cơ sở dữ liệu",
    "Sự cần thiết của các hệ cơ sở dữ liệu trong quản lý thông tin",
    "Các chiến lược sao lưu và phục hồi dữ liệu",
    "Hệ thống phân tán và cơ sở dữ liệu phân tán",
    "Tính toàn vẹn của dữ liệu và các ràng buộc toàn vẹn",
    "Các phương pháp bảo vệ an toàn cơ sở dữ liệu",
    "Cấu trúc và mô hình cơ sở dữ liệu Client-Server",
    "Nguyên lý hoạt động của hệ quản trị cơ sở dữ liệu",
    "Phân loại và quản lý các quyền truy cập cơ sở dữ liệu"
]

# <<<<<<< HEAD
file_content=pdf_to_html_with_images("E:/6. Agent_MCQ_gen/MCQ-Gen/BE/CSDL giáo trình.pdf")
print(file_content)
import random
for topic in topics:
    bloom = random.choice(bloom_list)
    file_path="E:/6. Agent_MCQ_gen/MCQ-Gen/BE/CSDL giáo trình.pdf"
    quantity=3
    difficulty=bloom
    number_of_answers=4
    type="SingleChoice"
    mcqGen_with_check(topic, quantity, difficulty, file_path, "", "true", type, number_of_answers)
    # print(test)
# =======

def main():
    file_content=read_pdf_file("E:/6. Agent_MCQ_gen/MCQ-Gen/BE/CSDL giáo trình.pdf")
    import random
    for topic in topics:
        bloom = random.choice(bloom_list)
        file_path="E:/6. Agent_MCQ_gen/MCQ-Gen/BE/CSDL giáo trình.pdf"
        quantity=3
        difficulty=bloom
        number_of_answers=4
        type="SingleChoice"
        mcqGen_with_check(topic, quantity, difficulty, file_path, "", "true", type, number_of_answers)
        # print(test)
# >>>>>>> 057898a9555099bde5ef74f37c634606ecb46998
