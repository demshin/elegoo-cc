# FAQ по FDM-печати и Elegoo Centauri Carbon

Повторяющиеся проблемы и решения из пользовательского чата, с проверкой применимости и ссылками на источники. Материалы предназначены для новичков и опытных владельцев.

[Читать сайт](https://demshin.github.io/elegoo-cc/) · [Предложить тему или исправление](https://github.com/demshin/elegoo-cc/issues) · [Как участвовать](CONTRIBUTING.md)

Статьи сгруппированы по темам. Текст всех 78 458 сообщений архива прочитан последовательно; ход разбора и ограничения описаны в реестрах ниже. Общие приёмы FDM-печати отделены от диагностики CC1, CC2 и особенностей CANVAS. Для каждого решения указаны применимость и границы подтверждения. Это пополняемый FAQ, а не полный каталог неисправностей.

## Для новичков

- [Первый слой не прилипает: очистка печатной поверхности](faq/first-layer-adhesion.md#для-новичков).
- [После множества настроек печать испортилась: базовый профиль](faq/slicing/profile-baseline.md#для-новичков).
- [Пузырьки и паутина: проверка сушки](faq/filament/drying-and-storage.md#для-новичков).
- [ASA: расслоение и достаточный обдув модели](faq/filament/asa-layer-separation.md).
- [Первый слой с щелями или наплывами: Z-offset](faq/centauri/first-layer-z-offset.md#для-новичков).
- [CC1: предупреждение о стороне пластины и выбор поверхности](faq/centauri/cc1-build-plate-selection.md).
- [CC2 не подключается к компьютеру: «Только ЛВС»](faq/centauri/cc2-lan-connection.md#для-новичков).

## По темам

### Материалы и подача

- [ASA: расслоение и достаточный обдув](faq/filament/asa-layer-separation.md).
- [CC1 не захватывает нить после смены катушки](faq/centauri/cc1-filament-loading.md).
- [CC2: CANVAS не переключается на запасную катушку](faq/centauri/cc2-filament-backup.md).
- [Сушка и хранение филамента](faq/filament/drying-and-storage.md).
- [TPU перестаёт подаваться: тракт и CANVAS](faq/filament/tpu-feed-path.md).
- [Катушка и перегибы трубок мешают подаче](faq/filament/feed-resistance.md).

### Первый слой и удержание детали

- [CC1: выбор стороны и типа пластины](faq/centauri/cc1-build-plate-selection.md).
- [Загрязнение печатной поверхности](faq/first-layer-adhesion.md).
- [Мусор под пластиной](faq/debris-under-build-plate.md).
- [Отрыв углов: кайма и условия печати](faq/printing/warping-and-brim.md).
- [Пустое начало контура: юбка перед моделью](faq/printing/empty-start-skirt.md).
- [Щели и наплывы первого слоя: Z-offset](faq/centauri/first-layer-z-offset.md).
- [Основание шире детали: слоновья нога](faq/printing/elephant-foot.md).
- [CC1: неровный монослой и толщина первого слоя](faq/centauri/cc1-first-layer-height.md).

### Слайсер, периметры и поддержки

- [Температурная башня и рабочая деталь](faq/slicing/temperature-tower.md).
- [Калибровка и сохранение коэффициента потока](faq/slicing/flow-ratio.md).
- [Pressure Advance: тест, расчёт и сохранение](faq/slicing/pressure-advance.md).
- [Поддержки трудно отделяются](faq/slicing/support-removal.md).
- [Провисают периметры на скосах и резьбе](faq/slicing/overhang-walls.md).
- [Вазный режим: отверстия на наклонной стенке](faq/slicing/vase-wall-gaps.md).
- [Возврат к базовому профилю](faq/slicing/profile-baseline.md).
- [Маленькая деталь печатается долго: время слоя и охлаждение](faq/slicing/small-part-cooling-time.md).
- [Вертикальная полоска: размещение шва](faq/slicing/seam-placement.md).
- [Клиновидный шов Scarf на круглой стенке](faq/slicing/scarf-seam.md).
- [Шероховатая поверхность: нечёткая оболочка](faq/slicing/fuzzy-skin.md).
- [Щели между сплошной поверхностью и стенкой](faq/slicing/surface-wall-gaps.md).
- [Разглаживание поверхности и поддержки](faq/slicing/ironing.md).
- [Сопло чиркает при перемещении: Z-hop и откаты](faq/slicing/travel-scratches-z-hop.md).
- [Провисающие мосты: отдельный тест](faq/slicing/bridges.md).
- [Часть модели исчезает после нарезки: исправление сетки](faq/slicing/model-mesh-repair.md).
- [Неровные скругления в предпросмотре: дуги](faq/slicing/arc-preview.md).
- [CC1 без CANVAS: ручная смена цвета](faq/slicing/manual-color-change.md).

### Экструзия и нагрев

- [CC1: повреждено горло хотэнда — проверка и замена узла](faq/centauri/cc1-hotend-damage.md).
- [Когда помогает очистка сопла](faq/printing/nozzle-clog.md).
- [CC2: ошибка экструзии 1243](faq/centauri/cc2-extrusion-1243.md).
- [CC1: ошибка нагрева 103](faq/centauri/heating-error-103.md).
- [CC1: сопло само нагревается после включения](faq/centauri/cc1-uncontrolled-heating.md).
- [CC1: ошибка проводки между платами головы и принтера](faq/centauri/cc1-printhead-communication.md).
- [CC1: ошибка вентилятора модели 703](faq/centauri/cc1-fan-703.md).
- [Проверка прижима экструдера](faq/printing/extruder-grip.md).

### Механика, калибровка и обслуживание

- [CC1: просмотр сохранённой карты высот](faq/centauri/cc1-bed-mesh-viewer.md).

- [Cosmos: ошибки Probe triggered и Load Cell](faq/centauri/cosmos-bed-probe.md).
- [CC1: ошибка 502 при выравнивании](faq/centauri/bed-leveling-502.md).
- [Стол заедает по Z при первом запуске](faq/centauri/z-axis-binding.md).
- [CC1: шум в простое после смены филамента](faq/centauri/cc1-idle-noise.md).
- [CC1: вытяжка снова включается после отключения](faq/centauri/cc1-exhaust-fan-control.md).
- [CC1: гудит вентилятор основной платы](faq/centauri/mainboard-fan-noise.md).
- [Дребезжит крышка головы](faq/centauri/toolhead-cover-rattle.md).
- [Хруст движения: направляющие и ремни](faq/centauri/axis-noise.md).
- [CC1: передача вибрации на стол и мягкие ножки](faq/centauri/cc1-antivibration-feet.md).
- [CC1: у надстройки крышки не двигаются шторки](faq/centauri/cc1-vented-riser.md).
- [CC1: подсветка сопла](faq/centauri/cc1-nozzle-light.md).
- [CC2: не снимаются трубки из 4-в-1 хаба](faq/centauri/cc2-ptfe-release.md).
- [CC1: ограничения полного поля 256×256 мм](faq/centauri/cc1-full-build-area.md).

### Связь и интерфейс

- [Слайсер потерял принтер после смены IP](faq/centauri/printer-ip-address.md).
- [CC1: доступ из другой сети через домашний VPN](faq/centauri/cc1-remote-access.md).
- [CC1: пропали камера, статистика и управление](faq/web-interface-recovery.md).
- [CC2 Carbon: камера не найдена при работающем управлении](faq/centauri/cc2-camera-not-detected.md).
- [CC2: локальное подключение к компьютеру](faq/centauri/cc2-lan-connection.md).
- [Принтер виден, файл не отправляется или зависает на 99%](faq/centauri/file-upload-failure.md).

### Прошивки и восстановление работы

- [Cosmos: очистительная линия под каймой или поддержками](faq/centauri/cosmos-purge-collision.md).

- [CC2: «Принтер занят», CANVAS горит красным](faq/centauri/cc2-printer-busy.md).
- [После обновления слайсер перестал видеть принтер](faq/centauri/slicer-firmware-compatibility.md).
- [Белый экран после прошивки](faq/centauri/white-screen-recovery.md).
- [CC2: обновление с USB при отказе OTA](faq/centauri/cc2-offline-firmware-update.md).

## Для опытных

В каждой статье есть раздел «Для опытных»: условия исходных случаев, различие параметров и ограничения диагностики.

- [Коэффициент потока и объёмное ограничение — разные настройки](faq/slicing/flow-ratio.md#для-опытных).
- [Зазор поддержек зависит от высоты слоя](faq/slicing/support-removal.md#для-опытных).
- [Восстановление веб-интерфейса не доказывает устранение первопричины](faq/web-interface-recovery.md#для-опытных).
- [M600, пауза и смена внутри слоя](faq/slicing/manual-color-change.md#для-опытных).
- [Шум портала: отделение причин и проверка рецидивов](faq/centauri/axis-noise.md#для-опытных).
- [PA: формула башни зависит от заданного начала и шага](faq/slicing/pressure-advance.md#для-опытных).
- [Диагностика платы головы: диодный режим и единицы измерения](faq/centauri/cc1-printhead-communication.md#для-опытных).

## Как читать подтверждения

В FAQ попадают повторяющиеся проблемы, для которых есть явное сообщение об успешном решении. Повторные сообщения одного владельца и пересказы не увеличивают число независимых случаев. Успешный обход может восстановить работу, не устранив первопричину; такие ограничения отмечены в статье.

Повторяемость симптома и число успешных испытаний способа учитываются отдельно. Например, для неровностей предпросмотра найдены два независимых успешных изменения нарезки; это не объявлено двумя успешными физическими печатями.

Сообщения участников, рекомендации производителя и редакционные выводы разделены. Аппаратная проверка этих решений на принтере при подготовке FAQ не проводилась.

- [Карта тем, покрытие архива и решения об отборе](docs/topic-map.md).
- [Прогресс последовательного разбора всей истории](docs/history-audit.md) и [его новые основания](docs/evidence-history.md).
- [Основания трёх исходных статей](docs/evidence.md) и [десяти тематических статей](docs/evidence-more.md).
- [Основания 17 статей расширенного разбора](docs/evidence-expanded.md), включая отрицательные результаты.
- [Повторные вопросы, ответы, исходы и отсылки для девяти новых статей](docs/evidence-qa.md).
- [Проверенные первоисточники](docs/sources.md).
- [Исторический отчёт пилота и воспроизведение индекса](docs/pilot.md).
- [Локальный статический сайт: сборка и проверки](site/README.md).
- [Договорённости о публикации и участии сообщества](docs/publication-plan.md).

## Исходные материалы

Выгрузка и локальный индекс находятся в `data/`, исключённой из Git. В репозитории остаются обезличенные пересказы и идентификаторы сообщений. Ссылки на исходные сообщения работают только при наличии локальной выгрузки; текст и изображения чата в статьи не скопированы.

Сайт, его код и статьи подготовлены с помощью OpenAI Codex и могут содержать ошибки. Это независимый проект сообщества, не официальный сервис ELEGOO. Код распространяется по [MIT](LICENSE), статьи и справочные тексты — по [CC BY-SA 4.0](LICENSE-CONTENT.md).
