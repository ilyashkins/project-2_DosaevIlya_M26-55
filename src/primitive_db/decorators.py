import functools
import time

import prompt


def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. " \
                "Возможно, база данных не инициализирована"
                )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper

def confirm_action(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ans = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                )
            if ans.lower() == 'y':
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")
                return None
        return wrapper
    return decorator

def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд.")
        return result
    return wrapper

def create_cacher():
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
    cache_result.cache = cache #Для сброса кэша в engine.py
    return cache_result