import sys

with open("cauhoi.txt", "r", encoding="utf-8") as file:
    data = file.read()
    quess = data.strip().split('Câu hỏi: ')
    res = ''
    for index, ques in enumerate(quess):
        if index == 0:
            continue
        rank = f"LLM đánh giá: {ques.split('Đánh giá: ')[1]}"
        human_rank = f"Nhãn: {ques.split('Đánh giá: ')[1].split(' ')[0]}\n"
        ques = ques.split('Đánh giá: ')[0]
        res += f'{index}.\nCâu hỏi: {ques}{rank}{human_rank}\n'
        pass
with open("CSDL.txt", "w", encoding="utf-8") as file_2:
    file_2.write(res)