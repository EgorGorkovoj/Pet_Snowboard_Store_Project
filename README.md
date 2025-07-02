# Pet_Snowboard_Store_Project

#### Активация виртуального окружения

**В Poetry 1.x:**
```bash
poetry shell
```

**В Poetry 2.x:**
В версии 2.0.0 и выше команда `poetry shell` не доступна по умолчанию. Используйте один из следующих методов:

```bash
# Рекомендуемый способ: активация окружения
poetry env activate
```

# Альтернатива: установка плагина shell
poetry self add poetry-plugin-shell
poetry shell

# Или напрямую активируйте окружение
```
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate.bat   # Windows cmd
.venv\Scripts\Activate.ps1   # Windows PowerShell
```

> 📘 Подробнее в документации: [Poetry: Activating the environment](https://python-poetry.org/docs/managing-environments/#activating-the-environment)

#### Запуск команд в виртуальном окружении
```bash
poetry run <команда>
```

Примеры:
```bash
poetry run python src/main.py
poetry run pytest
poetry run ruff format
```

#### Управление зависимостями

**Добавление основной зависимости:**
```bash
poetry add <имя_пакета>
```

**Добавление зависимости для разработки:**
```bash
poetry add <имя_пакета> --dev
```

**Обновление зависимостей:**
```bash
poetry update
```

### 🔄 Pre-commit <a name="pre-commit"></a>

<details>
<summary><strong>🔽 Настройка pre-commit</strong></summary>

1. Проверьте, что pre-commit установлен:
   ```bash
   pre-commit --version
   ```

2. Настройте git hook:
   ```bash
   pre-commit install
   ```

После настройки при каждом коммите будет автоматически запускаться проверка линтером и форматирование кода.

</details>

### 🧹 Линтеры <a name="linters"></a>

<details>
<summary><strong>🔽 Проверка качества кода</strong></summary>

В проекте используется [Ruff](https://github.com/astral-sh/ruff) для форматирования и проверки кода.

#### Основные настройки

- **Максимальная длина строки:** 99 символов
- **Исключены из проверки:** директории "alembic"
- **Проверки:** "E" (ошибки), "F" (предупреждения), "I" (импорты)
- **Стиль строк:** одинарные кавычки
- **Импорты:** с учетом внутренних модулей `src`

#### Запуск проверки

```bash
poetry run ruff check .
```

#### Автоматическое форматирование

```bash
poetry run ruff format .
```

</details>
