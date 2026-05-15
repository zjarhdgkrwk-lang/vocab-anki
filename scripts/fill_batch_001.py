import csv
import os

FILLED_PATH = "data/output/filled/batch_001_filled.csv"
REVIEW_PATH = "data/output/review/polysemy_review.csv"

FIELDNAMES = [
    "lemma", "display_word", "variant", "oxford_pos",
    "meaning_ko", "example_en", "example_ko",
    "card_type", "sense_hint", "split_from", "needs_review",
]

# fmt: off
ROWS = [
    # ── 기능어 (function_word) ──────────────────────────────────────────────
    dict(lemma="the",    display_word="the",  variant="",   oxford_pos="definite article",
         meaning_ko="그, 그 ~",
         example_en="The dog is cute.",        example_ko="그 개는 귀여워요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="be",     display_word="be",   variant="",   oxford_pos="auxiliary v.|v.",
         meaning_ko="~이다 / ~있다",
         example_en="I am happy.",             example_ko="저는 행복해요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="and",    display_word="and",  variant="",   oxford_pos="conj.",
         meaning_ko="그리고",
         example_en="I like cats and dogs.",   example_ko="저는 고양이와 개를 좋아해요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="of",     display_word="of",   variant="",   oxford_pos="prep.",
         meaning_ko="~의",
         example_en="She drinks a glass of water.", example_ko="그녀는 물 한 잔을 마셔요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="to",     display_word="to",   variant="",   oxford_pos="infinitive marker|prep.",
         meaning_ko="~에 / ~하기 위해",
         example_en="I want to eat.",          example_ko="저는 먹고 싶어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="a",      display_word="a",    variant="an", oxford_pos="indefinite article",
         meaning_ko="하나의 / 어떤 ~",
         example_en="I have a dog.",           example_ko="저는 개 한 마리가 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="in",     display_word="in",   variant="",   oxford_pos="adv.|prep.",
         meaning_ko="~안에 / ~에서",
         example_en="She is in the kitchen.",  example_ko="그녀는 부엌에 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="have",   display_word="have", variant="",   oxford_pos="v.",
         meaning_ko="가지다 / 먹다(식사)",
         example_en="I have a cat.",           example_ko="저는 고양이가 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="it",     display_word="IT",   variant="",   oxford_pos="pron.",
         meaning_ko="그것 / (날씨·시간 주어)",
         example_en="It is cold today.",       example_ko="오늘은 추워요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="you",    display_word="you",  variant="",   oxford_pos="pron.",
         meaning_ko="당신 / 너",
         example_en="You are my friend.",      example_ko="당신은 제 친구예요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="he",     display_word="he",   variant="",   oxford_pos="pron.",
         meaning_ko="그 (남자)",
         example_en="He is my brother.",       example_ko="그는 제 오빠예요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="for",    display_word="for",  variant="",   oxford_pos="prep.",
         meaning_ko="~을 위해 / ~동안",
         example_en="This is for you.",        example_ko="이건 당신을 위한 거예요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="they",   display_word="they", variant="",   oxford_pos="pron.",
         meaning_ko="그들",
         example_en="They are my friends.",    example_ko="그들은 제 친구예요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="not",    display_word="not",  variant="",   oxford_pos="adv.",
         meaning_ko="~않다 / ~아니다",
         example_en="I am not tired.",         example_ko="저는 피곤하지 않아요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="that",   display_word="that", variant="",   oxford_pos="conj.|det.|pron.",
         meaning_ko="저 ~ / 그것",
         example_en="That is my book.",        example_ko="저건 제 책이에요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="we",     display_word="we",   variant="",   oxford_pos="pron.",
         meaning_ko="우리",
         example_en="We eat together.",        example_ko="우리는 함께 먹어요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="on",     display_word="on",   variant="",   oxford_pos="adv.|prep.",
         meaning_ko="~위에 / ~에(날짜·요일)",
         example_en="The book is on the table.", example_ko="책이 탁자 위에 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="with",   display_word="with", variant="",   oxford_pos="prep.",
         meaning_ko="~와 함께 / ~로",
         example_en="I eat with my family.",   example_ko="저는 가족과 함께 먹어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="this",   display_word="this", variant="",   oxford_pos="det.|pron.",
         meaning_ko="이것 / 이 ~",
         example_en="This is my bag.",         example_ko="이건 제 가방이에요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="i",      display_word="I",    variant="",   oxford_pos="pron.",
         meaning_ko="나 / 저",
         example_en="I love my family.",       example_ko="저는 가족을 사랑해요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="do",     display_word="do",   variant="",   oxford_pos="auxiliary v.|v.",
         meaning_ko="~하다 / (의문·부정 조동사)",
         example_en="Do you like fish?",       example_ko="생선 좋아해요?",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="as",     display_word="as",   variant="",   oxford_pos="prep.",
         meaning_ko="~로서 / ~처럼",
         example_en="She works as a teacher.", example_ko="그녀는 선생님으로 일해요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="at",     display_word="at",   variant="",   oxford_pos="prep.",
         meaning_ko="~에(장소·시간)",
         example_en="She is at home.",         example_ko="그녀는 집에 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="she",    display_word="she",  variant="",   oxford_pos="pron.",
         meaning_ko="그녀",
         example_en="She is my sister.",       example_ko="그녀는 제 언니예요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="but",    display_word="but",  variant="",   oxford_pos="conj.",
         meaning_ko="하지만 / 그런데",
         example_en="I like cats, but he likes dogs.", example_ko="저는 고양이를 좋아하지만, 그는 개를 좋아해요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="from",   display_word="from", variant="",   oxford_pos="prep.",
         meaning_ko="~에서 / ~부터",
         example_en="He is from Korea.",       example_ko="그는 한국에서 왔어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="by",     display_word="by",   variant="",   oxford_pos="prep.",
         meaning_ko="~옆에 / ~에 의해",
         example_en="Sit by me.",              example_ko="제 옆에 앉아요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="will",   display_word="will", variant="",   oxford_pos="modal v.",
         meaning_ko="~할 거예요",
         example_en="I will go home.",         example_ko="저는 집에 갈 거예요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="or",     display_word="or",   variant="",   oxford_pos="conj.",
         meaning_ko="또는 / 아니면",
         example_en="Tea or coffee?",          example_ko="차요, 아니면 커피요?",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="say",    display_word="say",  variant="",   oxford_pos="v.",
         meaning_ko="말하다",
         example_en="She says hello.",         example_ko="그녀는 안녕이라고 말해요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="go",     display_word="go",   variant="",   oxford_pos="v.",
         meaning_ko="가다",
         example_en="I go to school.",         example_ko="저는 학교에 가요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="so",     display_word="so",   variant="",   oxford_pos="adv.|conj.",
         meaning_ko="그래서 / 매우",
         example_en="I am tired, so I sleep.", example_ko="피곤해서 자요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="all",    display_word="all",  variant="",   oxford_pos="det.|pron.",
         meaning_ko="모든 / 전부",
         example_en="All students are here.",  example_ko="모든 학생이 여기 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="if",     display_word="if",   variant="",   oxford_pos="conj.",
         meaning_ko="만약 ~라면",
         example_en="If it rains, we stay home.", example_ko="비가 오면 집에 있어요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="one",    display_word="one",  variant="",   oxford_pos="det.|number|pron.",
         meaning_ko="하나의 / 한 명",
         example_en="I have one sister.",      example_ko="저는 언니가 한 명 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="would",  display_word="would",variant="",   oxford_pos="modal v.",
         meaning_ko="~하겠어요 / ~하고 싶어요",
         example_en="I would like some tea.",  example_ko="차를 마시고 싶어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="about",  display_word="about",variant="",   oxford_pos="adv.|prep.",
         meaning_ko="~에 대해 / 약",
         example_en="Tell me about your family.", example_ko="가족에 대해 말해줘요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="can",    display_word="can",  variant="",   oxford_pos="modal v.",
         meaning_ko="~할 수 있다",
         example_en="She can swim.",           example_ko="그녀는 수영할 수 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="which",  display_word="which",variant="",   oxford_pos="det.|pron.",
         meaning_ko="어느 / 어떤 것",
         example_en="Which bag is yours?",     example_ko="어느 가방이 당신 거예요?",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="there",  display_word="there",variant="",   oxford_pos="adv.",
         meaning_ko="거기에 / ~이 있다",
         example_en="There is a cat.",         example_ko="고양이 한 마리가 있어요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="know",   display_word="know", variant="",   oxford_pos="v.",
         meaning_ko="알다",
         example_en="I know her name.",        example_ko="저는 그녀의 이름을 알아요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="more",   display_word="more", variant="",   oxford_pos="adv.|det.|pron.",
         meaning_ko="더 / 더 많은",
         example_en="I want more rice.",       example_ko="밥을 더 먹고 싶어요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="get",    display_word="get",  variant="",   oxford_pos="v.",
         meaning_ko="얻다 / 받다",
         example_en="I got a gift.",           example_ko="저는 선물을 받았어요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="who",    display_word="who",  variant="",   oxford_pos="pron.",
         meaning_ko="누가 / 누구",
         example_en="Who is she?",             example_ko="그녀는 누구예요?",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    # ── 다의어 분리: like (입력 CSV에 이미 prep./v. 두 행으로 존재) ─────────
    dict(lemma="like",   display_word="like", variant="",   oxford_pos="prep.",
         meaning_ko="~처럼",
         example_en="She sings like a bird.",  example_ko="그녀는 새처럼 노래해요.",
         card_type="polysemy_split", sense_hint="(~처럼)", split_from="like", needs_review="FALSE"),

    dict(lemma="like",   display_word="like", variant="",   oxford_pos="v.",
         meaning_ko="좋아하다",
         example_en="I like apples.",          example_ko="저는 사과를 좋아해요.",
         card_type="polysemy_split", sense_hint="(좋아하다)", split_from="like", needs_review="FALSE"),

    dict(lemma="when",   display_word="when", variant="",   oxford_pos="adv.|conj.|pron.",
         meaning_ko="언제 / ~할 때",
         example_en="When do you eat?",        example_ko="언제 밥 먹어요?",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="think",  display_word="think",variant="",   oxford_pos="v.",
         meaning_ko="생각하다",
         example_en="I think she is kind.",    example_ko="그녀가 친절하다고 생각해요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="make",   display_word="make", variant="",   oxford_pos="v.",
         meaning_ko="만들다",
         example_en="She makes dinner.",       example_ko="그녀는 저녁을 만들어요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="time",   display_word="time", variant="",   oxford_pos="n.",
         meaning_ko="시간 / 번",
         example_en="What time is it?",        example_ko="지금 몇 시예요?",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="see",    display_word="see",  variant="",   oxford_pos="v.",
         meaning_ko="보다",
         example_en="I see a bird.",           example_ko="저는 새를 봐요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="what",   display_word="what", variant="",   oxford_pos="det.|pron.",
         meaning_ko="무엇 / 어떤",
         example_en="What do you want?",       example_ko="무엇을 원해요?",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="up",     display_word="up",   variant="",   oxford_pos="adv.|prep.",
         meaning_ko="위로 / 위에",
         example_en="She looks up at the sky.", example_ko="그녀는 하늘을 올려다봐요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="some",   display_word="some", variant="",   oxford_pos="det.|pron.",
         meaning_ko="몇몇 / 약간의",
         example_en="I want some water.",      example_ko="물을 좀 원해요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="other",  display_word="other",variant="",   oxford_pos="adj.|pron.",
         meaning_ko="다른 / 나머지",
         example_en="I like other foods too.", example_ko="저는 다른 음식도 좋아해요.",
         card_type="function_word", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="out",    display_word="out",  variant="",   oxford_pos="adv.|prep.",
         meaning_ko="밖으로 / 밖에",
         example_en="He goes out.",            example_ko="그는 밖에 나가요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="good",   display_word="good", variant="",   oxford_pos="adj.",
         meaning_ko="좋은",
         example_en="She is a good cook.",     example_ko="그녀는 요리를 잘해요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="people", display_word="people",variant="",  oxford_pos="n.",
         meaning_ko="사람들",
         example_en="Many people eat here.",   example_ko="많은 사람들이 여기서 먹어요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="year",   display_word="year", variant="",   oxford_pos="n.",
         meaning_ko="해 / 년",
         example_en="I am ten years old.",     example_ko="저는 열 살이에요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),

    dict(lemma="take",   display_word="take", variant="",   oxford_pos="v.",
         meaning_ko="가져가다 / 타다",
         example_en="Take this bag.",          example_ko="이 가방을 가져가요.",
         card_type="normal", sense_hint="", split_from="", needs_review="FALSE"),
]
# fmt: on

os.makedirs(os.path.dirname(FILLED_PATH), exist_ok=True)
os.makedirs(os.path.dirname(REVIEW_PATH), exist_ok=True)

with open(FILLED_PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(ROWS)

review_rows = [r for r in ROWS if r["needs_review"] == "TRUE"]
review_file_exists = os.path.exists(REVIEW_PATH)
with open(REVIEW_PATH, "a", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if not review_file_exists:
        writer.writeheader()
    writer.writerows(review_rows)

n_in = 61  # 원본 행 수 (헤더 제외, like가 2행이므로 61-1=60단어)
n_out = len(ROWS)
print(f"처리 완료: batch_001.csv ({n_in-1}행 → {n_out}행)")
print(f"  function_word: {sum(1 for r in ROWS if r['card_type']=='function_word')}")
print(f"  polysemy_split: {sum(1 for r in ROWS if r['card_type']=='polysemy_split')}")
print(f"  normal: {sum(1 for r in ROWS if r['card_type']=='normal')}")
print(f"  needs_review=TRUE: {len(review_rows)}")
