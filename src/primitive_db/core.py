def create_table(metadata, table_name, columns):
    """Создает таблицу, проверяет типы и добавляет ID."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None  # Возвращаем None при ошибке

    valid_types = {"int", "str", "bool"}
    parsed_columns = [{"name": "ID", "type": "int"}]

    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return None
        
        name, col_type = col.split(":", 1)
        
        if col_type not in valid_types:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return None
        
        parsed_columns.append({"name": name, "type": col_type})

    metadata[table_name] = parsed_columns
    
    cols_str = ", ".join(f"{c['name']}:{c['type']}" for c in parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata

def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata