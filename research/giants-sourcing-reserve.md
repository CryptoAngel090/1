# Тотальный резерв: где гиганты берут материал и как сделать так, чтобы он у нас никогда не кончался

Дата: 09.10.2026.

**Метод.**
- Прочитаны описания 500 последних роликов 20 крупнейших каналов ниши.
- Через открытый API порталов NextRequest проверены **тексты запросов публичных записей**, которые сами каналы подают в полицию: 65+ порталов, тысячи запросов.

Всё ниже основано на этих данных. Выводы помечены как вывод.

---

## 1. Главный секрет: у гигантов не «источник», а КОНВЕЙЕР запросов

На тех же порталах, где мы берём видео, видно, как работают большие каналы.

| Что нашёл | Цифры |
|---|---|
| Запросов, где каналы прямо пишут «для моего YouTube-канала» | **2 473** на **82** порталах |
| Из них только за 2026 г. | **1 224** (в 2021 — 278, в 2024 — 107): гонка ускоряется |
| Шаблон «on behalf of my educational YouTube channel… BWC, 911, CCTV, interrogation» (**ArrestFlix**, ссылается на канал Police Insider, 1,24M) | **553** запроса на 43 порталах, 513 из них в 2026 г. |
| Шаблон «as a member of the Media acting in the best interest of the public… interview / interrogation / 911 / dash / CCTV» | **531** запрос на 48 порталах (2025–2026) |
| Шаблон «Dashcam and bodycam video for the **first two squads/officers** on scene…» с трекером **ClickUp** — **Midwest Safety** (4,8M) | 242 запроса с этим шаблоном на 23 порталах; 130 со ссылкой на ClickUp, **129 из них подписаны Midwest** |
| **Detective Williams** (Verda Studios, 792K): запросы по громким делам (Rust/Болдуин и др.) | 59 запросов на 12+ порталах |
| Arkansas Police Activity и др. мелкие каналы | десятки запросов |

### Как устроен конвейер (по текстам их запросов)
1. **Отбор дел:** по сообщениям об арестах, пресс-релизам, новостям и уже существующим роликам. В шаблоне так и пишут: *«Existing YouTube video of incident, for reference»*. В запросе указаны имя подозреваемого, дата, статья.
2. **Узкий и дешёвый запрос:** только «первые два экипажа + арестовавший офицер + рапорт / probable cause». Личные данные разрешают вырезать.
3. **Просьба отдать то, что уже выложено:** *«If that redacted video still exists, you can just send us that version»*. Так ведомство отвечает быстрее и бесплатно.
4. **Фильтр брака:** *«If the individual was NOT arrested on camera… we will likely cancel the request»*.
5. **Трекинг:** у Midwest каждая заявка — отдельная задача в ClickUp, ссылка вставлена прямо в запрос.
6. **Объём:** сотни открытых запросов одновременно в десятках ведомств. Часть отваливается, но поток видео идёт постоянно.
7. **География:** больше всего таких запросов на порталах San Diego (301), City of Miami (299), Los Angeles (233), Oakland (221), Humboldt (144), Lakewood WA (121). Там законы требуют выдавать видео (CPRA / SB 1421 / AB 748 в Калифорнии, Chapter 119 во Флориде, RCW 42.56 в Вашингтоне, Georgia ORA).

> **Вывод:** у гигантов материал «всегда есть» не потому, что у них секретный источник, а потому что у них **постоянно открыты 100–300 запросов**, и каждую неделю что-то приходит.

---

## 2. Все каналы поставки — что использует каждый гигант (по их описаниям)

| Источник | Кто использует (доказательство) |
|---|---|
| **Запросы публичных записей (FOIA/CPRA/Ch.119)** | Sergeant Curtis: *«This footage was obtained through public records requests»*. Body Cam Watch: *«obtained directly from the relevant law enforcement agency»*. STAYAWAKE: *«FOIA requested and/or purchased»*. Midwest, Police Insider/ArrestFlix, Detective Williams — по запросам на порталах |
| **Официальные релизы ведомств** (critical incident, YouTube ведомств) | PoliceActivity, Law&Crime, Real World Police («exclusive… never-before-seen footage», меморандумы прокуратуры, Brady List) |
| **Судебные записи** (процессы, допросы) | JCS: *«Courtroom footage sourced from @lawandcrime»*; STAYAWAKE: «trial footage» |
| **Лицензионные библиотеки** | Most Dangerous (публичный список лицензий на pastebin): Shutterstock, Wikimedia Commons, **DVIDS**, Envato, **Jukin Media**, Prelinger, Creative Commons, госархивы (DoD, NPS, NOAA) |
| **Присланное зрителями и коллаборации** | Hampton Law: форма «If you have body cam footage… submit it here»; Audit the Audit: «Submit your video» + коллабы с аудиторами; Midwest: форма TIPS; Code Blue Cam: tip@codebluecam.com |
| **Партнёрство с полицейскими структурами** | Code Blue Cam: *«Proudly partnered with the Wisconsin Professional Police Association»* |
| **Реакции и разборы чужих видео** | Sheriff Lamb: *«This video is from Breaking Body Cams»*, реакция на чужие ролики |
| **Защита канала** (чтобы источники не отрезали) | Midwest: «Right to be Forgotten» + форма удаления; Code Blue: «Reconsideration Policy»; Body Cam Watch: длинный блок «Value-Add Editing» о трансформации исходника |

---

## 3. НАШ резерв — что уже готово и работает

### 3.1. Мониторинг чужих запросов (бесплатный «пылесос»)
Когда ведомство отвечает на чей-то запрос (Midwest, ArrestFlix и т.д.), файл становится **публичным** на портале. Его может скачать любой.

- `tools/nextrequest_watch.py` проходит по 65 порталам и выдаёт свежие полицейские видео со ссылками.
- `tools/nextrequest_portals.txt` — список порталов (дополняйте).
- **Прогон прямо сейчас (`research/reserve-90days.md`): 86 файлов по 31 делу, выложенных за последние 90 дней.** Это материал, который можно брать сегодня.

Запуск раз в неделю:
```
python3 tools/nextrequest_watch.py --days 7 --out research/reserve-week.md
```

### 3.2. Постоянные архивы (запас на месяцы)
Из `foxusacam-new-sources-2.md`: шериф Ориндж (141 архив), Santa Ana, Richmond, Chico, Martinez, Fairfield, Lakewood WA, Guernsey SO, West Sacramento, CBP/DVIDS и др.

### 3.3. Свой конвейер запросов (как у гигантов, но честно)
**Цель:** всегда 30–50 открытых запросов; каждую неделю подавать 10–15 новых.

**Где брать дела:**
- пресс-релизы полиции и шерифов об арестах (DUI, погони, бытовые с арестом);
- судебные новости;
- уже вышедшие критические инциденты, где выложено не всё.

**Шаблон запроса A — арест или погоня** (заменить [..]):
```
Hello, this is a public records request under [state law, e.g. the California Public Records Act / Florida Statutes Chapter 119].

I run Fox USA Cam, a documentary YouTube channel that publishes full, contextual cases about real police incidents.

Requesting:
1. Body-worn camera and dashcam (ICV) video from the first two officers/units on scene and from the arresting officer.
2. The primary officer's narrative / probable cause statement.
3. 911 call audio and CAD log, if releasable.

If a redacted version of this video has already been released, that version is perfectly fine and saves your staff time.
You may redact any PII. If the subject was not arrested on camera, please let me know and I may withdraw the request.

Incident: [suspect name], arrested [date], [location], charges: [charges], case # [if known].
Electronic delivery preferred. Thank you!
```

**Шаблон B — полный кейс для длинного ролика:** то же, плюс:
```
4. Interview/interrogation video of the suspect.
5. Surveillance/CCTV and drone video collected for the case.
```

**Правила, которые мы взяли у гигантов:**
1. Узкий запрос: первые экипажи и арестовавший офицер.
2. Принимаем «уже выложенную» версию.
3. Каждый запрос — отдельная строка в таблице: дата подачи, ведомство, статус, срок, ссылка. Подойдёт обычная Google-таблица.
4. Пишем честно, кто мы. Не называемся СМИ, если ведомство требует подтверждения.

### 3.4. Бесплатные запасные линии
- **DVIDS** (CBP, федеральные бодикамы, 1080p).
- **Официальные критические инциденты** ведомств. Брать только как исходник ведомства, не перезаливать чужой монтаж.
- **Форма «Пришлите видео»** в описании канала (как у Hampton Law / Audit the Audit). Брать **только записи, полученные человеком законно**: например, его собственный ответ на запрос или видео с его камеры. Утёкшие записи не брать.

### 3.5. Платные линии (только как идея, ничего не покупать)
Jukin Media / Trusted Media Brands, ViralHog, Newsflare, Storyful — лицензирование вирусных роликов. Их использует Most Dangerous. Для бодикамов они не нужны, но пригодятся для погонь и видео очевидцев.

---

## 4. Недельный цикл «никогда без материала»
| День | Действие |
|---|---|
| Пн | Запуск `nextrequest_watch.py --days 7` → разобрать новые файлы, отметить 2–3 кандидата в ролики |
| Вт | Подать 10–15 новых запросов по шаблонам A/B (выбор дел по пресс-релизам) |
| Ср | Проверить ответы и статусы, скачать готовое, обновить таблицу |
| Чт | Проверить постоянные архивы (OC Sheriff, Santa Ana, Chico и т.д.) на новые дела |
| Пт | Проверить DVIDS и официальные релизы ведомств за неделю |

**Целевой запас:** 8–10 готовых кейсов на будущие ролики. Тогда график «2 ролика в неделю» не сорвётся.

## 5. Важно
- **Чужие перезаливы и чужой монтаж не брать** (PoliceActivity, Law&Crime и т.п.). Брать только исходники ведомств и своё оформление.
- **Видео, выложенное по чужому запросу, — публичная запись,** брать его законно. Но не копировать чужой ролик или текст.
- **Размывать** несовершеннолетних, жертв, адреса и номера. Держать форму на удаление, как у Midwest и Code Blue: она снижает число жалоб и страйков.
