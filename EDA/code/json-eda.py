import json
import re
from collections import defaultdict, Counter
from wordcloud import WordCloud
from konlpy.tag import Okt 

file_path = 'sentiment-service/NLP/data/navershopping_review.json'

with open(file_path, 'r', encoding="utf-8") as file:
    data = json.load(file)

## 정규 표현식을 통한 대괄호 내용 제거 메소드
def clean_item_name(item_name):
    if item_name is None:
        return "제품 없음"
    item_name = re.sub(r'\d+\.\s*|\[\d+\]|\[.*?\]', '', item_name)
    return item_name.strip()

## 1. 구매한 물품 및 rank 개수 추출
item_names = [clean_item_name(item["RD_ITEM_NM"]) for item in data]
item_names_counts = Counter(item_names)

rd_ranks = [item["RD_RANK"] for item in data]
rd_ranks_counts = Counter(rd_ranks)

# print(item_names_counts)

print("제품별 개수:")
for item_name, count in item_names_counts.items():
    print(f"{item_name}: {count}")

print("\nRD_RANK별 개수:")
for rank, count in rd_ranks_counts.items():
    print(f"{rank}: {count}")

## 2. 각 rank별 / 제품의 개수
rank_to_items = defaultdict(list)

for item in data:
    rank = item["RD_RANK"]
    item_name = clean_item_name(item["RD_ITEM_NM"])
    rank_to_items[rank].append(item_name)

rank_item_counts = {rank: Counter(items) for rank, items
                    in rank_to_items.items()}

for rank, item_count in rank_item_counts.items():
    print(f"Rank {rank}:")
    for item_name, count in item_count.items():
        print(f"   {item_name} : {count}")
    print()


