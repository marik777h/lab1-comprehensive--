# Анализ потоков данных

Нумерация исходного кода без пустых строк:

```text
 1  def process_transaction(user_id, amount, db_connection):
 2      log_entry = "Start processing"
 3      if amount > 0:
 4          status = "approved"
 5          balance = get_balance(user_id)
 6          new_balance = balance - amount
 7          update_balance(user_id, new_balance)
 8      log_entry = "Transaction finished with status: " + status
 9      file = open("audit_log.txt", "w")
10      file.write(log_entry)
11      return status
```

| Переменная | Def | Use |
| --- | --- | --- |
| user_id | 1, параметр | 5, 7 |
| amount | 1, параметр | 3, 6 |
| db_connection | 1, параметр | Не используется |
| log_entry | 2, 8 | 10; используется только значение из строки 8 |
| status | 4, внутри if | 8, 11 |
| balance | 5 | 6 |
| new_balance | 6 | 7 |
| file | 9 | 10 |

## Найденные дефекты

1. При amount <= 0 строка 4 пропускается. Чтение status в строке 8
   вызывает UnboundLocalError. До строки 11 выполнение уже не доходит.
2. Значение log_entry из строки 2 не читается: в строке 8 оно заменяется.
   Это мёртвое присваивание.
3. После открытия файла в строке 9 нет close(). Файл не закрывается явно,
   в том числе при ошибке записи.

В исправленном коде status задан до if, начальное присваивание log_entry
убрано, а файл открывается через with. Методы работы с балансом вызываются
через db_connection. Режим a дописывает журнал, сохраняя предыдущие записи.
