# 어머니 Anki 영어 단어장 프로젝트

## 프로젝트 개요
영어를 처음 배우는 한국 성인 여성(60대 이상)을 위한 Anki 단어 카드 제작.
입력 CSV를 읽고 한국어 뜻·예문·해석을 추가하여 출력 CSV를 생성한다.

## 입력 컬럼
- lemma: 기본형
- display_word: 카드에 표시할 형태
- variant: 변형형 (예: an)
- oxford_pos: 품사

## 출력 컬럼 (추가)
- meaning_ko: 한국어 뜻
- example_en: 영어 예문
- example_ko: 예문 한국어 해석
- card_type: normal | function_word | polysemy_split
- sense_hint: 다의어 구분 힌트 (필요시)
- split_from: 다의어 분리 시 원본 lemma
- needs_review: TRUE/FALSE

## 한국어 뜻(meaning_ko) 작성 규칙
1. 최대 2개까지만. 3개 이상이면 needs_review=TRUE로 표시
2. 구어적이고 자연스러운 한국어. "~하다" 형태 선호
3. 형식: 뜻1 / 뜻2 (슬래시로 구분)
4. 예: "먹다 / 식사하다" ❌ → "먹다" ✅ (중복 의미는 하나로)

## 예문(example_en) 작성 규칙
1. A1~A2 난이도. 8단어 이하 권장
2. 예문에 쓰이는 단어는 최대한 NGSL 1000 이내
3. 주어는 I / She / He / We / The boy/girl 등 구체적 인물
4. 추상적 예문 금지 ("This concept is important." 같은 것)
5. 일상생활 소재: 가족, 음식, 집, 학교, 날씨, 감정

## 기능어 처리 규칙 (card_type=function_word)
대상: be, do, have, to, in, on, at, of, for, from, by, with, as, that, this, it,
      the, a, there, what, which, who, where, when, how, some, any, all, both,
      each, one, other, another, will, can, may, must, should, would, could
처리 방법:
- meaning_ko: 가장 핵심 용법 1~2가지만
- example_en: 그 용법을 명확히 보여주는 문장 1개
- 완벽한 설명보다 "아, 이런 때 쓰는 말이구나"를 전달하는 예문

## 다의어 분리 규칙
### 분리하는 경우 (card_type=polysemy_split)
다음 조건 중 2개 이상 해당하면 행을 추가 분리한다:
- oxford_pos에 n.|v. 조합이 있고, 명사/동사 뜻이 전혀 다름
- oxford_pos에 품사가 3개 이상 (n.|v.|adj.)
- 한국어 뜻이 달라서 예문 하나로 설명 불가

분리 예시:
  book(n.) → 책  / book(v.) → 예약하다
  light(n.) → 빛 / light(adj.) → 가벼운, 밝은

### 분리하지 않는 경우
- n.|v. 이지만 뜻이 연결됨: show(n. 쇼 / v. 보여주다) → 한 카드
- adj.|adv. 조합: 대부분 한 카드로 유지

분리 시 행 추가 방법:
- 원본 행 유지, 새 행 추가
- split_from 컬럼에 원본 lemma 기입
- sense_hint로 구분: "(책)" / "(예약하다)"

## 처리 우선순위 단어 목록 (특별 주의)
다의어 후보:
book, bank, light, right, kind, present, close, second, match, mean,
watch, spring, fall, case, form, order, sound, point, line, date,
change, turn, work, play, run, set, check, note, save, serve, state,
park, rock, train, fair, act, break, leave, miss, class

## Batch 처리 방법
1. data/batches/ 폴더의 미처리 batch CSV를 읽는다
2. 위 규칙에 따라 컬럼을 채운다
3. data/output/filled/ 폴더에 같은 파일명으로 저장한다
4. needs_review=TRUE인 행은 data/output/review/polysemy_review.csv에도 추가 저장한다
5. 처리 완료 후 "처리 완료: batch_XXX.csv (N행 → M행)" 형태로 보고한다

## 절대 금지
- 너무 어려운 단어가 들어간 예문 (B2 이상 단어 사용 금지)
- "It is important to..." 형태의 추상적 예문
- 한국어 직역투 해석 ("나는 간다" → "저는 가요" 수준이 적절)
- meaning_ko에 영어 포함
- 3개 이상 의미를 한 카드에 쑤셔넣기
