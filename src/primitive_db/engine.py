import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_FILE = "db_meta.json"

def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (...) - добавить запись")
    print("<command> select from <имя_таблицы> - показать записи")
    print("<command> update <имя_таблицы> set ... where ... - обновить запись")
    print("<command> delete from <имя_таблицы> where ... - удалить запись")
    print("<command> info <имя_таблицы> - информация о таблице")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")

def run():
    """Основной цикл программы."""
    print("\n***База данных***")
    print_help()

    select_cache = create_cacher()

    while True:
        user_input = prompt.string(">>>Введите команду: ")
        if not user_input.strip():
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректный ввод. Попробуйте снова.")
            continue

        command = args[0]
        metadata = load_metadata(DB_FILE)

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            if not metadata:
                print("Таблиц нет.")
            else:
                for table in metadata:
                    print(f"- {table}")
        elif command == "create_table":
            if len(args) < 3:
                print("Ошибка: Не указано имя таблицы или столбцы.")
                continue
            
            table_name = args[1]
            columns = args[2:]
            
            new_metadata = create_table(metadata, table_name, columns)
            if new_metadata is not None:  # Если таблица создалась, сохраняем
                save_metadata(DB_FILE, new_metadata)
                select_cache.cache.clear()  #сброс кэша
                
        elif command == "drop_table":
            if len(args) < 2:
                print("Ошибка: Не указано имя таблицы.")
                continue
                
            table_name = args[1]
            new_metadata = drop_table(metadata, table_name)
            if new_metadata is not None:
                save_metadata(DB_FILE, new_metadata)
                select_cache.cache.clear()  #сброс кэша


        elif command == "insert" and len(args) > 2 and args[1] == "into":
            table_name = args[2]
            
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
                
            val_str = user_input.split("values")[1].strip()[1:-1]
            values = [v.strip().strip('"\'') for v in val_str.split(",")]

            for i, v in enumerate(values):
                if v.lower() == 'true': 
                    values[i] = True
                elif v.lower() == 'false': 
                    values[i] = False
                elif v.isdigit(): 
                    values[i] = int(v)

            # Вызываем функцию из core.py
            res = insert(metadata, table_name, values)
            
            # Если None останавливаем
            if res is None:
                continue

            # Если всё ок, генерируем ID и сохраняем
            table_data = load_table_data(table_name)
            new_id = max([row.get("ID", 0) for row in table_data], default=0) + 1
            row_dict = {"ID": new_id}
            
            for i, col in enumerate(metadata[table_name][1:]):
                row_dict[col["name"]] = values[i]

            table_data.append(row_dict)
            save_table_data(table_name, table_data)
            select_cache.cache.clear()  #сброс кэша
            print(f'Запись с ID={new_id} успешно добавлена.')

        elif command == "select" and args[1] == "from":
            table_name = args[2]

            if table_name not in metadata: #проверка на наличие таблицы
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            table_data = load_table_data(table_name)
            
            # передаем args в парсер
            where_clause = parse_condition(args, "where")
            result = select_cache(user_input, lambda: select(table_data, where_clause))

            if result:
                table = PrettyTable()
                table.field_names = [col["name"] for col in metadata[table_name]]
                for row in result:
                    row_data = [row.get(col["name"]) for col in metadata[table_name]]
                    table.add_row(row_data)
                print(table)
            else:
                print("Записей не найдено.")

        elif command == "update":
            table_name = args[1]
            # парсер найдет слова 'set' и 'where' и вытащит данные
            set_clause = parse_condition(args, "set")
            where_clause = parse_condition(args, "where")

            if not set_clause or not where_clause:
                print(
                    "Ошибка: неверный формат update. " \
                    "Нужно: update <таблица> set <столбец> " \
                    "= <значение> where <столбец> = <значение>"
                    )
                continue

            table_data = load_table_data(table_name)
            updated_data, count = update(table_data, set_clause, where_clause)

            if count > 0:
                save_table_data(table_name, updated_data)
                select_cache.cache.clear()  #сброс кэша
                print(f"Обновлено записей: {count}")
            else:
                print("Ничего не найдено, никого не обновили.")

        elif command == "delete" and len(args) > 2 and args[1] == "from":
            table_name = args[2]
            where_clause = parse_condition(args, "where")

            if not where_clause:
                print(
                    "Ошибка: неверный формат delete." \
                    " Нужно: delete from <таблица> where "
                    "<столбец> = <значение>"
                    )
                continue

            table_data = load_table_data(table_name)
            #декоратор вернёт none поэтому исправляю
            res = delete(table_data, where_clause)
            if res is not None:
                new_data, count = res
                if count > 0:
                    save_table_data(table_name, new_data)
                    select_cache.cache.clear()  #сброс кэша
                    print(f"Удалено записей: {count}")
                else:
                    print("Нечего удалять.")


        elif command == "info":
            if len(args) < 2:
                print("Ошибка: Укажите имя таблицы: info <имя_таблицы>")
                continue

            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
                
            cols = metadata[table_name]
            table_data = load_table_data(table_name)
            cols_str = ", ".join(f"{c['name']}:{c['type']}" for c in cols)
            
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {cols_str}")
            print(f"Количество записей: {len(table_data)}")


        else:
            print(f"Функции {command} нет. Попробуйте снова.")