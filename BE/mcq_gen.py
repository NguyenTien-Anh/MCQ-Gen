import os
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core import PromptTemplate
from dotenv import load_dotenv
from llama_index.agent.openai import OpenAIAgent
from llama_cloud_services import LlamaParse
import json

from prompt import PROMPT_TEMPLATE_GEN, PROMPT_TEMPLATE_EVA, react_system_header_str, PROMPT_TEMPLATE_TOPIC

load_dotenv()

data = None

def select_topic(topic, quantity):
    QA_PROMPT_TOPIC = PromptTemplate(PROMPT_TEMPLATE_TOPIC)
    query_engine_topic = data.as_query_engine(
        similarity_top_k=3, text_qa_template=QA_PROMPT_TOPIC,
        llm=OpenAI(model='gpt-4o-mini', temperature=0.1, max_tokens=512),
        max_tokens=-1
    )
    if topic != '':
        select_topic_prompt = "Hãy chọn " + str(quantity) + " nội dung liên quan đến chủ đề \"" + topic + "\""
    else:
        select_topic_prompt = "Hãy chọn " + str(quantity) + " nội dung bất kì trong dữ liệu bạn có"

    select_topic_prompt += (f", Câu trả lời bạn đưa ra duy nhất chỉ là định dạng json có nội dung: " +
                            "{\"topics\": [nội dung 1, nội dung 2, nội dung 3, ...]}")
    response = query_engine_topic.query(select_topic_prompt)
    subTopics = json.loads(str(response))
    return subTopics["topics"]


def parse_doc(file):
    os.makedirs("docs", exist_ok=True)
    file_path = os.path.join("docs", file.filename)
    file.save(file_path)
    parser = LlamaParse(
        result_type="markdown",  # "markdown" and "text" are available
        verbose=True
    )
    file_content = "\n\n".join([content.text for content in parser.load_data(file_path)])
    return file_content


def mcqGen(topic, quantity, difficulty, file, inputText, status, type, number_of_answers=4, is_check=True):
    global data

    if status:
        file_content = ""
        if file is not None:
            file_content = parse_doc(file)

        text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
        content = file_content if file is not None else inputText
        gpt_documents = [Document(text=content)]
        data = VectorStoreIndex.from_documents(documents=gpt_documents, transformations=[text_splitter], show_progress=True)

    llm = OpenAI(model="gpt-4o-mini")
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
    Settings.text_splitter = text_splitter

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

    QA_PROMPT_EVA = PromptTemplate(PROMPT_TEMPLATE_EVA)
    eva_prompt_step_by_step = "Bước 1: Kiểm tra độ rõ ràng của câu hỏi và các đáp án. Bước 2: Đánh giá tính liên quan của câu hỏi đến nội dung đã học. Bước 3: Xác minh tính đúng đắn của đáp án đúng và sai. Bước 4: Đánh giá độ khó của câu hỏi. Bước 5: Đánh giá tính khách quan của câu hỏi. Bước 6: Sửa đổi câu hỏi nếu cần thiết dựa trên các đánh giá. Bước 7: Trả về câu hỏi đã được sửa đổi hoặc câu hỏi ban đầu."
    eva_prompt_example = "Bước 1: Câu hỏi \"Trong các loại khóa sau, loại nào được sử dụng để xác định duy nhất một bản ghi trong bảng?\" là rõ ràng và dễ hiểu.\nBước 2: Câu hỏi này liên quan trực tiếp đến nội dung đã học về cơ sở dữ liệu và các loại khóa.\nBước 3: Đáp án A) Khóa chính (Primary Key) là đúng. Các đáp án B) Khóa ngoại (Foreign Key), C) Khóa duy nhất (Unique Key), D) Khóa kết hợp (Composite Key), và E) Khóa tạm thời (Temporary Key) đều không phải là đáp án đúng cho câu hỏi này.\nBước 4: Độ khó của câu hỏi được đánh giá là trung bình vì nó yêu cầu người học hiểu rõ về các loại khóa trong cơ sở dữ liệu.\nBước 5: Câu hỏi này là khách quan, không thiên vị và không dẫn đến bất kỳ sự nhầm lẫn nào cho người trả lời.\nBước 6: Không cần sửa đổi câu hỏi, vì nó đã đạt yêu cầu và rõ ràng.\nCâu hỏi trắc nghiệm cuối cùng: \"Trong các loại khóa sau, loại nào được sử dụng để xác định duy nhất một bản ghi trong bảng?\" A) Khóa chính (Primary Key) B) Khóa ngoại (Foreign Key) C) Khóa duy nhất (Unique Key) D) Khóa kết hợp (Composite Key) E) Khóa tạm thời (Temporary Key) Đáp án đúng: A) Khóa chính (Primary Key)."
    attention_eva_dict = {
        "MultipleChoice": "Câu hỏi trắc nghiệm MultipleChoice gồm " + str(
            number_of_answers) + " đáp án và có ít nhất 2 đáp án đúng. ",
        "SingleChoice": "Câu hỏi trắc nghiệm SingleChoice gồm " + str(
            number_of_answers) + " đáp án và có 1 đáp án đúng, " + str(number_of_answers - 1) + " đáp án sai.",
        "TrueFalse": "Câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án là 'đúng' và 'sai'.",
    }
    QA_PROMPT_EVA_FORMAT = QA_PROMPT_EVA.partial_format(prompt_step_by_step=eva_prompt_step_by_step,
                                                        prompt_example=eva_prompt_example,
                                                        attention_eva=attention_eva_dict[type])

    # GPT
    query_engine1 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_GEN_FORMAT,
                                         llm=OpenAI(model='gpt-4o-mini', temperature=0.5, max_tokens=512),
                                         max_tokens=-1)
    query_engine2 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_EVA_FORMAT,
                                         llm=OpenAI(model='gpt-4o-mini', temperature=0.1, max_tokens=512),
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
        )
    ]

    if is_check:
        query_engine_tools.append(QueryEngineTool(
            query_engine=query_engine2,
            metadata=ToolMetadata(
                name="Check",
                description=(
                    "Đầu vào là một câu hỏi trắc nghiệm. Đầu ra là 1 câu đánh giá và 1 câu hỏi trắc nghiệm. Hãy chỉ rõ câu trả lời đúng."
                    "Tiến hành đánh giá câu hỏi. Giải thích câu trả lời đúng, nếu câu hỏi hoặc câu trả lời sai thì thực hiện chỉnh sửa lại."
                    "Nếu không có câu trả lời đúng thì hãy sửa lại câu trả lời."
                    "Nếu các đáp án tương tự nhau thì hãy sửa lại."
                    "Cải thiện câu hỏi trắc nghiệm."
                    "Kết quả cuối cùng là 1 câu hỏi trắc nghiệm."
                ),
            ),
        ))

    agent = ReActAgent.from_tools(
        query_engine_tools,
        llm=llm,
        verbose=True,
    )

    format_agent = OpenAIAgent.from_tools(
        llm=llm,
        verbose=True,
        system_prompt=(
            "Hãy định dạng lại câu hỏi thành duy nhất một json có nội dung {\"question\": câu hỏi trắc nghiệm"
            "\"answers\": [{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, "
            "{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, ...]} "
            "mà không thêm bất kì dòng chữ nào khác. Ví dụ câu hỏi bạn nhận được là:\n"
            "Câu hỏi trắc nghiệm: Mô hình kiến trúc 3 mức cơ sở dữ liệu trong chủ đề Mô hình cơ sở dữ liệu bao gồm "
            "những mức nào?\nA) Mức trong\nB) Mức mô hình dữ liệu\nC) Mức ngoài\nD) Mức trung tâm\nĐáp án đúng: A) "
            "Mức trong, B) Mức mô hình dữ liệu'\n"
            "Câu trả lời chính xác bạn cần đưa ra là: "
            "{'question': 'Mô hình kiến trúc 3 mức cơ sở dữ liệu trong chủ đề Mô hình cơ sở dữ "
            "liệu bao gồm những mức nào?', 'answers': [{'answer': 'A) Mức trong', 'isCorrectAnswer': 'true'}, "
            "{'answer': 'B) Mức mô hình dữ liệu', 'isCorrectAnswer': 'true'}, {'answer': 'C) Mức ngoài', "
            "'isCorrectAnswer': 'false'}, {'answer': 'D) Mức trung tâm', 'isCorrectAnswer': 'false'}]}"
        )
    )

    react_system_prompt = PromptTemplate(react_system_header_str)
    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
    agent.reset()
    list_topic = select_topic(topic, quantity)
    notify = ""
    if len(list_topic) < int(quantity):
        notify = "XIN LỖI CHÚNG TÔI KHÔNG THỂ SINH ĐỦ CÂU HỎI CHO CHỦ ĐỀ NÀY"
    bloom_dict = {
        "nhớ": "Câu hỏi yêu cầu người học ghi nhớ hoặc nhận diện thông tin đã học trước đó. Câu hỏi chỉ yêu cầu người học có thể nhớ lại các sự kiện, khái niệm, thuật ngữ, hoặc định nghĩa mà họ đã học. Câu hỏi ở cấp độ này chỉ yêu cầu nhớ lại thông tin, không yêu cầu giải thích hay phân tích gì thêm. Ví dụ: 'Đâu là năm diễn ra Cách mạng Tháng Tám ở Việt Nam?' \nA. 1945 \nB. 1954 \nC. 1975 \nD. 1986",

        "hiểu": "Câu hỏi yêu cầu người học giải thích hoặc diễn giải ý nghĩa của thông tin đã học. Người học phải hiểu và nắm vững ý nghĩa của thông tin trước khi có thể diễn đạt lại bằng từ ngữ của mình. Câu hỏi này yêu cầu người học phải làm rõ những gì họ đã học thay vì chỉ đơn giản là nhớ thông tin. Ví dụ: 'Chọn câu trả lời đúng nhất để giải thích tại sao lá cây có màu xanh?' \nA. Do chứa diệp lục hấp thụ ánh sáng xanh \nB. Do chứa diệp lục phản xạ ánh sáng xanh \nC. Do chứa nước trong tế bào lá \nD. Do chứa các sắc tố hấp thụ tất cả ánh sáng ngoại trừ xanh",

        "áp dụng": "Câu hỏi yêu cầu sử dụng kiến thức đã học trong các tình huống thực tế. Người học cần phải áp dụng các lý thuyết hoặc nguyên lý vào một tình huống mới. Đây là cấp độ yêu cầu người học sử dụng các công cụ hoặc quy tắc đã học để giải quyết vấn đề. Ví dụ: 'Nếu một tam giác có hai cạnh là 3 cm và 4 cm, đâu là độ dài cạnh huyền?' \nA. 5 cm \nB. 6 cm \nC. 7 cm \nD. 8 cm",
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
        if topic != "":
            prompt = type_dict[
                         type] + "Câu hỏi có nội dung liên quan đến " + s + " trong chủ đề " + topic + \
                     bloom_dict[difficulty]
        else:
            prompt = type_dict[
                         type] + "Câu hỏi có nội dung liên quan đến " + s + \
                     bloom_dict[difficulty]
        prompt = prompt + "Sau khi tạo câu hỏi sử dụng công cụ kiểm tra lại."
        question = agent.chat(prompt)
        format_question = format_agent.chat(
            f"Bạn nhận được câu hỏi trắc nghiệm sau:\n{question.response} "
            "Hãy định dạng lại câu hỏi thành duy nhất một json có nội dung {\"question\": câu hỏi trắc nghiệm"
            "\"answers\": [{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, "
            "{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, ...]} "
            "mà không thêm bất kì dòng chữ nào khác."
        )
        kq = json.loads(str(format_question.response))
        mcqs.append(kq)
    return mcqs, notify
