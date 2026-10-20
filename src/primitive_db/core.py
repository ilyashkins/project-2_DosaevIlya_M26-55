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

def insert(metadata, table_name, values):
    """Вставляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    columns = metadata[table_name]
    # Отнимаем 1, так как ID генерируется автоматически
    if len(values) != len(columns) - 1:
        print(f"Ошибка: Неверное количество значений. Ожидалось {len(columns) - 1}.")
        return None

    return values

def select(table_data, where_clause=None):
    """Возвращает данные по условию или все данные."""
    if not where_clause:
        return table_data
    result = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if match:
            result.append(row)
    return result

def update(table_data, set_clause, where_clause):
    """Обновляет данные по условию."""
    updated_count = 0
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if match:
            for set_key, set_value in set_clause.items():
                row[set_key] = set_value
            updated_count += 1
            
    return table_data, updated_count


def delete(table_data, where_clause):
    """Удаляет данные по условию."""
    new_data = []
    deleted_count = 0
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if match:
            deleted_count += 1
        else:
            new_data.append(row)  
    return new_data, deleted_count