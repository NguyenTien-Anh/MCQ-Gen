# !pip install llama-index
# !pip install llama-index-llms-anthropic
# !pip install llama-index-llms-mistralai
# !pip install -q --upgrade google-generativeai langchain-google-genai chromadb pypdf
# !pip install langchain-community langchain-core

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core import PromptTemplate
# import warnings
# from langchain import PromptTemplate as PromptTemplateLangchain
# from langchain.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.docstore.document import Document as GeminiDocument
# from langchain.chains import RetrievalQA
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
from docx import Document as DocxDocument
import win32com

load_dotenv()

llm = OpenAI(model="gpt-3.5-turbo-0125")
text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
Settings.text_splitter = text_splitter

PROMPT_TEMPLATE1 = (
    "Dưới đây là một chủ đề về một môn học."
    "\n -----------------------------\n"
    "{context_str}"
    "\n -----------------------------\n"
    "Bạn là một chuyên gia câu hỏi trắc nghiệm, hãy sinh ra câu hỏi trắc nghiệm gồm 4 đáp án dựa trên chủ đề đưa vào và chỉ ra đáp án đúng."
    "Tạo câu hỏi về chủ đề là:  {query_str}"
)
QA_PROMPT1 = PromptTemplate(PROMPT_TEMPLATE1)

PROMPT_TEMPLATE2 = (
    "Đầu vào là 1 câu hỏi trắc nghiệm."
    "\n -----------------------------\n"
    "{context_str}"
    "\n -----------------------------\n"
    "Bạn là một chuyên gia về câu hỏi trắc nghiệm, hãy kiểm tra lại độ chính xác của câu hỏi và chỉnh sửa lại chúng tốt hơn."
    "Đầu ra là 1 lời đánh giá và một câu hỏi trắc nghiệm. Hãy đánh giá và cập nhật câu hỏi:  {query_str}."
    "Đảm bảo định dạng phản hồi là 1 lời đánh giá và 1 câu hỏi trắc nghiệm có 4 đáp án lựa chọn, sau đó chỉ rõ đáp án đúng."
)
QA_PROMPT2 = PromptTemplate(PROMPT_TEMPLATE2)

react_system_header_str = """\
Bạn được thiết kế để phục vụ một chức năng duy nhất: tạo ra các câu hỏi trắc nghiệm.\
Đáp án cuối cùng bạn cần đưa ra là một câu hỏi trắc nghiệm với bốn lựa chọn và chỉ định câu trả lời đúng.\

## Tools
Bạn có quyền truy cập vào nhiều công cụ khác nhau.
Bạn có trách nhiệm sử dụng các công cụ theo trình tự bất kỳ mà bạn cho là phù hợp để hoàn thành nhiệm vụ trước mắt.
Điều này có thể yêu cầu chia nhiệm vụ thành các nhiệm vụ phụ và sử dụng các công cụ khác nhau để hoàn thành từng nhiệm vụ phụ.

Bạn có quyền truy cập vào các công cụ sau:
{tool_desc}

## Output Format
Để tạo hoặc đánh giá các câu hỏi trắc nghiệm, vui lòng sử dụng định dạng sau.

```
Thought: Tôi cần sử dụng một công cụ để giúp tôi tạo hoặc đánh giá các câu hỏi trắc nghiệm.
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
- Câu trả lời PHẢI là một câu hỏi trắc nghiệm với bốn lựa chọn và chỉ định câu trả lời đúng, được viết bằng tiếng việt.
- Câu trả lời PHẢI có định dạng sau: 
Câu hỏi: (Đưa ra câu hỏi)
A. Đáp án 1
B. Đáp án 2
C. Đáp án 3
D. Đáp án 4
Đáp án đúng: (Chỉ ra đáp án đúng)

## Current Conversation
Dưới đây là cuộc trò chuyện hiện tại bao gồm các tin nhắn của con người và trợ lý xen kẽ nhau.

"""

data = None


def read_pdf_file(file):
    print('----------------file-pdf---------------')
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
    print('----------------file-docx---------------')
    doc = DocxDocument(file)
    for para in doc.paragraphs:
        file_content += " " + para.text
    return file_content


def read_txt_file(file):
    print('----------------file-txt---------------')
    file_content = file.read().decode('utf-8')
    return file_content


def mcqGen(topic, quantity, difficulty, file, inputText, status):
    global data
    if status == 'true':
        print('tạo data')
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

    print('tạo câu hỏi')
    template_0 = """
    Bạn là một chuyên gia tạo câu hỏi trắc nghiệm, từ một chủ đề được yêu cầu, hãy tìm ra các nội dung có thể sử dụng để tạo câu hỏi trắc nghiệm.
    Nếu không thể chọn đủ số lượng yêu cầu, hãy cố gắng chọn ra nhiều nhất có thể.
    Các nội dung được chọn phải có liên quan đến chủ đề được yêu cầu, được viết khái quát và ngắn gọn.
    Đảm bảo định dạng câu trả lời bao gồm các nội dung được viết theo kiểu list trong python.
    Ví dụ: ["nội dung 1", "nội dung 2", "nội dung 3",...]"""

    template_0_other = """
        Bạn là một chuyên gia tạo câu hỏi trắc nghiệm, hãy tự lựa chọn một chủ đề và tìm ra các nội dung có thể sử dụng để tạo câu hỏi trắc nghiệm.
        Nếu không thể chọn đủ số lượng yêu cầu, hãy cố gắng chọn ra nhiều nhất có thể.
        Các nội dung được chọn phải có liên quan đến chủ đề bạn nghĩ ra, được viết khái quát và ngắn gọn.
        Đảm bảo định dạng câu trả lời bao gồm các nội dung được viết theo kiểu list trong python.
        Ví dụ: ["nội dung 1", "nội dung 2", "nội dung 3",...]"""

    PROMPT_TEMPLATE0 = (
        "Dưới đây là một chủ đề về một môn học."
        "\n -----------------------------\n"
        "{context_str}"
        "\n -----------------------------\n"
        "Bạn là một chuyên gia tạo câu hỏi trắc nghiệm, từ một chủ đề được yêu cầu, hãy tìm ra các nội dung có thể sử dụng để tạo câu hỏi trắc nghiệm."
        "Nếu không thể chọn đủ số lượng yêu cầu, hãy cố gắng chọn ra nhiều nhất có thể."
        "Các nội dung được chọn phải có liên quan đến chủ đề được yêu cầu, được viết khái quát và ngắn gọn."
        "Đảm bảo định dạng câu trả lời bao gồm các nội dung được viết theo kiểu list trong python."
        "Ví dụ: ['nội dung 1', 'nội dung 2', 'nội dung 3',...]"
        "Đưa ra danh sách nội dung: {query_str}"
    )
    QA_PROMPT0 = PromptTemplate(PROMPT_TEMPLATE0)

    PROMPT_TEMPLATE0_other = (
        "Dưới đây là một chủ đề về một môn học."
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
        select_topic_prompt = template_0 + "\nYêu cầu: Hãy chọn " + str(
            quantity) + " nội dung liên quan đến chủ đề \"" + topic + "\" và đưa ra duy nhất một câu trả lời đúng định dạng kiểu list trong python."
        query_engine0 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT0,
                                             llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, max_tokens=512),
                                             max_tokens=-1)
    else:
        select_topic_prompt = template_0_other + "\nYêu cầu: Hãy chọn " + str(
            quantity) + " nội dung liên quan chủ đề mà bạn tự chọn và đưa ra duy nhất một câu trả lời đúng định dạng kiểu list trong python."
        query_engine0 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT0_other,
                                             llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, max_tokens=512),
                                             max_tokens=-1)
    print('select_topic_prompt:', select_topic_prompt)
    response = query_engine0.query(select_topic_prompt)
    subTopics = str(response)[1:-1]
    print('subTopics:', subTopics)

    # GPT
    query_engine1 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT1,
                                         llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.5, max_tokens=512),
                                         max_tokens=-1)
    query_engine2 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT2,
                                         llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, max_tokens=512),
                                         max_tokens=-1)

    # Gemini
    # warnings.filterwarnings("ignore")
    # restart python kernal if issues with langchain import.
    # model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1,convert_system_message_to_human=True)
    # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # gemini_documents = [GeminiDocument(page_content=file_content)]
    # gemini_text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=1000)
    # context = "\n\n".join(str(p.page_content) for p in gemini_documents)
    # texts = gemini_text_splitter.split_text(context)
    # vector_index = Chroma.from_texts(texts, embeddings).as_retriever(search_kwargs={"k":3})

    # template = """
    # Bạn là một chuyên gia tạo câu hỏi trắc nghiệm, từ 1 chủ đề hãy tìm ra các nội dung có thể sử dụng để tạo câu hỏi trắc nghiệm.
    # Từ chủ đề được đưa vào, hãy chọn ra một số nội dung có thể tạo câu hỏi trắc nghiệm.
    # Đảm bảo định dạng câu trả lời là các nội dung được để định dạng kiểu list trong python.
    # Ví dụ: ["nội dung 1", "nội dung 2", "nội dung 3", "nội dung 4"]
    # \nVăn bản đầu vào (Context): {context}
    # \nCâu hỏi (Question): {question}
    # \nCâu trả lời (Answer):"""
    # QA_CHAIN_PROMPT = PromptTemplateLangchain.from_template(template)
    # qa_chain = RetrievalQA.from_chain_type(model, retriever=vector_index, return_source_documents=True, chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})

    query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine1,
            metadata=ToolMetadata(
                name="Create",
                description=(
                    "Đầu vào là một yêu cầu. Đầu ra là một câu hỏi trắc nghiệm và có chỉ rõ đáp án đúng."
                    "Tạo câu hỏi trắc nghiệm về chủ đề được yêu cầu."
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

    # select_topic_prompt = "Chọn " + str(quantity) +  " nội dung liên quan đến chủ đề bất kì" + topic
    # result = qa_chain({"query": select_topic_prompt})
    # subTopics = result["result"][1:-1]
    # print(subTopics)

    mcqs = []
    for s in subTopics.split(","):
        prompt = " Tạo 1 câu hỏi trắc nghiệm có nội dung liên quan đến " + s
        if difficulty != "auto":
            prompt = prompt + " có độ khó ở mức " + str(difficulty)
        prompt = prompt + ", sau đó sử dụng công cụ kiểm tra lại."
        print("In ra prompt: ")
        print(prompt)
        question = agent.chat(prompt)
        mcqs.append(str(question))
    return mcqs


if __name__ == "__main__":
    topic = 'Thao tác với File'
    quantity = 1
    difficulty = 'easy'
    file = None
    inputText = ''
    result = mcqGen(topic, quantity, difficulty, file, inputText)
    print(result)