# Новые места с оригинальными видео полиции США (проверено 09.10.2026)

**Как проверял.** У каждого места я сам скачал или открыл образец файла:
- длительность и разрешение измерены `ffprobe` по прямой ссылке;
- содержимое zip-архивов прочитано удалённо, без скачивания целиком.

**Нигде не регистрировался, капчи не обходил, ничего не покупал.**

**Исключено всё из вашего списка:** MARTA, Garland, Sauk, San Rafael, SF DPA, COPA, MuckRock и т.д.
Три портала (Окленд, Сан-Диего, Лос-Анджелес) — это города из вашего списка, но **другой источник**: их отдельные порталы NextRequest с файлами, а не страницы прозрачности. Они помечены ⚑.

## Главный приём: порталы NextRequest без логина
У любого портала `*.nextrequest.com` есть открытый список файлов:
`https://<портал>.nextrequest.com/client/documents?search_term=mp4&per_page=100`
Подставьте вместо `mp4` слова `axon`, `bwc`, `body`, `dash`.

Страница файла: `https://<портал>.nextrequest.com/documents/<ID>`. Кнопка Download сразу отдаёт оригинал из облака, **без входа**.

Так я проверил около 1 000 вариантов адресов и нашёл порталы ниже.

---

## Таблица (32 места: 29 полностью новых + 3 ⚑)

| # | штат | агентство | тип | страница | формат и качество (замер) | логин | видео, примерно | что за записи | пример дела → файл |
|---|---|---|---|---|---|---|---|---|---|
| 1 | CA | **Orange County Sheriff** | сайт агентства → облако (Azure) | https://www.ocsheriff.gov/about-ocsheriff/senate-bill-1421 | **zip с mp4**; архивы до 1,3 ГБ (в OIS 20-031243 — 7 камер, по таймкодам в именах ~25–30 мин); в части архивов только документы | нет | **141 архив**: стрельба 48, применение силы 28, чрезмерная сила 25, нечестность 34, др. | бодикамы и камеры машин нескольких депутатов, видео из тюрьмы, допросы | OIS 20-031243, 7 камер: https://cpraazlrshotprod1.blob.core.usgovcloudapi.net/cpraprod1/Mediazip/Critical%20Incident/OIS%2020-031243.zip · чрезмерная сила 16-149 (тюремные камеры и допрос): https://cpraazlrshotprod1.blob.core.usgovcloudapi.net/cpraprod1/Mediazip/SF-Unreasonable%20or%20Excessive%20Force/SF%20of%20Excessive%20Force%2016-149.zip |
| 2 | CA | **Santa Ana PD** | NextRequest | https://cityofsantaanaca.nextrequest.com | mp4 **1280×720**, файлы **30–67 мин**, 0,7–1,4 ГБ | нет | ≥66 | бытовые вызовы («415FAM» — семейная ссора), K9, смерть под стражей | K9 / применение силы, 30.07.2023, 11 файлов: https://cityofsantaanaca.nextrequest.com/requests/25-2623 → 67 мин: https://cityofsantaanaca.nextrequest.com/documents/56081924 · ICD 2018, 42 мин: https://cityofsantaanaca.nextrequest.com/documents/23518939 |
| 3 | CA | **Richmond PD** | NextRequest | https://cityofrichmondca.nextrequest.com | **zip с mp4**: 0,6 ГБ (5 камер) и 3,7 ГБ (**12 камер**) | нет | 6 архивов | аресты, бодикамы всех офицеров на месте | арест Deonte Cormier, 26.05.2024, 5 камер: https://cityofrichmondca.nextrequest.com/documents/39965650 · дело 23-5256, 12 камер: https://cityofrichmondca.nextrequest.com/documents/36694352 |
| 4 | CA | **Martinez PD** | NextRequest | https://cityofmartinezca.nextrequest.com | mp4 720p (с редактурой), один файл **3 ч 03 мин** | нет | ≥61 | стрельба 18.08.2023: 54 файла (бодикамы, сцена, внутреннее расследование) | https://cityofmartinezca.nextrequest.com/requests/25-70 → https://cityofmartinezca.nextrequest.com/documents/43707801 |
| 5 | CA | **Chico PD** | NextRequest | https://cityofchicoca.nextrequest.com | 720p бодикам (63 мин), **1080p** видео очевидца, допросы 800×600 | нет | ≥82 | 3 громких дела с несколькими ракурсами и допросами | Tyler Rushing, 2017, 28 файлов: https://cityofchicoca.nextrequest.com/requests/21-29 → 63 мин: https://cityofchicoca.nextrequest.com/documents/6987086 · Stephen Vest, 2020, 17 файлов: https://cityofchicoca.nextrequest.com/requests/21-30 |
| 6 | WA | **Lakewood PD** | NextRequest | https://cityoflakewoodwa.nextrequest.com | Axon Body 4 **1152×864** (47 мин); видеорегистратор 1344×540 до **2 ч 17 мин** | нет | ≥99 | дело о младенце 2026 (15 файлов), смертельное ДТП, вызовы | https://cityoflakewoodwa.nextrequest.com/documents/68209107 · ДТП (видеорегистратор, 44 мин): https://cityoflakewoodwa.nextrequest.com/documents/32823533 |
| 7 | CA | **Fairfield PD** | NextRequest | https://fairfieldcapd.nextrequest.com | 720p, **53–64 мин** | нет | ≥28 | **погоня + стрельба 2022** (28 файлов); применение силы 2023; уличная камера 1080p | https://fairfieldcapd.nextrequest.com/requests/22-1 → https://fairfieldcapd.nextrequest.com/documents/16200454 |
| 8 | OH | **Guernsey County Sheriff** | NextRequest | https://guernseycountysheriff-oh.nextrequest.com | Axon Body 2/3 720p + камера в машине (Fleet IR); до **83 мин** | нет | ≥60 (37 дел) | **бытовые вызовы**: проверка самочувствия, ссоры, рапорты депутатов | проверка самочувствия, 17.03.2022: https://guernseycountysheriff-oh.nextrequest.com/documents/15132392 · ночной вызов, 29.01.2023 (24 мин): https://guernseycountysheriff-oh.nextrequest.com/documents/17736302 |
| 9 | CA | **West Sacramento PD** | NextRequest | https://westsacramento.nextrequest.com | 720p, **24–70 мин** | нет | 6 бодикамов + камеры машин | смертельная стрельба: Роберт Коулман, 88 лет, 2020 | https://westsacramento.nextrequest.com/requests/20-208 → 70 мин: https://westsacramento.nextrequest.com/documents/5823725 |
| 10 | CA | **Pasadena PD** | сайт → **Google Drive** (открытая папка) | https://www.cityofpasadena.net/police/news/pasadena-police-department-releases-video-related-to-march-2-officer-involved-shooting/ | mp4 **720p**, по 1–4 мин, всего 22 файла | нет | 17 бодикамов + 5 камер в машинах (MAV) | стрельба 02.03.2026, станция Sierra Madre Villa | папка: https://drive.google.com/drive/folders/1msMk_THxbbNajNIXndnFCfY_OXP36vM3 · ещё папка «RECORDINGS → Video/Audio» по другому делу: https://drive.google.com/drive/folders/1aptZccIbAM-mEl0u0NA-nm3E5U44QOJR (не проверено) · на сайте есть Vimeo-плееры, но скачать оттуда нельзя |
| 11 | Federal | **CBP** (пограничная служба) | DVIDS (федеральный хостинг) | https://www.dvidshub.net/feature/CBPbodyworncamera | mp4 **1920×1080**, до **17,8 мин** | нет | ≥4 на странице | бодикамы применения силы CBP | https://d34w7g4gy10iej.cloudfront.net/video/2505/DOD_111018230/DOD_111018230.mp4 |
| 12 | CA | **Shasta County** (шериф) | NextRequest | https://shastacountyca.nextrequest.com | 720p бодикам **67 мин**; камеры наблюдения 2688×1520 | нет | ≥11 полицейских (108 видео всего) | вызовы на адрес (7 файлов); **дело Шерри Папини** (16 файлов) | https://shastacountyca.nextrequest.com/documents/56078517 · Папини: https://shastacountyca.nextrequest.com/requests/25-129 |
| 13 | CA | **National City PD** | NextRequest | https://cityofnationalcityca.nextrequest.com | 720p, видео со сцены **94 мин** | нет | ≥17 (44 в папке SB 1421) | стрельбы | https://cityofnationalcityca.nextrequest.com/documents/22798857 · https://cityofnationalcityca.nextrequest.com/documents/18617904 |
| 14 | CA | **Oceanside PD** | NextRequest | https://cityofoceansideca.nextrequest.com | Axon Body 4 720p (14–22 мин); видеорегистратор 1344×540 до **5 ч** | нет | ≥39 | расчистка лагеря бездомных, аресты, бодикамы + видеорегистраторы | https://cityofoceansideca.nextrequest.com/documents/70472475 · https://cityofoceansideca.nextrequest.com/documents/59321035 |
| 15 | CA | **Modesto PD** | NextRequest | https://cityofmodestoca.nextrequest.com | 720p бодикам + **уличные камеры города** (PTZ 1080p) | нет | ≥40 | инцидент 18.05.2021: бодикамы + уличные камеры (10 файлов в запросе) | https://cityofmodestoca.nextrequest.com/requests/22-187 → https://cityofmodestoca.nextrequest.com/documents/14217735 |
| 16 | CA | **Humboldt County Sheriff** | NextRequest | https://humboldtgov.nextrequest.com | 720×480 – **1080p**; допросы 44 мин, камера в машине (MAV) | нет | ≥47 (папка «Sheriff's Office Audio/Video Redactions») | стрельбы, допросы, камеры в машинах | MAV: https://humboldtgov.nextrequest.com/documents/12717313 · 1080p: https://humboldtgov.nextrequest.com/documents/12717399 |
| 17 | RI | **Providence PD** | NextRequest | https://providenceri.nextrequest.com | 720p, короткие (1,5–8 мин) | нет | ≥54 | общественные беспорядки, ссора в баре с членом горсовета, «драка у клуба» | https://providenceri.nextrequest.com/requests/20-725 → https://providenceri.nextrequest.com/documents/5341642 |
| 18 | OH | **Clermont County Sheriff** | NextRequest | https://clermontcountysheriffoh.nextrequest.com | 720p бодикам, **1080p** камеры тюрьмы; 2–6 мин | нет | ≥37 | охраннику тюрьмы предъявлено нападение (2026); дело Chad Essert (обвинение 2026, бодикамы депутатов) | https://clermontcountysheriffoh.nextrequest.com/requests/26-3727 → https://clermontcountysheriffoh.nextrequest.com/documents/70374453 |
| 19 | IL | **Berwyn PD** | NextRequest | https://cityofberwynilpolice.nextrequest.com | Axon Body 3 720p, **11–25 мин** | нет | 4+ | рапорт 24-10341 (8 файлов); вызов 2025 | https://cityofberwynilpolice.nextrequest.com/documents/41121559 |
| 20 | NC | **Fayetteville PD** | NextRequest | https://fayettevillenc.nextrequest.com | 720p, по ~10 мин × 4 | нет | 4 | задержание Ja'Lana Dunlap, 06.09.2022 (выпущено по решению суда) | https://fayettevillenc.nextrequest.com/requests/22-1958 → https://fayettevillenc.nextrequest.com/documents/16035841 |
| 21 | FL | **City of Miami** (не Miami-Dade) | NextRequest | https://miami.nextrequest.com | Axon Body 2 720p (**26–28 мин**); бодикамы инспекторов **1080p** | нет | ≥14 | выезды инспекторов с полицией | https://miami.nextrequest.com/documents/7057126 · 1080p: https://miami.nextrequest.com/documents/57894589 |
| 22 | CA | **Pittsburg PD** | NextRequest | https://pittsburgcapd.nextrequest.com | ⚠️ 2016 г. — **640×480** (ниже нормы); есть Axon Body 3 2022 | нет | ≥48 | дело 16-5211 (24 мин), дело 22-1682 | https://pittsburgcapd.nextrequest.com/documents/1713478 |
| 23 | CA | **Port of San Diego Harbor Police** | сайт → облако (Azure) | https://www.portofsandiego.org/public-safety/transparency-disclosures | zip 0,64 ГБ: 4 бодикама | нет | 1 дело | дело 22-04232 (09.10.2022) | https://pantheonstorage.blob.core.windows.net/public-safety/PSDHPD-10-09-2022-case22-04232-videos.zip |
| 24 | CA | Vallejo PD | NextRequest | https://vallejo.nextrequest.com | 720p, короткие | нет | ≥7 | бодикамы свидетелей / офицеров | https://vallejo.nextrequest.com/documents/22955913 |
| 25 | CA | Napa PD | NextRequest | https://cityofnapaca.nextrequest.com | брифинг 1080p (13 мин, смонтирован); бодикам 720p (11 мин) | нет | ≥14 | стрельба на Vineyard Terrace; арест | https://cityofnapaca.nextrequest.com/documents/13151045 |
| 26 | CA | Cathedral City PD | NextRequest | https://cathedralcityca.nextrequest.com | 720/1080p, 4–5 мин (смонтировано) | нет | 6 | стрельба 2023 | https://cathedralcityca.nextrequest.com/documents/35912208 |
| 27 | TX | Temple PD | NextRequest | https://cityoftempletx.nextrequest.com | 720p камера в машине, ~4 мин | нет | ≥16 | стрельба (Michael Dean, 2019) | https://cityoftempletx.nextrequest.com/documents/7070770 |
| 28 | OH | Dayton (город) | NextRequest | https://cityofdaytonoh.nextrequest.com | **1080p**, 4 мин | нет | 1 | погоня 24.04.2024 | https://cityofdaytonoh.nextrequest.com/documents/33210682 |
| 29 | CA | Escondido PD | NextRequest | https://cityofescondidoca.nextrequest.com | 1246×940 обход места преступления; допрос 640×480 | нет | 9 | дело 2013 г. | https://cityofescondidoca.nextrequest.com/documents/36706211 |
| 30 ⚑ | CA | Oakland (портал города) | NextRequest | https://oaklandca.nextrequest.com | **1080p** (стрельба 2026), 720p | нет | ≥83 | стрельба 13.07.2026 на International Blvd; допросы по жалобам на силу | https://oaklandca.nextrequest.com/documents/68707502 |
| 31 ⚑ | CA | San Diego (портал города) | NextRequest | https://sandiego.nextrequest.com | 720p, видео по смерти под стражей 27 мин | нет | ≥37 | смерть под стражей 2018 | https://sandiego.nextrequest.com/documents/10854669 |
| 32 ⚑ | CA | Los Angeles (портал города, LAPD) | NextRequest | https://lacity.nextrequest.com | 720×480 – 720p; камера в машине до **3 ч** | нет | ≥52 | смерть под стражей 2012 (камера в машине), стрельба 2020 (бодикам) | https://lacity.nextrequest.com/documents/25390774 · https://lacity.nextrequest.com/documents/5790626 |

---

## Не проверено (нужен вход или файлы не видны)
- **Long Beach PD (CA)**: SB 1421 лежат в GovQA → «My Request Center», нужна регистрация жителя. https://longbeachcapd.govqa.us/WEBAPP/_rs/supporthome.aspx
- **Pomona PD (CA)**: страница SB 1421 + GovQA; файлы без входа не видны. https://www.pomonaca.gov/government/departments/police-department/transparency/senate-bill-1421-releases
- **Pasadena PD, папка «RECORDINGS»** (дело на странице briefings): подпапки Video/Audio видны, файлы не проверены.

## Проверено — НЕ подходит (чтобы не тратить время)
- **Только YouTube или встроенные плееры:** Westminster PD (CA), Fullerton PD (CA), Riverside County Sheriff (CA), Menifee PD (CA), Boulder County DA (CO), Castle Rock PD (CO), Humboldt — страница сайта (файлы шерифа есть на NextRequest, см. №16).
- **Только PDF:** Weld County DA (CO), DA 23rd Judicial District (CO), Westminster PD (CO), San Diego County DA.
- **Не полиция:** Lynnwood WA, Trumbull County OH (камеры мэрии и здания), Santa Fe County NM, Washoe NV, Tracy, Cupertino, Placer, Sutter, Mendocino и т.д. (заседания, стройка).
- **Суд по делу Кармело Энтони (Collin County, TX):** официальной ссылки на файлы не найдено, только пересказы СМИ.

---

## 10 лучших мест (польза: длинные записи + история + несколько камер + качество)
1. **Orange County Sheriff (CA)** — 141 архив, на дело до 7 камер; есть применение силы и тюрьма, а не только стрельба.
2. **Santa Ana PD (CA)** — записи 30–67 мин, семейные вызовы и K9, много камер на дело.
3. **Richmond PD (CA)** — архив дела с 12 бодикамами (3,7 ГБ).
4. **Chico PD (CA)** — 3 громких дела, бодикамы + видео очевидцев 1080p + допросы.
5. **Fairfield PD (CA)** — погоня со стрельбой, 28 файлов по ~1 часу.
6. **Lakewood PD (WA)** — Axon Body 4 1152×864, длинные записи, смертельное ДТП, дело о младенце.
7. **Guernsey County Sheriff (OH)** — 37 обычных вызовов (проверки, ссоры), записи до 83 мин; ровно та «бытовуха», что нужна.
8. **Martinez PD (CA)** — 54 файла по одной стрельбе, до 3 ч.
9. **West Sacramento PD (CA)** — дело Роберта Коулмана (88 лет), 6 камер, до 70 мин.
10. **CBP через DVIDS** — единственный источник с честным **1080p** и прямыми mp4; плюс **Pasadena** (22 файла по свежей стрельбе 2026 г., бодикамы и камеры в машинах).

## Честно о пределах
- Нужно было минимум 40 мест, нашёл и проверил **32** (из них 3 ⚑). Остальные кандидаты либо только на YouTube, либо только в PDF, либо за логином. Они перечислены выше, чтобы не тратить на них время.
- **1080p редко бывает в исходниках:** большинство бодикамов Axon экспортируются в 720p. 1080p есть у CBP/DVIDS, свежих файлов Окленда, видео очевидцев (Chico), тюремных камер (Clermont) и уличных камер (Modesto).
- Это публичные записи, но в них реальные люди. Перед публикацией размывайте лица посторонних и несовершеннолетних и не показывайте адреса.
