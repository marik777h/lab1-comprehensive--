# Лабораторная работа №1

Комплексный анализ, настройка инфраструктуры и контроль качества ПО.
Микросервис расчёта корзины и скидок системы лояльности.

**[Открыть итоговый отчёт в develop](https://github.com/marik777h/lab1-comprehensive--/blob/develop/REPORT.md)**

Основная работа находится в ветке
[develop](https://github.com/marik777h/lab1-comprehensive--/tree/develop).
Отчёт содержит матрицу выбора СУБД, ссылки на коммиты и PR,
скриншоты защиты ветки и проверки CI, UML и анализ legacy-кода.

- [PR №1 — инфраструктура](https://github.com/marik777h/lab1-comprehensive--/pull/1), слит.
- [PR №2 — QA и код](https://github.com/marik777h/lab1-comprehensive--/pull/2), слит; CI прошёл после намеренной ошибки.
- [PR №3 — план ревью и UML](https://github.com/marik777h/lab1-comprehensive--/pull/3), **оставлен открытым по заданию**.

## Проверка кода

Выполнить после переключения на develop, используя Python 3.12:

```bash
python -m pip install flake8==7.4.1 coverage==7.16.2
python -m flake8 .
python -m coverage run --branch --source=src -m unittest discover -s tests -v
python -m coverage report -m --fail-under=81
```

Текущий результат: lint без ошибок, все 7 тестовых методов проходят,
покрытие строк и ветвлений src — 100%.
