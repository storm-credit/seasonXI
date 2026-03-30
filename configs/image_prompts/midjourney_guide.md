# SeasonXI — Midjourney Image Generation Guide

## 핵심 규칙
- Discord에서 `/imagine` 명령어 사용
- 매번 같은 구조: **Base + Player + Mood + Scene + Parameters**
- 파라미터는 항상 마지막에 붙임

---

## 기본 파라미터 (모든 이미지 공통)
```
--ar 9:16 --v 6.1 --s 750 --q 2
```
| 파라미터 | 의미 |
|---------|------|
| `--ar 9:16` | 쇼츠 세로 비율 |
| `--v 6.1` | Midjourney v6.1 |
| `--s 750` | 스타일 강도 (높을수록 아트워크 느낌) |
| `--q 2` | 퀄리티 최대 |

---

## 프롬프트 구조

```
/imagine [BASE] [PLAYER] [MOOD] [SCENE] --ar 9:16 --v 6.1 --s 750 --q 2
```

---

## BASE (모든 선수 공통)
```
premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark
```

---

## PLAYER BLOCKS (선수별)

### MESSI
```
compact athletic Argentine forward, short dark brown hair, trimmed beard, calm genius expression, low center of gravity, elegant dribbling stance, blue and red vertical striped kit
```

### RONALDO
```
tall muscular Portuguese forward, sharp jawline, short styled dark hair, intense dominant expression, explosive heroic posture, powerful shooting stance, white kit with gold trim
```

### MBAPPE
```
young athletic French forward, short dark hair, focused determined expression, explosive speed energy, dynamic sprinting pose, dark blue kit
```

### SON
```
lean athletic Korean forward, short black hair, clean-shaven, focused determined expression, explosive speed, dynamic left-footed shooting pose, white kit
```

### ZIDANE
```
elegant French midfielder, shaved head, tall graceful build, composed masterful expression, smooth body control, orchestrating pose, white kit
```

### HENRY
```
tall athletic French striker, short dark hair, confident cool expression, explosive speed and power, celebrating or striking pose, red and white kit
```

### RONALDINHO
```
Brazilian attacking midfielder, long curly dark hair, joyful confident smile, creative genius aura, dribbling with flair, blue and red striped kit
```

### SALAH
```
Egyptian forward, dark curly afro hair, short beard, intense focused expression, explosive left-footed cutting inside, red kit
```

### DE BRUYNE
```
Belgian midfielder, ginger-blonde hair, determined intelligent expression, commanding midfield presence, passing or through-ball pose, light blue kit
```

### LEWANDOWSKI
```
tall Polish striker, athletic build, short dark hair, predatory focused expression, clinical finishing posture, red kit
```

### SUAREZ
```
stocky Uruguayan striker, dark hair, short beard, fierce aggressive expression, powerful shooting stance, blue and red striped kit
```

### HAALAND
```
tall imposing Scandinavian striker, long blonde hair tied back, intense predatory expression, raw power aura, brutal forward charge, light blue kit
```

### INIESTA
```
compact Spanish midfielder, receding dark hair, calm intelligent expression, perfect body balance, elegant close control, blue and red striped kit
```

### MODRIC
```
lean Croatian midfielder, long dark blonde hair, composed focused expression, graceful movement, precise passing stance, white kit
```

### KAKA
```
tall elegant Brazilian attacking midfielder, short brown hair, serene confident expression, graceful running stride, smooth dribbling, red and black striped kit
```

### MALDINI
```
tall Italian defender, distinguished short dark hair slightly graying, calm authoritative expression, perfect defensive posture, commanding presence, red and black striped kit
```

### VAN DIJK
```
tall imposing Dutch defender, short dark hair, short beard, calm dominant expression, commanding aerial presence, red kit
```

### NEUER
```
tall German goalkeeper, short blonde hair, intense alert expression, athletic sweeper-keeper stance, commanding presence, dark goalkeeper kit
```

### HAZARD
```
compact Belgian forward, short dark hair, playful confident expression, low center of gravity, explosive dribbling stance, blue kit
```

### AGUERO
```
compact Argentine striker, dark hair, determined clutch expression, explosive finishing posture, celebrating iconic goal, light blue kit
```

### TOTTI
```
Italian forward, slightly longer brown hair, charismatic captain expression, elegant creative stance, regal presence, dark red and gold kit
```

### RIBERY
```
French winger, short dark hair with scar, intense competitive expression, explosive pace energy, cutting inside dribble, red kit
```

### NEYMAR
```
Brazilian forward, styled dark hair with blonde highlights, creative showman expression, flashy dribbling flair, dynamic body movement, dark blue kit with pink accents
```

---

## MOOD BLOCKS (시즌 무드)

### PEAK_MONSTER
```
unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura
```

### ELEGANT_PRIME
```
controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence
```

### BREAKTHROUGH
```
raw hungry energy, emerging talent explosion, electric atmosphere, bright dynamic accents
```

### DECLINE_TRANSITION
```
reflective veteran energy, emotional weight, controlled intensity, quieter powerful tone
```

---

## SCENE BLOCKS

### HOOK (메인 이미지)
```
full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text
```

### CARD (카드용)
```
3/4 body stable composition, player centered, clean readable silhouette, suitable for card frame overlay, slightly less dramatic than hook
```

---

## 30개 시즌 완성 프롬프트 (복붙용)

### Day 1

**1. Messi 2011-12 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, compact athletic Argentine forward, short dark brown hair, trimmed beard, calm genius expression, low center of gravity, elegant dribbling stance, blue and red vertical striped kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**2. Messi 2011-12 CARD**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, compact athletic Argentine forward, short dark brown hair, trimmed beard, calm genius expression, low center of gravity, elegant dribbling stance, blue and red vertical striped kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, 3/4 body stable composition, player centered, clean readable silhouette, suitable for card frame overlay, slightly less dramatic than hook --ar 9:16 --v 6.1 --s 750 --q 2
```

**3. Ronaldo 2016-17 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall muscular Portuguese forward, sharp jawline, short styled dark hair, intense dominant expression, explosive heroic posture, powerful shooting stance, white kit with gold trim, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**4. Ronaldo 2016-17 CARD**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall muscular Portuguese forward, sharp jawline, short styled dark hair, intense dominant expression, explosive heroic posture, powerful shooting stance, white kit with gold trim, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, 3/4 body stable composition, player centered, clean readable silhouette, suitable for card frame overlay, slightly less dramatic than hook --ar 9:16 --v 6.1 --s 750 --q 2
```

**5. Mbappe 2018-19 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, young athletic French forward, short dark hair, focused determined expression, explosive speed energy, dynamic sprinting pose, dark blue kit, raw hungry energy, emerging talent explosion, electric atmosphere, bright dynamic accents, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**6. Mbappe 2018-19 CARD**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, young athletic French forward, short dark hair, focused determined expression, explosive speed energy, dynamic sprinting pose, dark blue kit, raw hungry energy, emerging talent explosion, electric atmosphere, bright dynamic accents, 3/4 body stable composition, player centered, clean readable silhouette, suitable for card frame overlay, slightly less dramatic than hook --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 2

**7. Messi 2014-15 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, compact athletic Argentine forward, short dark brown hair, trimmed beard, calm genius expression, low center of gravity, elegant dribbling stance, blue and red vertical striped kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**8. Ronaldo 2007-08 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall muscular Portuguese forward, sharp jawline, short styled dark hair, intense dominant expression, explosive heroic posture, powerful shooting stance, red kit with white collar, raw hungry energy, emerging talent explosion, electric atmosphere, bright dynamic accents, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**9. Mbappe 2021-22 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, young athletic French forward, short dark hair, focused determined expression, explosive speed energy, dynamic sprinting pose, dark blue kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 3

**10. Zidane 2005-06 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, elegant French midfielder, shaved head, tall graceful build, composed masterful expression, smooth body control, orchestrating pose, white kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**11. Henry 2003-04 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall athletic French striker, short dark hair, confident cool expression, explosive speed and power, celebrating or striking pose, red and white kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**12. Ronaldinho 2005-06 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, Brazilian attacking midfielder, long curly dark hair, joyful confident smile, creative genius aura, dribbling with flair, blue and red striped kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 4

**13. Salah 2017-18 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, Egyptian forward, dark curly afro hair, short beard, intense focused expression, explosive left-footed cutting inside, red kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**14. De Bruyne 2019-20 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, Belgian midfielder, ginger-blonde hair, determined intelligent expression, commanding midfield presence, passing or through-ball pose, light blue kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**15. Son 2021-22 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, lean athletic Korean forward, short black hair, clean-shaven, focused determined expression, explosive speed, dynamic left-footed shooting pose, white kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 5

**16. Lewandowski 2020-21 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall Polish striker, athletic build, short dark hair, predatory focused expression, clinical finishing posture, red kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**17. Suarez 2015-16 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, stocky Uruguayan striker, dark hair, short beard, fierce aggressive expression, powerful shooting stance, blue and red striped kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**18. Haaland 2022-23 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall imposing Scandinavian striker, long blonde hair tied back, intense predatory expression, raw power aura, brutal forward charge, light blue kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 6

**19. Iniesta 2011-12 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, compact Spanish midfielder, receding dark hair, calm intelligent expression, perfect body balance, elegant close control, blue and red striped kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**20. Modric 2017-18 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, lean Croatian midfielder, long dark blonde hair, composed focused expression, graceful movement, precise passing stance, white kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**21. Kaka 2006-07 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall elegant Brazilian attacking midfielder, short brown hair, serene confident expression, graceful running stride, smooth dribbling, red and black striped kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 7

**22. Maldini 2004-05 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall Italian defender, distinguished short dark hair slightly graying, calm authoritative expression, perfect defensive posture, commanding presence, red and black striped kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**23. Van Dijk 2018-19 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall imposing Dutch defender, short dark hair, short beard, calm dominant expression, commanding aerial presence, red kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**24. Neuer 2013-14 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall German goalkeeper, short blonde hair, intense alert expression, athletic sweeper-keeper stance, commanding presence, dark goalkeeper kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 8

**25. Son 2019-20 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, lean athletic Korean forward, short black hair, clean-shaven, focused determined expression, explosive speed, dynamic left-footed shooting pose, white kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**26. Hazard 2018-19 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, compact Belgian forward, short dark hair, playful confident expression, low center of gravity, explosive dribbling stance, blue kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**27. Aguero 2011-12 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, compact Argentine striker, dark hair, determined clutch expression, explosive finishing posture, celebrating iconic goal, light blue kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 9

**28. Totti 2006-07 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, Italian forward, slightly longer brown hair, charismatic captain expression, elegant creative stance, regal presence, dark red and gold kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**29. Ribery 2012-13 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, French winger, short dark hair with scar, intense competitive expression, explosive pace energy, cutting inside dribble, red kit, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**30. Neymar 2017-18 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, Brazilian forward, styled dark hair with blonde highlights, creative showman expression, flashy dribbling flair, dynamic body movement, dark blue kit with pink accents, raw hungry energy, emerging talent explosion, electric atmosphere, bright dynamic accents, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

### Day 10

**31. Messi 2018-19 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, compact athletic Argentine forward, short dark brown hair, trimmed beard, calm genius expression, low center of gravity, elegant dribbling stance, blue and red vertical striped kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**32. Ronaldo 2013-14 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, tall muscular Portuguese forward, sharp jawline, short styled dark hair, intense dominant expression, explosive heroic posture, powerful shooting stance, white kit with gold trim, unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, maximum aura, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

**33. Mbappe 2023-24 HOOK**
```
/imagine premium cinematic football card art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, semi-realistic sports illustration, single male football player, dynamic pose, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark, young athletic French forward, short dark hair, focused determined expression, explosive speed energy, dynamic sprinting pose, dark blue kit, controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, full body dramatic entrance shot, player dominating frame, facing camera, maximum presence, strongest lighting, emerging from darkness, space at top for text --ar 9:16 --v 6.1 --s 750 --q 2
```

---

## 작업 흐름

1. 오늘 만들 선수 확인 (`02_Production/today_queue.md`)
2. 이 파일에서 해당 프롬프트 복사
3. Discord `/imagine` 에 붙여넣기
4. 4장 중 가장 좋은 것 선택 → U1~U4 업스케일
5. 다운로드 → `remotion/public/{player}_{season}_main.png` 저장
6. CARD 프롬프트도 같은 방식
7. Dashboard에서 Render MP4

## 팁
- 맘에 안 들면 같은 프롬프트로 다시 생성 (매번 다른 결과)
- `--s 250`으로 낮추면 더 사실적
- `--s 1000`으로 올리면 더 아트워크
- `--chaos 30` 추가하면 더 다양한 변형
- 특정 포즈 원하면 `running forward`, `celebrating goal`, `dribbling past defender` 등 추가
