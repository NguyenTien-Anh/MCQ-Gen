from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
def select_topic(data, topic, quantity, model):
    PROMPT_TEMPLATE0_other = (
        "Dưới đây là một chủ đề về môn học."
        "\n-----------------------------\n"
        "{context_str}"
        "\n-----------------------------\n"
        "Bạn là một chuyên gia tạo câu hỏi trắc nghiệm, từ một chủ đề mà bạn tự chọn ra, hãy tìm ra các nội dung có thể sử dụng để tạo câu hỏi trắc nghiệm. "
        "Nếu không thể chọn đủ số lượng yêu cầu, hãy cố gắng chọn ra nhiều nhất có thể. "
        "Các nội dung được chọn phải có liên quan đến chủ đề đã chọn, được viết khái quát và ngắn gọn. "
        "Đảm bảo định dạng câu trả lời bao gồm các nội dung được viết theo kiểu list trong python. "
        "Ví dụ: ['nội dung 1', 'nội dung 2', 'nội dung 3',...]. "
        "Đưa ra danh sách nội dung: {query_str}"
    )

    QA_PROMPT0_other = PromptTemplate(PROMPT_TEMPLATE0_other)
    select_topic_prompt = ''
    query_engine0 = ''
    if topic != '':
        select_topic_prompt = "Hãy chọn " + str(
            quantity) + " nội dung liên quan đến chủ đề \"" + topic + "\" và đưa ra duy nhất một câu trả lời đúng định dạng kiểu list trong python."
        query_engine0 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT0_other,
                                             llm=OpenAI(model= model, temperature=0.1, max_tokens=512),
                                             max_tokens=-1)
    else:
        select_topic_prompt = "Hãy chọn " + str(
            quantity) + " nội dung bất kì trong dữ liệu bạn có và đưa ra duy nhất một câu trả lời đúng định dạng kiểu list trong python."
        query_engine0 = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT0_other,
                                             llm=OpenAI(model= model, temperature=0.1, max_tokens=512),
                                             max_tokens=-1)

    response = query_engine0.query(select_topic_prompt)
    subTopics = str(response).split('[')[-1][:-1]
    return subTopics