# План статического сайта Elegoo CC FAQ

Исходное исследование: 1 ноября 2026. Варианты сайта исследовал отдельный фоновый агент без чтения `data/`; тематический разбор архива выполнялся отдельно. Ниже сохранён исходный план.

Актуальные договорённости о независимой публикации на https://demshin.github.io/elegoo-cc/ находятся в [плане публикации](publication-plan.md). Описания отсутствующих Git/CI ниже относятся к моменту исходного исследования.

**Состояние02.11.2026:** первая локальная версия реализована на Astro7.4.4 / Starlight0.42.8. Собраны65 статей и11 навигационных/справочных страниц, проверены ссылки, исключение исходного архива и русский поиск. Успешно проверен вариант с префиксом `/elegoo_cc_faq`. Браузерныйhost недоступен, поэтому мобильная и визуальная проверка остаются невыполненными. [Сборка и проверки](../site/README.md). Каталог не является Git-репозиторием; origin, CI и публикация не настроены.

## Рекомендация

**Astro Starlight + GitHub Pages**, стандартная тема с небольшой настройкой CSS и одной главной страницей. Статьи остаются обычными Markdown в `faq/`. Один небольшой скрипт готовит временное публичное дерево из явного списка файлов, добавляет метаданные и преобразует ссылки. Генерируемую копию не храним в Git и не редактируем вручную.

Это чуть больше первоначальной настройки, чем простейший VitePress, но после учёта связанных evidence-реестров и приватных ссылок этап подготовки нужен обоим. У Starlight полезные для проекта готовые преимущества: русский интерфейс и Pagefind с поддержкой русского языка и стемминга. Свой фронтенд, CMS, сервер и внешний поисковый сервис не нужны. [Starlight: поиск](https://starlight.astro.build/guides/site-search/), [локализация интерфейса](https://starlight.astro.build/guides/i18n/), [Pagefind: языки](https://pagefind.app/docs/multilingual/).

## Сравнение

| Вариант | Что подходит | Цена интеграции и ограничения |
| --- | --- | --- |
| **Starlight — основной** | Документационный дизайн, тематический sidebar, локальный Pagefind, русский UI и стемминг | У каждой страницы обязателен YAML `title`; штатный `docsLoader()` читает `src/content/docs/`. Добавляем title из H1 при подготовке временных файлов. |
| **VitePress — разумная альтернатива** | Обычный Markdown; title из H1; source directory настраивается; sidebar и локальный MiniSearch | Прямое `srcDir: './faq'` НЕ решает ссылки в `docs/` и README. Нужны тот же отбор публичных источников и преобразование ссылок. Русскую морфологию по умолчанию не обещаем: документация подтверждает fuzzy search, локализацию UI и настраиваемую обработку терминов. |
| **Material for MkDocs — не выбирать для нового проекта** | Хорошая готовая документационная тема, Markdown и локальный поиск, русский язык | Официально объявлен EOL 5 мая 2027, предлагается преемник Zensical. Начинать сейчас с будущей миграции невыгодно. |

Первичные источники: [Starlight: обязательный title](https://starlight.astro.build/reference/frontmatter/), [Starlight: docsLoader и его options](https://starlight.astro.build/reference/configuration/#docsloader), [VitePress: source directory и H1-title](https://vuejs.github.io/vitepress/v1/reference/site-config), [VitePress: MiniSearch](https://vuejs.github.io/vitepress/v1/reference/default-theme-search), [Material: EOL](https://squidfunk.github.io/mkdocs-material/getting-started/).

При реализации закрепить стабильные совместимые версии и lockfile. Номера версий сверить на момент установки; примеры из документации предварительных выпусков не переносить автоматически.

## Публичное содержимое: явный allowlist

Разрешать только перечисленные ниже исходники. Не обходить весь репозиторий с последующим blacklist. Новая статья попадает на сайт после добавления в список публикации.

```text
faq/first-layer-adhesion.md
faq/debris-under-build-plate.md
faq/web-interface-recovery.md
faq/centauri/cc1-remote-access.md
faq/centauri/cc1-hotend-damage.md
faq/centauri/cc1-filament-loading.md
faq/centauri/printer-ip-address.md
faq/centauri/cc1-bed-mesh-viewer.md
faq/filament/drying-and-storage.md
faq/filament/asa-layer-separation.md
faq/filament/tpu-feed-path.md
faq/printing/warping-and-brim.md
faq/printing/nozzle-clog.md
faq/slicing/flow-ratio.md
faq/slicing/temperature-tower.md
faq/slicing/support-removal.md
faq/slicing/overhang-walls.md
faq/slicing/vase-wall-gaps.md
faq/slicing/profile-baseline.md
faq/slicing/small-part-cooling-time.md
faq/centauri/cc2-extrusion-1243.md
faq/centauri/heating-error-103.md
faq/slicing/seam-placement.md
faq/printing/elephant-foot.md
faq/centauri/first-layer-z-offset.md
faq/centauri/cc1-build-plate-selection.md
faq/centauri/bed-leveling-502.md
faq/centauri/z-axis-binding.md
faq/centauri/toolhead-cover-rattle.md
faq/centauri/axis-noise.md
faq/centauri/mainboard-fan-noise.md
faq/centauri/cc1-idle-noise.md
faq/centauri/cc1-exhaust-fan-control.md
faq/centauri/cc1-antivibration-feet.md
faq/centauri/cc1-vented-riser.md
faq/centauri/cc1-nozzle-light.md
faq/centauri/cc2-ptfe-release.md
faq/filament/feed-resistance.md
faq/slicing/manual-color-change.md
faq/centauri/cc2-printer-busy.md
faq/centauri/cc2-lan-connection.md
faq/centauri/slicer-firmware-compatibility.md
faq/centauri/white-screen-recovery.md
faq/centauri/cc2-offline-firmware-update.md
faq/centauri/file-upload-failure.md
faq/printing/extruder-grip.md
faq/slicing/arc-preview.md
faq/slicing/model-mesh-repair.md
faq/slicing/pressure-advance.md
faq/slicing/scarf-seam.md
faq/slicing/fuzzy-skin.md
faq/slicing/surface-wall-gaps.md
faq/slicing/ironing.md
faq/slicing/bridges.md
faq/slicing/travel-scratches-z-hop.md
faq/centauri/cc1-full-build-area.md
faq/centauri/cc1-printhead-communication.md
faq/centauri/cc1-fan-703.md
faq/centauri/cc1-first-layer-height.md
docs/evidence.md
docs/evidence-more.md
docs/evidence-expanded.md
docs/evidence-qa.md
docs/evidence-history.md
docs/sources.md
```

README использовать как источник структуры главной, но не публиковать автоматически целиком: в нём есть служебные разделы. Проще одна короткая публичная `site/home.md`, явно добавленная в allowlist; она содержит описание, поиск/темы и ссылки «Новичку» / «Опытному». Альтернатива — строго определённые публичные разделы README, однако извлечение по заголовкам добавляет зависимость от его структуры. Навигационный manifest может одновременно задавать allowlist, темы и подписи, чтобы не поддерживать второй список статей в конфиге темы.

Из ассетов разрешать только конкретные проверенные файлы будущего `site/public/` (favicon/logo/собственные иллюстрации/локальные шрифты). Не копировать вложения чата и не разрешать произвольные файлы по расширению из корня. Сборка читает только публичные Markdown, проверенные ассеты и собственный код конфигурации. `data/`, `.agents/`, `.codex/`, сырые JSON/HTML, индексы, вложения, рабочие журналы и прочие `docs/` не являются входом сайта.

Важно: исключение из меню или поискового индекса не скрывает страницу. Для приватных данных требуется отсутствие в публичном дереве и deploy artifact.

## Один небольшой подготовительный скрипт

Предлагаемая схема, без реализации сейчас:

1. Очистить только свою игнорируемую генерируемую папку `site/src/content/docs/`.
2. Прочитать только manifest allowlist. Для каждого файла сохранить стабильный ID страницы и исходный путь.
3. Добавить Starlight YAML `title` из первого H1; убрать дублирующий H1 только в генерируемой версии. Остальные заголовки и смысл статьи не менять.
4. Переложить выбранные файлы в публичное дерево и переписать Markdown-ссылки по явной таблице source path → public route. Сохранять якоря. Неизвестная внутренняя ссылка останавливает подготовку, а не тянет новый файл в публикацию.
5. В evidence-страницах заменить локальные ссылки `data/.../messagesN.html#messageID` на текстовые архивные указатели. Не читать цели этих ссылок, не копировать HTML и не пытаться сделать их доступными посетителю.
6. Проверить пути и ссылки, затем вызвать обычную сборку Starlight. Получается только `site/dist/`, включая публичный поисковый индекс.

Пример устойчивой карты маршрутов:

| Исходник | Публичный путь |
| --- | --- |
| `site/home.md` | `/` |
| `faq/filament/drying-and-storage.md` | `/faq/filament/drying-and-storage/` |
| `docs/evidence.md` | `/sources/pilot/` |
| `docs/evidence-more.md` | `/sources/topics/` |
| `docs/sources.md` | `/sources/` |

Все URL учитывают настроенный project base. Относительные ссылки сначала разрешаются относительно **исходного** файла, затем переводятся через карту маршрутов. Так `../../README.md`, `../../docs/evidence-more.md#dry` и ссылки между статьями не ломаются после перемещения. Служебные ссылки README на карту покрытия и процесс отбора в публичную главную не переносить.

Свой `glob({base: './faq'})` вместо `docsLoader()` не предлагать как гарантированную штатную интеграцию Starlight: documented loader не имеет настройки base. Генерируемое дерево сохраняет стандартный путь темы и упрощает обновления. [Документация loader](https://starlight.astro.build/reference/configuration/#docsloader).

## Как показывать источники

Публичный FAQ сохраняет ссылки на обезличенные реестры случаев. Реестр показывает ID случая, дату/период, модель и условия, что именно подтвердил участник и ограничения вывода. Официальные руководства остаются обычными внешними ссылками.

Пример публичного указателя: `ADH-02 · архив чата, messages7.html, message34282 · исходная переписка не публикуется`. Это указатель для локальной перепроверки, а не обещание посетителю открыть оригинал. Полный путь выгрузки и ссылка `../data/...` посетителю не нужны. Никаких имён, username, аватаров, телефонов и цитат исходной переписки добавлять не требуется.

Оригинальные локальные ссылки сохраняются в канонических `docs/evidence*.md` в рабочем проекте; преобразование происходит только в выводе сайта. У публичного посетителя остаётся честное ограничение: он может проверить метод отбора и сводку, но не закрытую переписку. Сайт не должен утверждать независимую доступную проверку исходного чата.

Evidence-реестры и служебное описание источников доступны по ссылке, но исключены из поиска через `pagefind: false`, чтобы выдача приводила прежде всего к решениям. Сами FAQ индексируются. Это настройка релевантности, не механизм приватности. [Starlight: исключение страницы из поиска](https://starlight.astro.build/guides/site-search/).

## Навигация и внешний вид

- Главная: название, короткое назначение, поиск, семь текущих тематических групп, входы для новичка и опытного.
- Sidebar по темам, а не отдельное дерево под каждую модель. На карточках/в начале статьи явная применимость «Общее FDM / CC1 / CC2 / CANVAS»; смешанные случаи сохраняют свои ограничения.
- В статье видны обычные секции «Для новичков» и «Для опытных», доступные по оглавлению и прямым якорям. Не дублировать статью для двух аудиторий и не прятать необходимую диагностику в обязательные переключатели.
- Второй небольшой индекс «По моделям» содержит ссылки на те же страницы; отдельный фасетный движок на первом этапе не нужен. Аналогично навигация «Новичку / Опытному» ведёт к соответствующим секциям.
- Готовая светлая/тёмная тема, аккуратный акцентный цвет, читаемый кириллический шрифт, ограниченная ширина текста, спокойные карточки тем. Мобильная навигация стандартной темы. Без обязательной анимации, фонового видео и отдельного SPA.

Starlight штатно поддерживает группы и вложенные группы sidebar, ручные списки и автогенерацию по каталогам, badges; физическое объединение нескольких статей в один файл не нужно. [Sidebar](https://starlight.astro.build/guides/sidebar/). Здесь лучше один manifest, генерирующий группы и allowlist.

## GitHub Pages и workflow

GitHub Pages подходит для такого статического некоммерческого справочника. Free поддерживает Pages из публичных репозиториев; для private repo возможности зависят от плана. Ограничения: опубликованный сайт до 1 GB, мягкий трафик 100 GB/месяц, таймаут deployment 10 минут. Мягкий лимит 10 сборок/час не применяется к custom Actions workflow. Это не обещание фактического размера или скорости нашей ещё не выполненной сборки. [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

Для project site `https://OWNER.github.io/elegoo_cc_faq/` настроить Astro `site: 'https://OWNER.github.io'`, `base: '/elegoo_cc_faq'`. Для репозитория `OWNER.github.io` или отдельного домена конфигурация корня другая; имя владельца/репозитория сейчас неизвестно и не выдумывается. Проверить картинки, deep links и поиск именно с project base. [Официальная инструкция Astro для GitHub Pages](https://docs.astro.build/en/guides/deploy/github/).

Workflow: checkout → установка по lockfile → allowlist-подготовка → build → проверка output → `upload-pages-artifact` **с path `site/dist`** → `deploy-pages`. В Pages выбрать GitHub Actions. Deploy job требует `pages: write`, `id-token: write`, зависимость от build и environment `github-pages`; checkout достаточно `contents: read`. Не копировать пример загрузки всего `.`. Сгенерированный `gh-pages` branch не требуется. [GitHub: custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Пока публикация не поручена, можно впоследствии реализовать локальную сборку и CI-проверку без deploy. Первый deploy и включение автоматического deploy после push — отдельное явно запрошенное действие. Сам этот план не является разрешением на Git init, commit, push или публикацию.

## Проверка и оценка объёма

Для первой реализации проверить:

1. Все статьи из актуального manifest и выбранные публичные реестры присутствуют; неизвестные ссылки дают ошибку. Заголовки и якоря из реестров сохранены.
2. В опубликованном дереве и поисковых данных нет `data/`, исходных `messages*.html`, приватных вложений, служебных файлов и абсолютных локальных путей. Автопроверка путей не заменяет ручную проверку обезличивания текстов.
3. Поиск находит русские слова, склонения и обозначения: «прилипание», «влажный филамент», «поддержки», `1243`, `103`, `TPU`, `CANVAS`; проверять фактическую выдачу production build, а не только dev server. Поддержка русского в Pagefind задокументирована, конкретная релевантность ещё не проверялась.
4. На мобильной ширине и desktop читаются таблицы и шаги; работают тёмная/светлая тема, keyboard navigation, оглавление и переходы с project base.
5. Deploy artifact содержит только результат сборки, а не source/staging или корень workspace.

Оценка, не обязательство: **1–2 рабочих дня** на аккуратную первую версию с подготовкой контента, минимальным оформлением, CI и проверкой ссылок/поиска; без дальнейшего написания FAQ и без сложных фильтров. По коду это конфигурация Starlight, небольшой скрипт подготовки, один manifest, CSS, главная и workflow. Если начнутся требования к собственным компонентам/фасетам/галереям, объём пересмотреть. Для VitePress общий этап приватности и ссылок остаётся тем же; экономия — преимущественно отсутствие генерации title, а не исчезновение интеграции.
