from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
def get_bloom_evaluation(data, question):
    PROMPT_TEMPLATE_BLOOM = (
    "Dưới đây là một câu hỏi về một môn học bất kỳ."
    "\n -----------------------------\n"
    "{context_str}"
    "\n -----------------------------\n"
    "Bạn là một chuyên gia về giảng dạy, hãy đánh giá câu hỏi tôi đưa vào theo thang đo Bloom. Thang đo Bloom có 6 cấp độ như sau:"
    "\n\n1. **Nhớ (Remember)**: Cấp độ này yêu cầu người học ghi nhớ hoặc nhận diện thông tin đã học, không cần hiểu sâu hay giải thích thêm. "
    "Câu hỏi ở cấp độ này sẽ kiểm tra khả năng nhớ lại các khái niệm, sự kiện, hoặc định nghĩa. "
    "Ví dụ: 'Nêu định nghĩa của lực ma sát.'"
    "\n   A. Lực cản trở chuyển động của vật trên bề mặt\n   B. Lực giúp tăng tốc vật chuyển động\n   C. Lực hút giữa hai vật\n   D. Lực làm vật dừng lại hoàn toàn"
    
    "\n\n2. **Hiểu (Understand)**: Câu hỏi yêu cầu người học giải thích hoặc diễn giải ý nghĩa của thông tin đã học. "
    "Đây là cấp độ yêu cầu người học không chỉ nhớ thông tin mà còn phải hiểu và có thể giải thích được ý nghĩa của thông tin đó. "
    "Ví dụ: 'Tại sao một vật chuyển động lại dừng lại khi không có lực tác dụng thêm?'"
    "\n   A. Do lực hấp dẫn\n   B. Do lực ma sát làm tiêu hao động năng\n   C. Do trọng lượng vật giảm dần\n   D. Do vận tốc ban đầu không đủ lớn"
    
    "\n\n3. **Áp dụng (Apply)**: Câu hỏi yêu cầu sử dụng kiến thức trong tình huống thực tế. "
    "Ở cấp độ này, người học phải vận dụng các lý thuyết hoặc nguyên lý vào một tình huống mới hoặc thực tế. "
    "Ví dụ: 'Một xe ô tô đang di chuyển với vận tốc 60 km/h, lực ma sát tác dụng lên xe là 500 N. Tính lực kéo cần thiết để xe giữ nguyên tốc độ.'"
    "\n   A. 400 N\n   B. 500 N\n   C. 600 N\n   D. 0 N"
    
    "\n\n4. **Phân tích (Analyze)**: Câu hỏi yêu cầu người học phân tích thông tin, chia nhỏ và xác định mối quan hệ giữa các phần của thông tin. "
    "Ở cấp độ này, người học phải phân tích các yếu tố hoặc mối quan hệ giữa các phần của vấn đề để hiểu rõ hơn về chúng. "
    "Ví dụ: 'Điều gì xảy ra khi tăng độ nhám của bề mặt tiếp xúc trong một hệ thống ma sát?'"
    "\n   A. Tăng ma sát và giảm chuyển động\n   B. Giảm ma sát và tăng chuyển động\n   C. Không thay đổi ma sát\n   D. Không ảnh hưởng đến chuyển động"
    
    "\n\n5. **Đánh giá (Evaluate)**: Câu hỏi yêu cầu người học đưa ra nhận định hoặc đánh giá về một vấn đề hoặc quan điểm. "
    "Câu hỏi ở cấp độ này yêu cầu người học đưa ra phán đoán dựa trên các tiêu chí hoặc bằng chứng, đánh giá một quan điểm hoặc giải pháp. "
    "Ví dụ: 'Đánh giá hiệu quả của việc sử dụng phanh ABS trên ô tô so với phanh thường.'"
    "\n   A. Giúp xe dừng nhanh hơn\n   B. Tăng độ an toàn khi phanh gấp\n   C. Giảm chi phí bảo trì xe\n   D. Không có lợi ích cụ thể nào"
    
    "\n\n6. **Sáng tạo (Create)**: Câu hỏi yêu cầu người học tạo ra một sản phẩm mới hoặc giải pháp sáng tạo từ kiến thức đã học. "
    "Đây là cấp độ yêu cầu người học phát triển một ý tưởng, thiết kế hoặc giải pháp mới. "
    "Ví dụ: 'Thiết kế một hệ thống phanh xe mới có khả năng tự động điều chỉnh lực phanh dựa trên điều kiện mặt đường.'"
    "\n   A. Hệ thống điều chỉnh lực bằng cảm biến nhiệt\n   B. Hệ thống ABS kết hợp với phân bố lực phanh điện tử\n   C. Phanh tay kết hợp với hệ thống phanh cơ khí\n   D. Phanh từ tính sử dụng lực hút nam châm"
    
    "\n\nHãy đưa ra câu trả lời là **1 level đánh giá** phù hợp nhất (Nhớ, Hiểu, Áp dụng, Phân tích, Đánh giá, hoặc Sáng tạo) mà không cần giải thích: {query_str}"
    )

    QA_PROMPT_BLOOM = PromptTemplate(PROMPT_TEMPLATE_BLOOM)
    query_engine_bloom = data.as_query_engine(similarity_top_k=3, text_qa_template=QA_PROMPT_BLOOM,
                                             llm=OpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, max_tokens=512),
                                             max_tokens=-1)
    response = query_engine_bloom.query(question)
    return response