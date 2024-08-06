import json
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
# import nltk
# from konlpy.tag import Okt
# from wordcloud import WordCloud

import warnings
warnings.filterwarnings('ignore')

import os
os.environ['HF_TOKEN']="hf_huggingface token"

file_path = 'sentiment-service/NLP/data/navershopping_review.json'

with open(file_path, 'r', encoding="utf-8") as file:
    data = json.load(file)

def clean_item_name(item_name):
    if item_name == "":
        return "제품 없음"
    item_name = re.sub(r'\d+\.\s*|\[\d+\]|\[.*?\]', '', item_name)
    return item_name.strip()

# 예시. Rank 5에 저장된 내용만 추출하여 요약하기
contents_5 = []

for item in data:
    rank = item["RD_RANK"]
    if int(rank) == 5:
        rd_content = item.get("RD_CONTENT", "").strip()
        contents_5.append(rd_content)

input_text = ' '.join(contents_5)

# print(len(top_rank_contents))
# print(top_rank_contents)

## 추가. text 정제하기


# "gogamza/kobart-summarization"
model = "MLP-KTLim/llama-3-Korean-Bllossom-8B"

tokenizer = AutoTokenizer.from_pretrained(model)
model = AutoModelForCausalLM.from_pretrained(
    model, 
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

model.eval()
                                             
PROMPT = '''
You are an expert in review summarization, 
analyzing people's reviews to extract and deliver the key points. 
Please look at the comprehensive reviews below and summarize only the main points.
Write the response in Korean.
'''
instruction = "Reviews to summarize:" + input_text

messages = [
    {"role": "system", "content": f"{PROMPT}"},
    {"role": "user", "content": f"{instruction}"}
]

input_ids = tokenizer.apply_chat_template(
    messages, 
    add_generation_prompt=True,
    return_tensors="pt"
).to('cpu')

terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

outputs = model.generate(
    input_ids,
    max_new_tokens=1024,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9
)

# outputs = model.generate(
#     input_ids,
#     max_length=150,  
#     num_beams=4,   
#     length_penalty=2.0, 
#     early_stopping=True, 
# )

print(tokenizer.decode(
    outputs[0][input_ids.shape[-1]:], 
    skip_special_tokens=True)
)
