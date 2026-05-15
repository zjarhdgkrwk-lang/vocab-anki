"""vocab_all.csv에서 needs_review=TRUE 행을 수정한다."""
import csv, os

SRC = "data/output/vocab_all.csv"
DST = "data/output/vocab_all.csv"

FIELDNAMES = [
    "lemma","display_word","variant","oxford_pos",
    "meaning_ko","example_en","example_ko",
    "card_type","sense_hint","split_from","needs_review",
]

def row(lemma, display_word, variant, oxford_pos,
        meaning_ko, example_en, example_ko,
        card_type="normal", sense_hint="", split_from="", needs_review="FALSE"):
    return dict(lemma=lemma, display_word=display_word, variant=variant,
                oxford_pos=oxford_pos, meaning_ko=meaning_ko,
                example_en=example_en, example_ko=example_ko,
                card_type=card_type, sense_hint=sense_hint,
                split_from=split_from, needs_review=needs_review)


# 각 lemma별 처리 규칙
# True → 해당 행을 대체할 row 목록 반환
# False → 해당 행 in-place 수정

def fix_past(r):
    return [
        row("past","past","","adj.|n.|prep.",
            "과거의 / 과거","She talked about her past.",
            "그녀는 자신의 과거에 대해 이야기했어요.",
            "polysemy_split","(과거)","past"),
        row("past","past","","adj.|n.|prep.",
            "~을 지나서","Walk past the school on the left.",
            "학교를 지나 왼쪽으로 가세요.",
            "polysemy_split","(지나서)","past"),
    ]

def fix_lie(r):
    return [
        row("lie","lie","","v.",
            "거짓말하다","He lied to his mother.",
            "그는 어머니에게 거짓말을 했어요.",
            "polysemy_split","(거짓말하다)","lie"),
        row("lie","lie","","v.",
            "눕다","She lay on the sofa to rest.",
            "그녀는 소파에 누워서 쉬었어요.",
            "polysemy_split","(눕다)","lie"),
    ]

def fix_bar(r):
    return [
        row("bar","bar","","n.",
            "술집","He had a drink at the bar.",
            "그는 술집에서 음료를 마셨어요.",
            "polysemy_split","(술집)","bar"),
        row("bar","bar","","n.",
            "막대기 / 바","She grabbed the metal bar.",
            "그녀는 금속 막대기를 잡았어요.",
            "polysemy_split","(막대기)","bar"),
    ]

def fix_pitch(r):
    return [
        row("pitch","pitch","","n.",
            "음높이","Her voice has a high pitch.",
            "그녀의 목소리는 음이 높아요.",
            "polysemy_split","(음높이)","pitch"),
        row("pitch","pitch","","n.",
            "경기장","The boys play on the football pitch.",
            "남자아이들이 축구장에서 놀아요.",
            "polysemy_split","(경기장)","pitch"),
    ]

def fix_moderate(r):
    return [
        row("moderate","moderate","","adj.|n.|v.",
            "적당한 / 온건한","She exercises at a moderate pace.",
            "그녀는 적당한 속도로 운동해요.",
            "polysemy_split","(적당한)","moderate"),
        row("moderate","moderate","","adj.|n.|v.",
            "조절하다 / 사회를 맡다","She moderated the class discussion.",
            "그녀가 수업 토론을 진행했어요.",
            "polysemy_split","(조절하다)","moderate"),
    ]

def fix_tender(r):
    return [
        row("tender","tender","","adj.|n.|v.",
            "부드러운 / 다정한","The meat was very tender.",
            "그 고기는 매우 부드러웠어요.",
            "polysemy_split","(부드러운)","tender"),
        row("tender","tender","","adj.|n.|v.",
            "제출하다 / 입찰하다","She tendered her resignation.",
            "그녀는 사직서를 제출했어요.",
            "polysemy_split","(제출하다)","tender"),
    ]

def fix_intimate(r):
    return [
        row("intimate","intimate","","adj.|n.|v.",
            "친밀한 / 가까운","She talked with her intimate friend.",
            "그녀는 친밀한 친구와 이야기했어요.",
            "polysemy_split","(친밀한)","intimate"),
        row("intimate","intimate","","adj.|n.|v.",
            "넌지시 알리다","He intimated that he would leave.",
            "그는 떠날 것이라고 넌지시 알렸어요.",
            "polysemy_split","(넌지시 알리다)","intimate"),
    ]

# in-place 수정 목록: (lemma판별키) → 수정할 필드 dict
INPLACE = {
    "opposite": {"meaning_ko": "반대의 / 반대편", "needs_review": "FALSE"},
    "FALSE":    {"lemma": "false", "display_word": "false",
                 "oxford_pos": "adj.", "meaning_ko": "거짓의 / 틀린",
                 "example_en": "That information is false.",
                 "example_ko": "그 정보는 틀린 거예요.", "needs_review": "FALSE"},
    "o?™clock": {"lemma": "o'clock", "display_word": "o'clock",
                 "example_en": "We eat lunch at twelve o'clock.",
                 "example_ko": "우리는 12시 정각에 점심을 먹어요.", "needs_review": "FALSE"},
    "double":   {"needs_review": "FALSE"},
    "peak":     {"meaning_ko": "정점 / 최고조", "needs_review": "FALSE"},
    "gay":      {"needs_review": "FALSE"},
    "parallel": {"needs_review": "FALSE"},
    "damn":     {"needs_review": "FALSE"},
    "bang":     {"needs_review": "FALSE"},
    "trunk":    {"meaning_ko": "(나무) 줄기 / 트렁크", "needs_review": "FALSE"},
    "declension": {"meaning_ko": "어형 변화", "needs_review": "FALSE"},
    "faculty":  {"needs_review": "FALSE"},
    "pat":      {"needs_review": "FALSE"},
    "programmatic": {"needs_review": "FALSE"},
}

SPLIT_HANDLERS = {
    "past":     fix_past,
    "lie":      fix_lie,
    "bar":      fix_bar,
    "pitch":    fix_pitch,
    "moderate": fix_moderate,
    "tender":   fix_tender,
    "intimate": fix_intimate,
}

rows_in = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
rows_out = []
stats = {"split": 0, "fixed": 0, "unchanged": 0}

for r in rows_in:
    if r["needs_review"] != "TRUE":
        rows_out.append(r)
        stats["unchanged"] += 1
        continue

    lemma = r["lemma"]

    if lemma in SPLIT_HANDLERS:
        new_rows = SPLIT_HANDLERS[lemma](r)
        rows_out.extend(new_rows)
        stats["split"] += 1
        print(f"  분리: {lemma} → {len(new_rows)}행")
    elif lemma in INPLACE:
        for k, v in INPLACE[lemma].items():
            r[k] = v
        rows_out.append(r)
        stats["fixed"] += 1
        print(f"  수정: {lemma}")
    else:
        r["needs_review"] = "FALSE"
        rows_out.append(r)
        stats["unchanged"] += 1
        print(f"  기본처리: {lemma}")

with open(DST, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows_out)

print(f"\n완료: {len(rows_in)}행 → {len(rows_out)}행")
print(f"  분리: {stats['split']}건, 수정: {stats['fixed']}건")
