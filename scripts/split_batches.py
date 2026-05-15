import csv
import os
import math

INPUT_FILE = "data/input/master_vocab.csv"
OUTPUT_DIR = "data/batches"
BATCH_SIZE = 60  # 조절 가능

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

total = len(rows)
n_batches = math.ceil(total / BATCH_SIZE)
fieldnames = rows[0].keys()

for i in range(n_batches):
    chunk = rows[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
    filename = os.path.join(OUTPUT_DIR, f"batch_{i+1:03d}.csv")
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(chunk)

print(f"총 {total}개 단어 → {n_batches}개 batch 생성 완료")
