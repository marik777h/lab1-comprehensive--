# Проверка требований лабораторной работы №1

Эта таблица связывает каждый результат с проверяемым артефактом.
Основная ветка для проверки — develop. План ревью остаётся в открытом PR.

| Этап | Требование | Подтверждение | Состояние |
| --- | --- | --- | --- |
| 1 | 4–5 критериев, веса 1.00, баллы и расчёты | [REPORT.md, раздел 2](../REPORT.md#2-сравнительный-анализ-технологий) | 5 критериев, 4.75 против 3.65 |
| 2 | Публичный репозиторий и ветки | [Репозиторий](https://github.com/marik777h/lab1-comprehensive--) | Public; main, develop и feature-ветки сохранены |
| 2 | Имя с фамилией автора | Текущее имя lab1-comprehensive-- | Нужно уточнить фамилию |
| 2 | EditorConfig и CODEOWNERS | [.editorconfig](../.editorconfig), [CODEOWNERS](../.github/CODEOWNERS) | UTF-8, LF, четыре пробела; владелец @marik777h |
| 2 | Изменения инфраструктуры через PR | [PR №1](https://github.com/marik777h/lab1-comprehensive--/pull/1) | Слит; итоговые конфигурации исправлены отдельными коммитами |
| 2 | Защита develop с требованием PR | [Protect develop](https://github.com/marik777h/lab1-comprehensive--/rules/25237735), [скриншот](branch-protection.jpg) | Активный ruleset; также запрещены удаление и force push |
| 2 | Approve перед слиянием | Правило GitHub: автор не может одобрить свой PR | Нужен второй участник; одобрение не выдумывалось |
| 3 | Линтер и PR-пайплайн | [.flake8](../.flake8), [qa.yml](../.github/workflows/qa.yml) | Лимит 80 символов; PR в develop и push в develop |
| 3 | Настоящий красный CI | [Запуск №1](https://github.com/marik777h/lab1-comprehensive--/actions/runs/38903539783) | failure: F401, F841, E501 |
| 3 | Исправление и зелёный CI | [PR №2](https://github.com/marik777h/lab1-comprehensive--/pull/2), [скриншот](qa-red-green.jpg) | Исправление в том же PR; слито после success |
| 4 | Рабочая calculate_cart_total | [discount.py](../src/discount.py), [тесты](../tests/test_discount.py) | Decimal, валидация и сохранённый порядок скидок |
| 4 | UML с циклом и условиями | [PNG](uml_diagram.png), [.drawio](uml_diagram.drawio) | Начало, конец, порог, цикл, SUMMER/VIP, tier, лимит |
| 4 | Цели, критерии, роли, эскалация | [review-plan.md](https://github.com/marik777h/lab1-comprehensive--/blob/feature/review-plan/docs/review-plan.md) | План в feature/review-plan |
| 4 | PR с планом не сливать | [PR №3](https://github.com/marik777h/lab1-comprehensive--/pull/3) | Оставлен открытым |
| 5 | REPORT.md в develop | [Отчёт](../REPORT.md) | Все шесть разделов, ссылки, реальные скриншоты |

## Усиленная проверка реализации

Команда: `python scripts/check.py`. Установка зависимостей:
`python -m pip install -r requirements-dev.txt`.

- 12 тестовых методов, включая позитивные, граничные и негативные сценарии.
- 1000 детерминированных наборов входов сравниваются с эталоном на Fraction.
- Отдельные тесты доказывают изоляцию Decimal traps, точности и диапазона
  экспоненты, сохранность внешнего контекста и исходного списка промокодов.
- Два новых регрессионных теста падают на прежней реализации и проходят
  после исправления. Покрытие текущего модуля — 100%; минимальный порог — 95%.
- Actions привязаны к конкретным SHA; workflow имеет только contents: read,
  не сохраняет Git-учётные данные и не получает секреты через pull_request_target.

## Что не подменяется учебной реализацией

Выбор PostgreSQL обоснован в отчёте, но БД здесь не развёрнута. Проверка
владельца промокода, срока действия, одноразового погашения и транзакционного
списания баллов относится к интеграции сервиса. Поведение повторных и
неизвестных кодов сохранено из задания и явно отмечено в плане ревью.
