# Скрипты для работы с API

## upload_csv.py

Скрипт для тестирования загрузки CSV файла через API.

### Использование

```bash
# Базовое использование
python scripts/upload_csv.py <путь_к_csv_файлу>

# Примеры
python scripts/upload_csv.py scripts/example_grades.csv
python scripts/upload_csv.py data/my_grades.csv

# С указанием URL API сервера
API_URL=http://localhost:8080 python scripts/upload_csv.py example.csv
```

### Пример вывода

```
📤 Загрузка файла: scripts/example_grades.csv
🔗 URL: http://localhost:8000/upload-grades
--------------------------------------------------
📊 Статус ответа: 200

✅ Успешно загружено!
   Записей загружено: 13
   Уникальных студентов: 4
```

