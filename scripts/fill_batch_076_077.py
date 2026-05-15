import csv
import os

FIELDNAMES = [
    "lemma","display_word","variant","oxford_pos",
    "meaning_ko","example_en","example_ko",
    "card_type","sense_hint","split_from","needs_review",
]

def w(lemma, display_word, variant, oxford_pos,
      meaning_ko, example_en, example_ko,
      card_type="normal", sense_hint="", split_from="", needs_review="FALSE"):
    return dict(lemma=lemma, display_word=display_word, variant=variant,
                oxford_pos=oxford_pos, meaning_ko=meaning_ko,
                example_en=example_en, example_ko=example_ko,
                card_type=card_type, sense_hint=sense_hint,
                split_from=split_from, needs_review=needs_review)

ROWS_076 = [
    # swell: adj.|n.|v. → 3 POS + n./v. meanings differ → polysemy_split
    w("swell","swell","","adj.|n.|v.",
      "부풀다 / 붓다","My feet swell in hot weather.","더운 날씨에 발이 부어요.",
      "polysemy_split","(붓다)","swell"),
    w("swell","swell","","adj.|n.|v.",
      "훌륭한","She is a swell teacher.","그녀는 훌륭한 선생님이에요.",
      "polysemy_split","(훌륭한)","swell"),

    w("swift","swift","","adj.",
      "빠른","The swift bird flew away.","빠른 새가 날아갔어요."),
    w("symphony","symphony","","n.",
      "교향곡","She plays in a symphony.","그녀는 교향악단에서 연주해요."),
    w("tag","tag","","n.|v.",
      "꼬리표 / 태그하다","She put a tag on the bag.","그녀는 가방에 꼬리표를 붙였어요."),
    w("tease","tease","","n.|v.",
      "놀리다","He teases his little sister.","그는 여동생을 놀려요."),
    w("telegraph","telegraph","","n.|v.",
      "전보 / 전보를 치다","He sent a telegraph to his father.","그는 아버지에게 전보를 보냈어요."),
    w("temple","temple","","n.",
      "사원 / 관자놀이","We visited an old temple.","우리는 오래된 사원을 방문했어요."),
    w("tempt","tempt","","v.",
      "유혹하다","The cake tempts me every day.","케이크가 매일 저를 유혹해요."),
    w("tenant","tenant","","n.",
      "세입자","The tenant pays rent each month.","세입자는 매달 집세를 내요."),
    w("terminal","terminal","","adj.|n.",
      "터미널 / 말기의","We met at the airport terminal.","우리는 공항 터미널에서 만났어요."),
    w("terminate","terminate","","v.",
      "끝내다 / 종료하다","The contract will terminate next month.","계약이 다음 달에 끝나요."),
    w("terrace","terrace","","n.|v.",
      "테라스","We eat on the terrace.","우리는 테라스에서 식사해요."),
    w("terrific","terrific","","adj.",
      "훌륭한 / 멋진","She did a terrific job.","그녀는 정말 잘했어요."),
    w("terror","terror","","n.",
      "공포","He felt terror in the dark.","그는 어둠 속에서 공포를 느꼈어요."),
    w("thorough","thorough","","adj.",
      "철저한","She is a thorough worker.","그녀는 철저하게 일해요."),
    w("thread","thread","","n.|v.",
      "실 / 실을 꿰다","She threads a needle carefully.","그녀는 조심히 바늘에 실을 꿰어요."),
    w("thrill","thrill","","n.|v.",
      "짜릿함 / 흥분시키다","The movie gave me a thrill.","그 영화가 저를 짜릿하게 했어요."),
    w("thumb","thumb","","n.|v.",
      "엄지손가락","He hurt his thumb.","그는 엄지손가락을 다쳤어요."),
    w("tick","tick","","n.|v.",
      "체크 표시 / 진드기","Please put a tick in the box.","칸에 체크 표시를 해주세요."),
    w("tidy","tidy","","adj.|v.",
      "깔끔한 / 정리하다","She tidied her room after school.","그녀는 학교 후에 방을 정리했어요."),
    w("timber","timber","","n.",
      "목재","He built the house with timber.","그는 목재로 집을 지었어요."),
    w("torture","torture","","n.|v.",
      "고문 / 고통","The long wait was torture.","긴 기다림은 고통이었어요."),
    w("toss","toss","","n.|v.",
      "던지다","He tossed the ball to me.","그가 저에게 공을 던졌어요."),
    w("toxic","toxic","","adj.",
      "독성의 / 유해한","This plant is toxic to cats.","이 식물은 고양이에게 유해해요."),
    w("tragic","tragic","","adj.",
      "비극적인","The story has a tragic ending.","그 이야기는 비극적인 결말이에요."),
    w("transact","transact","","v.",
      "거래하다","We transacted business online.","우리는 온라인으로 거래했어요."),
    w("transmit","transmit","","v.",
      "전달하다 / 전송하다","He transmitted the message quickly.","그는 메시지를 빠르게 전달했어요."),
    w("treasure","treasure","","n.|v.",
      "보물 / 소중히 여기다","I treasure this old photo.","저는 이 오래된 사진을 소중히 여겨요."),
    w("treaty","treaty","","n.",
      "조약 / 협약","The two countries signed a treaty.","두 나라가 조약을 맺었어요."),
    w("tremendous","tremendous","","adj.",
      "엄청난","She made a tremendous effort.","그녀는 엄청난 노력을 했어요."),
    w("tribe","tribe","","n.",
      "부족","The tribe lives near the river.","그 부족은 강 근처에 살아요."),

    # trim: adj.|n.|v. → 3 POS + meanings differ → polysemy_split
    w("trim","trim","","adj.|n.|v.",
      "다듬다 / 자르다","He trimmed his beard.","그는 수염을 다듬었어요.",
      "polysemy_split","(다듬다)","trim"),
    w("trim","trim","","adj.|n.|v.",
      "날씬한 / 잘 정돈된","She has a trim figure.","그녀는 날씬한 몸매예요.",
      "polysemy_split","(날씬한)","trim"),

    w("triumph","triumph","","n.|v.",
      "승리 / 이겨내다","She triumphed over her illness.","그녀는 병을 이겨냈어요."),
    w("turnover","turnover","","n.",
      "이직률 / 매출액","The store has high turnover.","그 가게는 매출이 높아요."),
    w("ultimate","ultimate","","adj.|n.",
      "궁극의 / 최고의","This is my ultimate goal.","이것이 저의 궁극적인 목표예요."),
    w("unaware","unaware","","adj.",
      "모르는 / 인식하지 못하는","She was unaware of the problem.","그녀는 문제를 알지 못했어요."),
    w("undermine","undermine","","v.",
      "약화시키다 / 무너뜨리다","Stress can undermine your health.","스트레스는 건강을 약화시킬 수 있어요."),
    w("unify","unify","","v.",
      "통합하다 / 하나로 합치다","Music can unify people.","음악은 사람들을 하나로 합칠 수 있어요."),
    w("unprecedented","unprecedented","","adj.",
      "전례 없는","It was an unprecedented event.","그것은 전례 없는 사건이었어요."),
    w("urgent","urgent","","adj.",
      "긴급한","I got an urgent call from my son.","아들에게서 긴급 전화가 왔어요."),
    w("utilize","utilize","utilise","v.",
      "활용하다","She utilizes her free time well.","그녀는 자유 시간을 잘 활용해요."),
    w("utter","utter","","adj.|v.",
      "완전한 / 말하다","She did not utter a word.","그녀는 한 마디도 하지 않았어요."),
    w("vacate","vacate","","v.",
      "비우다 / 떠나다","Please vacate the room by noon.","정오까지 방을 비워주세요."),
    w("vaccine","vaccine","","n.",
      "백신","The child got a vaccine today.","아이가 오늘 백신을 맞았어요."),
    w("vacuum","vacuum","","n.|v.",
      "진공청소기 / 청소하다","She vacuums the floor every day.","그녀는 매일 바닥을 청소기로 청소해요."),
    w("vague","vague","","adj.",
      "막연한 / 불분명한","His answer was very vague.","그의 대답은 매우 불분명했어요."),
    w("valid","valid","","adj.",
      "유효한","My passport is still valid.","제 여권은 아직 유효해요."),
    w("vanish","vanish","","v.",
      "사라지다","The cat vanished into the garden.","고양이가 정원으로 사라졌어요."),
    w("verbal","verbal","","adj.",
      "말로 하는 / 언어의","She gave verbal instructions.","그녀는 말로 설명해줬어요."),
    w("verse","verse","","n.",
      "시 / 절","She read a verse from the book.","그녀는 책에서 한 절을 읽었어요."),
    w("vertical","vertical","","adj.|n.",
      "수직의","Draw a vertical line here.","여기에 수직선을 그으세요."),
    w("veterinarian","veterinarian","","n.",
      "수의사","The veterinarian helped my dog.","수의사가 제 개를 치료해줬어요."),
    w("vigor","vigor","","n.",
      "활력 / 힘","She works with great vigor.","그녀는 활력 넘치게 일해요."),
    w("vigorous","vigorous","","adj.",
      "활발한 / 힘찬","He does vigorous exercise daily.","그는 매일 활발하게 운동해요."),
    w("virgin","virgin","","adj.|n.",
      "처음의 / 손대지 않은","This is virgin territory for me.","이것은 저에게 처음 해보는 영역이에요."),
    w("virtue","virtue","","n.",
      "덕 / 미덕","Honesty is a great virtue.","정직함은 훌륭한 미덕이에요."),
    w("vivid","vivid","","adj.",
      "생생한 / 선명한","She has a vivid memory of that day.","그녀는 그날의 기억이 생생해요."),
    w("vocabulary","vocabulary","","n.",
      "어휘 / 단어","She has a large vocabulary.","그녀는 어휘가 풍부해요."),
    w("vocation","vocation","","n.",
      "직업 / 소명","Teaching is her vocation.","가르치는 것이 그녀의 소명이에요."),
    w("warehouse","warehouse","","n.|v.",
      "창고","The goods are in the warehouse.","상품들이 창고에 있어요."),
]

ROWS_077 = [
    # warrant: n.|v. with completely different meanings → polysemy_split
    w("warrant","warrant","","n.|v.",
      "영장 / 근거","The police had a search warrant.","경찰은 수색 영장이 있었어요.",
      "polysemy_split","(영장)","warrant"),
    w("warrant","warrant","","n.|v.",
      "정당화하다","His action does not warrant this.","그의 행동은 이것을 정당화하지 않아요.",
      "polysemy_split","(정당화하다)","warrant"),

    w("weave","weave","","n.|v.",
      "짜다 / 엮다","She weaves baskets by hand.","그녀는 손으로 바구니를 짜요."),
    w("weed","weed","","n.|v.",
      "잡초 / 잡초를 뽑다","She weeds the garden every morning.","그녀는 매일 아침 정원의 잡초를 뽑아요."),
    w("wheat","wheat","","n.",
      "밀","Bread is made from wheat.","빵은 밀로 만들어요."),
    w("whip","whip","","n.|v.",
      "채찍 / 빠르게 젓다","She whips cream for the cake.","그녀는 케이크를 위해 크림을 저어요."),
    w("wicked","wicked","","adj.",
      "나쁜 / 사악한","The wicked witch cast a spell.","사악한 마녀가 마법을 걸었어요."),
    w("wit","wit","","n.",
      "재치","He always speaks with great wit.","그는 항상 재치 있게 말해요."),
    w("worship","worship","","n.|v.",
      "숭배하다 / 예배하다","They worship at the temple.","그들은 사원에서 예배해요."),
    w("wreck","wreck","","n.|v.",
      "망가뜨리다 / 잔해","The storm wrecked our boat.","폭풍이 우리 배를 망가뜨렸어요."),
]


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def append_review(rows, path):
    review = [r for r in rows if r["needs_review"] == "TRUE"]
    if not review:
        return
    exists = os.path.exists(path) and os.path.getsize(path) > 0
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        writer.writerows(review)


REVIEW_PATH = "data/output/review/polysemy_review.csv"

write_csv(ROWS_076, "data/output/filled/batch_076_filled.csv")
append_review(ROWS_076, REVIEW_PATH)
n_in, n_out = 60, len(ROWS_076)
print(f"처리 완료: batch_076.csv ({n_in}행 → {n_out}행)")

write_csv(ROWS_077, "data/output/filled/batch_077_filled.csv")
append_review(ROWS_077, REVIEW_PATH)
n_in, n_out = 9, len(ROWS_077)
print(f"처리 완료: batch_077.csv ({n_in}행 → {n_out}행)")
