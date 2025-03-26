from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core import PromptTemplate
import json


def gen_mcq(data, number_of_answers, model):
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
    print(
        f"---------------PROMPT_TEMPLATE_GEN-----------------\n{PROMPT_TEMPLATE_GEN}")
    QA_PROMPT_GEN = PromptTemplate(PROMPT_TEMPLATE_GEN)
    with open(r'D:\MCQ-Gen\BE_v2\tools\prompt.json', 'r', encoding='utf-8') as file:
        list_prompt_gen = json.load(file)

    gen_prompt_step_by_step = ""
    gen_prompt_example = ""
    gen_attention = ""
    for prompt_gen in list_prompt_gen['prompt_gen']:
        if prompt_gen['type'] == type and prompt_gen['number_of_answers'] == number_of_answers:
            gen_prompt_step_by_step = prompt_gen['prompt_step_by_step']
            gen_prompt_example = prompt_gen["prompt_example"]
            gen_attention = prompt_gen["attention"]

    print(
        f"\n\n\n------------gen_prompt_step_by_step--------------------\n{gen_prompt_step_by_step}")
    print(
        f"\n\n\n------------gen_prompt_example-------------------------\n{gen_prompt_example}")
    print(
        f"\n\n\n------------gen_attention------------------------------\n{gen_attention}")

    QA_PROMPT_GEN_FORMAT = QA_PROMPT_GEN.partial_format(prompt_step_by_step=gen_prompt_step_by_step,
                                                        prompt_example=gen_prompt_example, attention=gen_attention)
    query_engine1 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_GEN_FORMAT,
                                         llm=OpenAI(
                                             model=model, temperature=0.5, max_tokens=512),
                                         max_tokens=-1)
    return query_engine1
