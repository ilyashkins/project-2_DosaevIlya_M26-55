import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

DB_FILE = "db_meta.json"


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def run():
    """Основной цикл программы."""
    print("\n***База данных***")
    print_help()

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
                
        elif command == "drop_table":
            if len(args) < 2:
                print("Ошибка: Не указано имя таблицы.")
                continue
                
            table_name = args[1]
            new_metadata = drop_table(metadata, table_name)
            if new_metadata is not None:
                save_metadata(DB_FILE, new_metadata)
                
        else:
            print(f"Функции {command} нет. Попробуйте снова.")