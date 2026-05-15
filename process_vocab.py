#!/usr/bin/env python3
"""
process_vocab.py — Claude API로 batch CSV를 자동 처리하는 스크립트

사용법:
  python process_vocab.py              # 미처리 batch 전체 처리
  python process_vocab.py 2            # batch_002만 처리
  python process_vocab.py 2 5 10       # batch_002, 005, 010 처리
  python process_vocab.py --all        # 이미 처리된 것도 재처리
"""

import anthropic
import csv
import json
import os
import sys
import time

BATCH_DIR = "data/batches"
FILLED_DIR = "data/output/filled"
REVIEW_FILE = "data/output/review/polysemy_review.csv"

FIELDNAMES = [
    "lemma", "display_word", "variant", "oxford_pos",
    "meaning_ko", "example_en", "example_ko",
    "card_type", "sense_hint", "split_from", "needs_review",
]

SYSTEM_PROMPT = """당신은 Anki 영어 단어카드를 만드는 전문가입니다.
영어를 처음 배우는 한국 성인 여성(60대 이상)을 위해 단어 카드를 제작합니다.

## 입력 형식
CSV 행: lemma, display_word, variant, oxford_pos

## 출력 형식
반드시 JSON 배열로만 응답하세요. 마크다운(```), 설명 텍스트, 다른 내용은 절대 포함하지 마세요.
순수 JSON만 출력하세요. 첫 글자는 반드시 `[` 이어야 합니다.

각 원소는 다음 11개 키를 가진 평면(flat) 객체입니다. 중첩 구조 금지:
{"lemma":"...","display_word":"...","variant":"...","oxford_pos":"...","meaning_ko":"...","example_en":"...","example_ko":"...","card_type":"...","sense_hint":"...","split_from":"...","needs_review":"..."}

- lemma: 입력 그대로
- display_word: 입력 그대로
- variant: 입력 그대로
- oxford_pos: 입력 그대로
- meaning_ko: 한국어 뜻 (슬래시 구분, 최대 2개)
- example_en: 영어 예문
- example_ko: 예문 한국어 해석
- card_type: "normal" | "function_word" | "polysemy_split" 중 하나
- sense_hint: 다의어 구분 힌트 (없으면 빈 문자열 "")
- split_from: 다의어 분리 시 원본 lemma (없으면 빈 문자열 "")
- needs_review: "TRUE" 또는 "FALSE"

## 한국어 뜻(meaning_ko) 규칙
1. 최대 2개까지만. 3개 이상이면 needs_review=TRUE
2. 구어적이고 자연스러운 한국어. "~하다" 형태 선호
3. 형식: 뜻1 / 뜻2 (슬래시 구분)
4. 중복 의미는 하나로 통합 ("먹다 / 식사하다" → "먹다")
5. meaning_ko에 영어 절대 포함 금지

## 예문(example_en) 규칙
1. A1~A2 난이도, 8단어 이하 권장
2. 단어는 최대한 NGSL 1000 이내
3. 주어: I / She / He / We / The boy / The girl 등 구체적 인물
4. 추상적 예문 금지 ("This concept is important." 같은 것)
5. 소재: 가족, 음식, 집, 학교, 날씨, 감정
6. B2 이상 단어 사용 금지

## 기능어 처리 (card_type=function_word)
다음 단어들은 function_word로 처리:
be, do, have, to, in, on, at, of, for, from, by, with, as, that, this, it,
the, a, there, what, which, who, where, when, how, some, any, all, both,
each, one, other, another, will, can, may, must, should, would, could,
not, or, and, if, so, but, up, out, about, more, i, we, you, he, she, they

처리 방법:
- meaning_ko: 핵심 용법 1~2가지
- example_en: 그 용법을 보여주는 문장 1개

## 다의어 분리 규칙 (card_type=polysemy_split)
다음 조건 중 2개 이상이면 행을 분리 추가:
- oxford_pos에 n.|v. 조합이 있고 명사/동사 뜻이 전혀 다름
- oxford_pos에 품사가 3개 이상
- 한국어 뜻이 달라서 예문 하나로 설명 불가

분리 시:
- 원본 행 유지, 새 행 추가 (출력 배열에 여러 객체)
- split_from에 원본 lemma 기입
- sense_hint로 구분: "(책)", "(예약하다)" 형태

분리하지 않는 경우:
- n.|v.지만 뜻이 연결됨 (show: 쇼/보여주다 → 한 카드)
- adj.|adv. 조합 → 대부분 한 카드

## 절대 금지
- "It is important to..." 형태의 추상적 예문
- 한국어 직역투 해석
- 3개 이상 의미를 한 카드에 넣기
- meaning_ko에 영어 포함"""


def get_filled_path(batch_name: str) -> str:
    stem = batch_name.replace(".csv", "")
    return os.path.join(FILLED_DIR, f"{stem}_filled.csv")


def read_batch(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build_user_message(rows: list[dict]) -> str:
    lines = ["lemma,display_word,variant,oxford_pos"]
    for r in rows:
        lines.append(f"{r['lemma']},{r['display_word']},{r['variant']},{r['oxford_pos']}")
    return "\n".join(lines) + "\n\n위 단어들을 처리하여 JSON 배열로 반환하세요."


def call_claude(client: anthropic.Anthropic, rows: list[dict]) -> list[dict]:
    user_msg = build_user_message(rows)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )

    text = response.content[0].text.strip()

    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def ensure_dirs():
    os.makedirs(FILLED_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REVIEW_FILE), exist_ok=True)


def write_filled(filepath: str, rows: list[dict]):
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_review(rows: list[dict]):
    review_rows = [r for r in rows if r.get("needs_review") == "TRUE"]
    if not review_rows:
        return
    write_header = not os.path.exists(REVIEW_FILE) or os.path.getsize(REVIEW_FILE) == 0
    with open(REVIEW_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(review_rows)


def process_batch(client: anthropic.Anthropic, batch_path: str, force: bool = False):
    batch_name = os.path.basename(batch_path)
    filled_path = get_filled_path(batch_name)

    if not force and os.path.exists(filled_path):
        print(f"건너뜀 (이미 처리됨): {batch_name}")
        return

    rows = read_batch(batch_path)
    n_in = len(rows)
    print(f"처리 중: {batch_name} ({n_in}행)...", end=" ", flush=True)

    try:
        result = call_claude(client, rows)
    except Exception as e:
        print(f"오류! {e}")
        return

    # Normalize fields
    for row in result:
        for field in FIELDNAMES:
            row.setdefault(field, "")
        if row.get("needs_review") not in ("TRUE", "FALSE"):
            row["needs_review"] = "FALSE"

    write_filled(filled_path, result)
    append_review(result)

    n_out = len(result)
    review_count = sum(1 for r in result if r.get("needs_review") == "TRUE")
    print(f"완료 ({n_in}행 → {n_out}행, 검토필요: {review_count}행)")
    print(f"  저장: {filled_path}")


def main():
    args = sys.argv[1:]
    force = "--all" in args
    if force:
        args = [a for a in args if a != "--all"]

    client = anthropic.Anthropic()
    ensure_dirs()

    if args:
        batch_files = []
        for num in args:
            name = f"batch_{int(num):03d}.csv"
            path = os.path.join(BATCH_DIR, name)
            if os.path.exists(path):
                batch_files.append(path)
            else:
                print(f"파일 없음: {path}")
    else:
        batch_files = sorted(
            os.path.join(BATCH_DIR, f)
            for f in os.listdir(BATCH_DIR)
            if f.startswith("batch_") and f.endswith(".csv")
        )

    if not batch_files:
        print("처리할 batch 파일이 없습니다.")
        return

    for i, path in enumerate(batch_files):
        process_batch(client, path, force=force)
        # Rate-limit pause between batches (skip after last)
        if i < len(batch_files) - 1:
            time.sleep(1)

    print("\n모든 처리 완료.")


if __name__ == "__main__":
    main()
