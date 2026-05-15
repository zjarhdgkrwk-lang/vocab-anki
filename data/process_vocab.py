"""
어머니 Anki 단어장 자동 생성 스크립트
Anthropic API를 사용해 CSV를 배치 처리합니다.

사용법:
  pip install anthropic
  export ANTHROPIC_API_KEY=sk-ant-...
  python process_vocab.py

중단 후 재시작해도 progress/ 폴더 덕분에 이어서 처리됩니다.
"""

import anthropic
import csv
import json
import os
import time
import sys

# ── 설정 ──────────────────────────────────────────────────────────────────────
INPUT_FILE  = "master_vocab_beginner_adjacent_merged.csv"
OUTPUT_FILE = "mother_anki_final.csv"
PROGRESS_DIR = "progress"
BATCH_SIZE  = 50          # 한 번에 처리할 단어 수
RETRY_MAX   = 3           # API 오류 시 재시도 횟수
SLEEP_SEC   = 1.5         # 배치 간 대기 (rate limit 방지)
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
당신은 한국인 영어 입문자(60대 여성)를 위한 Anki 단어 카드 제작 전문가입니다.
JSON 데이터를 입력받아 처리 후 JSON 배열만 반환합니다.
마크다운 코드블록, 설명, 주석을 절대 포함하지 마세요. 오직 JSON만 출력하세요.

## 출력 컬럼 규칙

**meaning_ko**
- 최대 2개, 슬래시로 구분 (예: "가다 / 출발하다")
- 자연스러운 구어 한국어 사용
- 3개 이상 필요하면 needs_review=true, 가장 핵심 뜻 2개만 기재

**example_en / example_ko**
- 난이도는 [DIFFICULTY_INSTRUCTION]으로 지정됨
- 일상 소재만: 가족, 음식, 날씨, 집, 학교, 감정
- "It is important to..." 같은 추상 예문 금지
- 주어는 I / She / He / We / The boy 등 구체적 인물 사용

**card_type**
- function_word: be, do, have, to, in, on, at, of, for, from, by, with, as,
                 that, this, it, the, a, there, what, which, who, where, when,
                 how, some, any, all, both, each, one, other, another,
                 will, can, may, must, should, would, could, not, but, or, and, so
- polysemy_split: 다의어 분리 카드
- normal: 그 외

**다의어 분리 규칙**
oxford_pos에 품사가 2개 이상이고, 한국어 뜻이 완전히 달라서 예문 하나로 설명 불가한 경우에만
원본 행을 두 개의 별도 행으로 분리한다.
- sense_hint: "(책)" / "(예약하다)" 형식으로 품사/의미 구분
- split_from: 원본 lemma
- 분리 예: book(n.책 / v.예약) → 2행
- 유지 예: show(n.쇼 / v.보여주다) → 1행 (뜻이 연결됨)

**needs_review**
다음 경우 true: 다의어 분리 판단 어려움 / 뜻이 3개 이상 / 특수 용법
그 외 false

## 출력 형식 (JSON 배열)
[
  {
    "lemma": "...",
    "display_word": "...",
    "variant": "...",
    "oxford_pos": "...",
    "meaning_ko": "...",
    "example_en": "...",
    "example_ko": "...",
    "card_type": "normal|function_word|polysemy_split",
    "sense_hint": "",
    "split_from": "",
    "needs_review": false
  }
]
"""

def get_difficulty(batch_idx: int, total_batches: int) -> tuple[str, str]:
    """배치 위치에 따라 예문 난이도를 점진적으로 높임."""
    pct = batch_idx / max(total_batches - 1, 1)

    if pct < 0.20:
        return "A1",    "5~6단어, 매우 단순한 현재시제 문장"
    elif pct < 0.40:
        return "A1+",   "6~7단어, 현재/과거 시제, 기본 어휘만"
    elif pct < 0.60:
        return "A2",    "7~8단어, 다양한 시제 허용, 간단한 접속사"
    elif pct < 0.80:
        return "A2+",   "8~9단어, 자연스러운 구어 표현 포함 가능"
    else:
        return "A2-B1", "9~10단어, 실생활 맥락이 풍부한 자연스러운 문장"


def build_prompt(rows: list[dict], difficulty_label: str, difficulty_desc: str) -> str:
    instruction = f"{difficulty_label} — {difficulty_desc}"
    prompt_system = SYSTEM_PROMPT.replace("[DIFFICULTY_INSTRUCTION]", instruction)
    return prompt_system, json.dumps(rows, ensure_ascii=False)


def parse_response(text: str) -> list[dict]:
    """응답에서 JSON 배열만 추출 (마크다운 펜스 자동 제거)."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    return json.loads(text.strip())


def process_batch(
    client: anthropic.Anthropic,
    rows: list[dict],
    batch_idx: int,
    total_batches: int,
) -> list[dict]:
    label, desc = get_difficulty(batch_idx, total_batches)
    system_prompt, user_content = build_prompt(rows, label, desc)

    for attempt in range(1, RETRY_MAX + 1):
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            result = parse_response(msg.content[0].text)
            return result
        except json.JSONDecodeError as e:
            print(f"    JSON 파싱 실패 (시도 {attempt}/{RETRY_MAX}): {e}")
            if attempt == RETRY_MAX:
                raise
            time.sleep(2 ** attempt)
        except anthropic.RateLimitError:
            wait = 10 * attempt
            print(f"    Rate limit — {wait}초 대기 후 재시도...")
            time.sleep(wait)
        except anthropic.APIError as e:
            print(f"    API 오류 (시도 {attempt}/{RETRY_MAX}): {e}")
            if attempt == RETRY_MAX:
                raise
            time.sleep(3)


OUTPUT_FIELDS = [
    "lemma", "display_word", "variant", "oxford_pos",
    "meaning_ko", "example_en", "example_ko",
    "card_type", "sense_hint", "split_from", "needs_review",
]


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ 환경변수 ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print("   export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    os.makedirs(PROGRESS_DIR, exist_ok=True)

    # 입력 읽기
    with open(INPUT_FILE, encoding="utf-8-sig") as f:
        all_rows = list(csv.DictReader(f))

    total = len(all_rows)
    batches = [all_rows[i : i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
    total_batches = len(batches)
    print(f"📚 총 {total}개 단어 → {total_batches}개 배치 (배치당 {BATCH_SIZE}개)\n")

    # 이미 처리된 배치 확인
    done = {
        int(f.replace("batch_", "").replace(".json", ""))
        for f in os.listdir(PROGRESS_DIR)
        if f.startswith("batch_") and f.endswith(".json")
    }
    if done:
        print(f"⏭  이미 처리된 배치: {sorted(done)}\n")

    # 배치별 처리
    for i, batch in enumerate(batches):
        progress_file = os.path.join(PROGRESS_DIR, f"batch_{i:03d}.json")
        label, _ = get_difficulty(i, total_batches)

        if i in done:
            print(f"[{i+1:3d}/{total_batches}] ✅ 캐시에서 로드")
            continue

        print(f"[{i+1:3d}/{total_batches}] 처리 중... (난이도: {label}, {len(batch)}개)", end=" ", flush=True)
        try:
            result = process_batch(client, batch, i, total_batches)
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            polysemy_count = sum(1 for r in result if r.get("card_type") == "polysemy_split")
            review_count   = sum(1 for r in result if r.get("needs_review"))
            print(f"→ {len(result)}행 (다의어분리:{polysemy_count}, 검수필요:{review_count})")
        except Exception as e:
            print(f"\n    ❌ 오류로 건너뜀: {e}")
            continue

        time.sleep(SLEEP_SEC)

    # 모든 progress JSON을 합쳐 최종 CSV 생성
    print("\n📝 최종 CSV 생성 중...")
    all_results = []
    review_rows = []

    for i in range(total_batches):
        path = os.path.join(PROGRESS_DIR, f"batch_{i:03d}.json")
        if not os.path.exists(path):
            print(f"  ⚠️  batch_{i:03d}.json 없음 — 건너뜀")
            continue
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
        for j, row in enumerate(rows):
            row["card_id"] = len(all_results) + 1
            all_results.append(row)
            if row.get("needs_review"):
                review_rows.append(row)

    final_fields = ["card_id"] + OUTPUT_FIELDS
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=final_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_results)

    review_file = "needs_review.csv"
    with open(review_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=final_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"\n✅ 완료!")
    print(f"   메인 파일  : {OUTPUT_FILE}  ({len(all_results)}행)")
    print(f"   검수 파일  : {review_file}  ({len(review_rows)}행)")


if __name__ == "__main__":
    main()
