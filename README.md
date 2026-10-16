# Расчёт корзины и скидок

Лабораторная работа №1 по моделированию и анализу программного обеспечения:
выбор СУБД, управление изменениями, автоматический контроль качества
и обратное проектирование алгоритма системы лояльности.

**[Итоговый отчёт](https://github.com/marik777h/lab1-comprehensive--/blob/develop/REPORT.md)**
· [Проверка требований](https://github.com/marik777h/lab1-comprehensive--/blob/develop/docs/requirements-checklist.md)
· [Код](https://github.com/marik777h/lab1-comprehensive--/blob/develop/src/discount.py)
· [Открытый PR с планом ревью](https://github.com/marik777h/lab1-comprehensive--/pull/3)

## Что реализовано

| Область | Результат |
| --- | --- |
| Выбор СУБД | PostgreSQL 4.75, MongoDB 3.65; сумма весов 1.00 |
| Расчёт | Decimal, валидация, скидки SUMMER/VIP, tier 0/1/2, лимит 30% |
| Тесты | 12 методов, включая 1000 воспроизводимых сценариев с точным эталоном |
| Контроль качества | flake8, тесты, coverage 100%; минимальный порог CI 95% |
| Инфраструктура | EditorConfig, CODEOWNERS, защищённая develop, изменения через PR |
| Документация | Отчёт, реальные скриншоты GitHub, UML PNG и исходник diagrams.net |

Основная работа находится в **develop**. PR №3 необходимо оставить
открытым по заданию. Зелёный CI не заменяет независимое code-review.

## Запустить все проверки

Требуется Python 3.12. Рабочий модуль использует только стандартную
библиотеку; внешние зависимости нужны для проверки качества.

```bash
git switch develop
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/check.py
```

В Windows вместо `source` активируйте среду командой
`.venv\Scripts\Activate.ps1` в PowerShell. Если репозиторий ещё не скачан:
`git clone https://github.com/marik777h/lab1-comprehensive--.git`.
Затем перейдите в созданную папку и выполните команды выше.

`scripts/check.py` последовательно запускает линтер, тесты и контроль
покрытия. При первой ошибке возвращает ненулевой код. GitHub Actions
использует тот же скрипт и тот же файл зафиксированных зависимостей.

## Пример расчёта

```python
from src.discount import calculate_cart_total

calculate_cart_total(10000, 0, ["SUMMER", "VIP"])  # Decimal('8550.00')
calculate_cart_total(10000, 0, ["VIP", "SUMMER"])  # Decimal('8500.00')
calculate_cart_total(20000, 2, ["SUMMER", "VIP"])  # Decimal('14000.00')
```

Порядок промокодов влияет на результат и сохранён из legacy-кода.
Повторные коды применяются повторно, неизвестные игнорируются. Это
учебная совместимость, а не реализация проверки права на промокод.

Сумма — конечное неотрицательное `int`, `float` или `Decimal`, максимум
999999999999.99; `bool` запрещён. Промокоды — список или кортеж строк.
Результат — Decimal с двумя знаками, ROUND_HALF_UP в конце расчёта.
Ошибочный тип вызывает TypeError, значение вне контракта — ValueError.
Для точной передачи денежных входов предпочтителен Decimal, для JSON
результат можно передать строкой: `str(total)`.

## Доказательства и артефакты

- [Защита develop](https://github.com/marik777h/lab1-comprehensive--/rules/25237735): PR обязателен, удаление и force push запрещены.
- [PR №2](https://github.com/marik777h/lab1-comprehensive--/pull/2): реальная ошибка линтера, затем исправление и успешные проверки.
- [Красный CI](https://github.com/marik777h/lab1-comprehensive--/actions/runs/38903539783) → [зелёный CI](https://github.com/marik777h/lab1-comprehensive--/actions/runs/38903714066).
- [UML PNG](https://github.com/marik777h/lab1-comprehensive--/blob/develop/docs/uml_diagram.png) и [редактируемый .drawio](https://github.com/marik777h/lab1-comprehensive--/blob/develop/docs/uml_diagram.drawio).
- [План ревью](https://github.com/marik777h/lab1-comprehensive--/blob/feature/review-plan/docs/review-plan.md) находится в незакрытом PR №3.

Репозиторий публичный. Перед сдачей требуется добавить фамилию автора
в его название; независимое одобрение может дать только второй участник.
