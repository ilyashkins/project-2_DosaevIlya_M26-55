import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Загружает данные из JSON-файла. Если файл не найден, возвращает {}."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def load_table_data(table_name):
    """Загружает файл из JsON если файла нет возвращает список"""
    filepath = f"{DATA_DIR}/{table_name}.json"
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_table_data(table_name, data):
    '''Сохраняет данные в JSON и создаёт папку если её еще нет'''
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    filepath = f"{DATA_DIR}/{table_name}.json"
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)