from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from docx import Document as DocxDocument
import json
import re
import string

load_dotenv()

react_system_header_str = """\
Bạn được thiết kế để phục vụ một chức năng duy nhất: tạo ra các câu hỏi trắc nghiệm.\
Đáp án cuối cùng bạn cần đưa ra là một câu hỏi trắc nghiệm và chỉ định câu trả lời đúng.\

## Tools
Bạn có quyền truy cập vào nhiều công cụ khác nhau.
Bạn có trách nhiệm sử dụng các công cụ theo trình tự bất kỳ mà bạn cho là phù hợp để hoàn thành nhiệm vụ trước mắt.
Điều này có thể yêu cầu chia nhiệm vụ thành các nhiệm vụ phụ và sử dụng các công cụ khác nhau để hoàn thành từng nhiệm vụ phụ.
Bạn có quyền truy cập vào các công cụ sau:
{tool_desc}

## Output Format
Để tạo hoặc đánh giá các câu hỏi trắc nghiệm, vui lòng sử dụng định dạng sau.

```
Thought: Tôi cần sử dụng một công cụ để giúp tôi tạo hoặc đánh giá các câu hỏi trắc nghiệm đảm bảo đầu ra theo yêu cầu.
Action: tên công cụ (một trong {tool_names}) nếu sử dụng một công cụ.
Action Input: đầu vào của công cụ, ở định dạng JSON biểu thị kwargs (ví dụ: {{"input": "hello world", "num_beams": 5}})
```

Hãy LUÔN bắt đầu bằng một Suy nghĩ.

Vui lòng sử dụng định dạng JSON hợp lệ cho Đầu vào hành động. KHÔNG làm điều này {{'input': 'hello world', 'num_beams': 5}}.

Nếu định dạng này được sử dụng, người dùng sẽ phản hồi theo định dạng sau:

```
Observation: công cụ phản hồi

```

Bạn nên tiếp tục lặp lại định dạng trên cho đến khi có đủ thông tin để đáp ứng yêu cầu
mà không cần sử dụng thêm bất kỳ công cụ nào. Lúc đó bạn PHẢI trả lời ở một trong hai định dạng sau:

```
Thought: Tôi có thể đưa ra câu hỏi trắc nghiệm, mà không cần sử dụng thêm bất kỳ công cụ nào.
Answer: Câu trả lời phải là một câu hỏi trắc nghiệm với bốn lựa chọn và chỉ định câu trả lời đúng.  [câu trả lời ở đây]
```

```
Thought: Tôi không thể trả lời yêu cầu bằng các công cụ được cung cấp.
Answer: Xin lỗi, tôi không thể trả lời yêu cầu của bạn.
```

## Additional Rules
- ** Câu trả lời PHẢI là một câu hỏi trắc nghiệm và chỉ định câu trả lời đúng, được viết bằng tiếng việt **.
- ** Đảm bảo định dạng câu hỏi đầu ra là:
Câu hỏi: (Đưa ra câu hỏi)
A. Đáp án 1
B. Đáp án 2
C. Đáp án 3 (nếu có)
D. Đáp án 4 (nếu có)
E. Đáp án 5 (nếu có)
Đáp án đúng: (Chỉ ra đáp án) đáp án đúng 1, đáp án đúng 2 (nếu có),...**

---
HÃY CHẮC CHẮN CÂU HỎI TRẮC NGHIỆM ĐƯỢC VIẾT BẰNG TIẾNG VIỆT VÀ ĐÚNG ĐỊNH DẠNG TRÊN. 
## Current Conversation
Dưới đây là cuộc trò chuyện hiện tại bao gồm các tin nhắn của con người và trợ lý xen kẽ nhau.

"""
data = None


def select_topic(topic, quantity):
    PROMPT_TEMPLATE0_other = (
        "Dưới đây là một chủ đề về môn học."
        "\n -----------------------------\n"
        "{context_str}"
        "\n -----------------------------\n"
        "Bạn là một chuyên gia tạo câu hỏi trắc nghiệm, từ một chủ đề mà bạn tự chọn ra, hãy tìm ra các nội dung có thể sử dụng để tạo câu hỏi trắc nghiệm."
        "Nếu không thể chọn đủ số lượng yêu cầu, hãy cố gắng chọn ra nhiều nhất có thể."
        "Các nội dung được chọn phải có liên quan đến chủ đề đã chọn, được viết khái quát và ngắn gọn."
        "Đảm bảo định dạng câu trả lời bao gồm các nội dung được viết theo kiểu list trong python."
        "Ví dụ: ['nội dung 1', 'nội dung 2', 'nội dung 3',...]"
        "Đưa ra danh sách nội dung: {query_str}"
    )

    QA_PROMPT0_other = PromptTemplate(PROMPT_TEMPLATE0_other)
    select_topic_prompt = ''
    query_engine0 = ''
    if topic != '':
        select_topic_prompt = "Hãy chọn " + str(
            quantity) + " nội dung liên quan đến chủ đề \"" + topic + "\" và đưa ra duy nhất một câu trả lời đúng định dạng kiểu list trong python."
        query_engine0 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT0_other,
                                             llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, max_tokens=512),
                                             max_tokens=-1)
    else:
        select_topic_prompt = "Hãy chọn " + str(
            quantity) + " nội dung bất kì trong dữ liệu bạn có và đưa ra duy nhất một câu trả lời đúng định dạng kiểu list trong python."
        query_engine0 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT0_other,
                                             llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, max_tokens=512),
                                             max_tokens=-1)
    response = query_engine0.query(select_topic_prompt)
    subTopics = str(response)[1:-1]
    return subTopics


def check(s):
    if s.startswith("Câu") and s.find("A.") != -1 and s.find("B.") != -1 and s.lower().find("đáp án") != -1:
        return True
    return False


def read_pdf_file(file):
    file_content = ''
    reader = PdfReader(file)
    num_pages = len(reader.pages)
    for page_num in range(num_pages):
        page_object = reader.pages[page_num]
        text = page_object.extract_text()
        file_content += " " + text
    return file_content


def read_docx_file(file):
    file_content = ''
    doc = DocxDocument(file)
    for para in doc.paragraphs:
        file_content += " " + para.text
    return file_content


def read_txt_file(file):
    file_content = file.read().decode('utf-8')
    return file_content


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



def mcqGen_with_check(topic, quantity, difficulty, file, inputText, status, type, number_of_answers=4):
    print("NUM ANSWERS: ", number_of_answers)
    global data

    if status == 'true':
        print('ĐANG TẠO DATA ...')
        file_content = ""
        if file is not None:
            print("ĐANG ĐỌC FILE ...")
            ext_file = file.filename.split('.')[-1]
            if ext_file == 'pdf':
                file_content = read_pdf_file(file)
            elif ext_file == 'docx':
                file_content = read_docx_file(file)
            elif ext_file == 'txt':
                file_content = read_txt_file(file)
            else:
                raise ValueError("Unsupported file type")
            print("ĐỌC FILE THÀNH CÔNG !!!")

        text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
        content = file_content if file is not None else inputText
        gpt_documents = [Document(text=content)]
        data = VectorStoreIndex.from_documents(documents=gpt_documents, transformations=[text_splitter])
        print("TẠO DATA THÀNH CÔNG !!!")

    print('ĐANG TẠO CÂU HỎI ...')
    llm = OpenAI(model="gpt-3.5-turbo-0125")
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
    Settings.text_splitter = text_splitter

    PROMPT_TEMPLATE_GEN = (
        "Bạn là một chuyên gia câu hỏi trắc nghiệm, hãy sinh ra câu hỏi trắc nghiệm trên nội dung đưa vào và chỉ ra đáp án đúng."
        "Đầu vào là một nội dung môn học."
        "Dữ liệu đưa vào là tài liệu về môn học."
        "\n -----------------------------\n"
        "{context_str}"
        "\n -----------------------------\n"
        "Quy trình thực hiện step by step để tạo câu hỏi trắc nghiệm."
        "{prompt_step_by_step}"
        "Ví dụ cho việc thực hiện quy trình là:"
        "{prompt_example}"
        "\n -----------------------------\n"
        "Bạn hãy thực hiện step by step quy trình trên và tạo 1 câu hỏi theo yêu cầu, đảm bảo định dạng câu trả lời:  {query_str} "
        "** Yêu cầu về định dạng câu trả lời là: **"
        "{attention}"
    )
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

    print("ATTENTION: ", gen_attention)
    QA_PROMPT_GEN_FORMAT = QA_PROMPT_GEN.partial_format(prompt_step_by_step=gen_prompt_step_by_step,
                                                        prompt_example=gen_prompt_example, attention=gen_attention)
    # print(QA_PROMPT_GEN_FORMAT)
    PROMPT_TEMPLATE_EVA = (
        "Bạn là một chuyên gia về câu hỏi trắc nghiệm, hãy kiểm tra lại độ chính xác của câu hỏi và chỉnh sửa lại chúng tốt hơn."
        "Đầu vào là 1 câu hỏi trắc nghiệm về môn học."
        "Dữ liệu đưa vào là tài liệu về môn học."
        "\n -----------------------------\n"
        "{context_str}"
        "\n -----------------------------\n"
        "Hãy thực hiện step by step các bước theo quy trình để đánh giá câu hỏi trắc nghiệm."
        "{prompt_step_by_step}"
        "Ví dụ cho cách thực hiện quy trình trên."
        "{prompt_example}"
        "\n -----------------------------\n"
        "Định dạng của câu hỏi cần đánh giá là:"
        "**{attention_eva}**"
        "\n -----------------------------\n"
        "Đầu ra là 1 lời đánh giá và một câu hỏi trắc nghiệm. Hãy đánh giá và cập nhật câu hỏi:  {query_str}."
        "Đảm bảo định dạng phản hồi là 1 lời đánh giá và 1 câu hỏi trắc nghiệm, sau đó chỉ rõ đáp án đúng."
    )
    QA_PROMPT_EVA = PromptTemplate(PROMPT_TEMPLATE_EVA)
    eva_prompt_step_by_step = "Bước 1: Kiểm tra độ rõ ràng của câu hỏi và các đáp án. Bước 2: Đánh giá tính liên quan của câu hỏi đến nội dung đã học. Bước 3: Xác minh tính đúng đắn của đáp án đúng và sai. Bước 4: Đánh giá độ khó của câu hỏi. Bước 5: Đánh giá tính khách quan của câu hỏi. Bước 6: Sửa đổi câu hỏi nếu cần thiết dựa trên các đánh giá. Bước 7: Trả về câu hỏi đã được sửa đổi hoặc câu hỏi ban đầu."
    eva_prompt_example = "Bước 1: Câu hỏi \"Trong các loại khóa sau, loại nào được sử dụng để xác định duy nhất một bản ghi trong bảng?\" là rõ ràng và dễ hiểu.\nBước 2: Câu hỏi này liên quan trực tiếp đến nội dung đã học về cơ sở dữ liệu và các loại khóa.\nBước 3: Đáp án A) Khóa chính (Primary Key) là đúng. Các đáp án B) Khóa ngoại (Foreign Key), C) Khóa duy nhất (Unique Key), D) Khóa kết hợp (Composite Key), và E) Khóa tạm thời (Temporary Key) đều không phải là đáp án đúng cho câu hỏi này.\nBước 4: Độ khó của câu hỏi được đánh giá là trung bình vì nó yêu cầu người học hiểu rõ về các loại khóa trong cơ sở dữ liệu.\nBước 5: Câu hỏi này là khách quan, không thiên vị và không dẫn đến bất kỳ sự nhầm lẫn nào cho người trả lời.\nBước 6: Không cần sửa đổi câu hỏi, vì nó đã đạt yêu cầu và rõ ràng.\nCâu hỏi trắc nghiệm cuối cùng: \"Trong các loại khóa sau, loại nào được sử dụng để xác định duy nhất một bản ghi trong bảng?\" A) Khóa chính (Primary Key) B) Khóa ngoại (Foreign Key) C) Khóa duy nhất (Unique Key) D) Khóa kết hợp (Composite Key) E) Khóa tạm thời (Temporary Key) Đáp án đúng: A) Khóa chính (Primary Key)."
    attention_eva_dict = {
        "MultipleChoice": "Câu hỏi trắc nghiệm MultipleChoice gồm " + str(number_of_answers) + " đáp án và có ít nhất 2 đáp án đúng. ",
        "SingleChoice": "Câu hỏi trắc nghiệm SingleChoice gồm " + str(number_of_answers) + " đáp án và có 1 đáp án đúng, " + str(number_of_answers - 1) + " đáp án sai.",
        "TrueFalse": "Câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án là 'đúng' và 'sai'.",
    }
    print(attention_eva_dict[type])
    QA_PROMPT_EVA_FORMAT = QA_PROMPT_EVA.partial_format(prompt_step_by_step=eva_prompt_step_by_step,
                                                        prompt_example=eva_prompt_example,
                                                        attention_eva=attention_eva_dict[type])
    # print(QA_PROMPT_EVA_FORMAT)

    # GPT
    query_engine1 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_GEN_FORMAT,
                                         llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.5, max_tokens=512),
                                         max_tokens=-1)
    query_engine2 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_EVA_FORMAT,
                                         llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, max_tokens=512),
                                         max_tokens=-1)

    query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine1,
            metadata=ToolMetadata(
                name="Create",
                description=(
                    "Đầu vào là một yêu cầu. Đầu ra là một câu hỏi trắc nghiệm và có chỉ rõ đáp án đúng."
                    "Tạo câu hỏi trắc nghiệm về nội dung được yêu cầu."
                    "Sử dụng các công cụ khác để đánh giá câu hỏi."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=query_engine2,
            metadata=ToolMetadata(
                name="Check1",
                description=(
                    "Đầu vào là một câu hỏi trắc nghiệm. Đầu ra là 1 câu đánh giá và 1 câu hỏi trắc nghiệm. Hãy chỉ rõ câu trả lời đúng."
                    "Tiến hành đánh giá câu hỏi. Giải thích câu trả lời đúng, nếu câu hỏi hoặc câu trả lời sai thì thực hiện chỉnh sửa lại."
                    "Nếu không có câu trả lời đúng thì hãy sửa lại câu trả lời."
                    "Nếu các đáp án tương tự nhau thì hãy sửa lại."
                    "Cải thiện câu hỏi trắc nghiệm."
                    "Kết quả cuối cùng là 1 câu hỏi trắc nghiệm."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=query_engine2,
            metadata=ToolMetadata(
                name="Check2",
                description=(
                    "Đầu vào là một câu hỏi trắc nghiệm. Đầu ra là 1 câu đánh giá và 1 câu hỏi trắc nghiệm. Hãy chỉ rõ câu trả lời đúng."
                    "Tiến hành đánh giá câu hỏi. Giải thích câu trả lời đúng, nếu câu hỏi hoặc câu trả lời sai thì thực hiện chỉnh sửa lại."
                    "Nếu không có câu trả lời đúng thì hãy sửa lại câu trả lời."
                    "Nếu các đáp án tương tự nhau thì hãy sửa lại."
                    "Cải thiện câu hỏi trắc nghiệm."
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

    react_system_prompt = PromptTemplate(react_system_header_str)
    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
    agent.reset()
    subTopics = select_topic(topic, quantity)
    list_topic = subTopics.split("',")
    notify = ""
    if len(list_topic) < int(quantity):
        notify = "XIN LỖI CHÚNG TÔI KHÔNG THỂ SINH ĐỦ CÂU HỎI CHO CHỦ ĐỀ NÀY"
        print(notify)
    difficulty_dict = {
        "dễ": "Câu hỏi có độ khó ở mức dễ. Câu hỏi dễ là câu hỏi có thông tin dễ dàng tìm kiếm được trong văn bản.",
        "trung bình": "Câu hỏi có độ khó ở mức trung bình. Câu hỏi trung bình là câu hỏi yêu cầu một vài bước tư duy đơn giản của người dùng.",
        "cao": "Câu hỏi có độ khó ở mức khó. Câu hỏi khó là câu hỏi dễ gây nhầm lẫn, đòi hỏi sự suy luận của người dùng.",
        "auto": ""
    }
    type_dict = {
        "MultipleChoice": "Tạo 1 câu hỏi trắc nghiệm MultipleChoice gồm " + str(
            number_of_answers) + " đáp án và có ít nhất 2 đáp án đúng. ",
        "SingleChoice": "Tạo 1 câu hỏi trắc nghiệm singlechoice gồm " + str(
            number_of_answers) + " đáp án và có 1 đáp án đúng, " + str(number_of_answers - 1) + " đáp án sai.",
        "TrueFalse": "Tạo 1 câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án đúng hoặc sai và có 1 đáp án đúng, 1 đáp án sai.",
    }
    mcqs = []
    for i in range(0, int(quantity)):
        if i > len(list_topic) - 1:
            continue
        s = list_topic[i]
        kq = ""
        prompt = type_dict[
                     type] + "Câu hỏi có nội dung liên quan đến " + s + " trong chủ đề " + topic + \
                 difficulty_dict[difficulty]
        prompt = prompt + "Sau khi tạo câu hỏi sử dụng công cụ kiểm tra lại."
        question = agent.chat(prompt)
        kq = str(question.response)
        mcqs.append(kq)
    print("TẠO CÂU HỎI THÀNH CÔNG !!!")
    print("ĐANG FORMAT CÂU HỎI ...")
    mcqs = format_mcq(mcqs)
    print("FORMAT CÂU HỎI THÀNH CÔNG !!!")
    return mcqs, notify


def mcqGen_without_check(topic, quantity, difficulty, file, inputText, status, type, number_of_answers=4):
    print("NUM ANSWERS: ", number_of_answers)
    global data
    if file is None:
        print("File IS NONE. USE INPUT TEXT !!!")
    else:
        print("USING FILE !!!")
    if status == 'true':
        print('ĐANG TẠO DATA ...')
        file_content = ""
        if file is not None:
            ext_file = file.filename.split('.')[-1]
            if ext_file == 'pdf':
                file_content = read_pdf_file(file)
            elif ext_file == 'docx':
                file_content = read_docx_file(file)
            elif ext_file == 'txt':
                file_content = read_txt_file(file)
            else:
                raise ValueError("Unsupported file type")

        text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
        content = file_content if file is not None else inputText
        gpt_documents = [Document(text=content)]
        data = VectorStoreIndex.from_documents(documents=gpt_documents, transformations=[text_splitter])
        print("TẠO DATA THÀNH CÔNG !!!")

    print('ĐANG TẠO CÂU HỎI ...')
    llm = OpenAI(model="gpt-3.5-turbo-0125")
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
    Settings.text_splitter = text_splitter

    PROMPT_TEMPLATE_GEN = (
        "Bạn là một chuyên gia câu hỏi trắc nghiệm, hãy sinh ra câu hỏi trắc nghiệm trên nội dung đưa vào và chỉ ra đáp án đúng."
        "Đầu vào là một nội dung môn học."
        "Dữ liệu đưa vào là tài liệu về môn học."
        "\n -----------------------------\n"
        "{context_str}"
        "\n -----------------------------\n"
        "Quy trình thực hiện step by step để tạo câu hỏi trắc nghiệm."
        "{prompt_step_by_step}"
        "Ví dụ cho việc thực hiện quy trình là:"
        "{prompt_example}"
        "\n -----------------------------\n"
        "Bạn hãy thực hiện step by step quy trình trên và tạo 1 câu hỏi trắc nghiệm theo yêu cầu."
        "Yêu cầu sinh câu hỏi là: {query_str}"
        "**Đảm bảo định dạng câu trả lời chỉ gồm 1 câu hỏi trắc nghiệm theo yêu cầu, câu hỏi ở dòng 1, đáp án đúng ghi trên 1 dòng."
        " Yêu cầu về định dạng câu trả lời là: "
        "{attention} **"
    )
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
    # print(QA_PROMPT_GEN_FORMAT)
    # GPT
    query_engine1 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_GEN_FORMAT,
                                         llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.5, max_tokens=512),
                                         max_tokens=-1)
    subTopics = select_topic(topic, quantity)
    list_topic = subTopics.split("',")
    notify = ""
    if len(list_topic) < int(quantity):
        notify = "XIN LỖI CHÚNG TÔI KHÔNG THỂ SINH ĐỦ SỐ CÂU HỎI CHO CHỦ ĐỀ NÀY"
        print(notify)
    difficulty_dict = {
        "dễ": "Câu hỏi có độ khó ở mức dễ. Câu hỏi dễ là câu hỏi có thông tin dễ dàng tìm kiếm được trong văn bản.",
        "trung bình": "Câu hỏi có độ khó ở mức trung bình. Câu hỏi trung bình là câu hỏi yêu cầu một vài bước tư duy đơn giản của người dùng.",
        "cao": "Câu hỏi có độ khó ở mức khó. Câu hỏi khó là câu hỏi dễ gây nhầm lẫn, đòi hỏi sự suy luận của người dùng.",
        "auto": ""
    }
    type_dict = {
        "MultipleChoice": "Tạo 1 câu hỏi trắc nghiệm MultipleChoice gồm " + str(number_of_answers) + " đáp án và có ít nhất 2 đáp án đúng và " + str(number_of_answers - 2) + "đáp án sai. Đảm bảo có ít nhất 2 đáp án đúng.",
        "SingleChoice": "Tạo 1 câu hỏi trắc nghiệm singlechoice gồm " + str(number_of_answers) + " đáp án và có 1 đáp án đúng, " + str(number_of_answers - 1) + " đáp án sai.",
        "TrueFalse": "Tạo 1 câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án là 'đúng' và 'sai'.",
    }
    mcqs = []
    for i in range(0, int(quantity)):
        if i > len(list_topic):
            continue
        s = list_topic[i]
        kq = ""
        prompt = type_dict[type] + "Câu hỏi có nội dung liên quan đến " + s + " trong chủ đề " + topic + difficulty_dict[difficulty]
        question = query_engine1.query(prompt)
        kq=str(question)
        mcqs.append(kq)
    print("TẠO CÂU HỎI THÀNH CÔNG !!!")
    print("ĐANG FORMAT CÂU HỎI ...")
    mcqs = format_mcq(mcqs)
    print("FORMAT CÂU HỎI THÀNH CÔNG !!!")
    return mcqs, notify