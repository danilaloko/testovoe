#!/usr/bin/env python3
"""
Скрипт для тестирования загрузки CSV файла через API.
Использование:
    python scripts/upload_csv.py <путь_к_csv_файлу>
    python scripts/upload_csv.py example.csv
"""
import sys
import requests
import os
from pathlib import Path

# URL API (по умолчанию localhost:8000)
API_URL = os.getenv("API_URL", "http://localhost:8000")
UPLOAD_ENDPOINT = f"{API_URL}/upload-grades"


def upload_csv_file(file_path: str):
    """Загрузить CSV файл через API"""
    if not os.path.exists(file_path):
        print(f"❌ Ошибка: Файл '{file_path}' не найден")
        return False
    
    if not file_path.endswith('.csv'):
        print(f"❌ Ошибка: Файл должен иметь расширение .csv")
        return False
    
    print(f"📤 Загрузка файла: {file_path}")
    print(f"🔗 URL: {UPLOAD_ENDPOINT}")
    print("-" * 50)
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            response = requests.post(UPLOAD_ENDPOINT, files=files)
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Успешно загружено!")
            print(f"   Записей загружено: {data.get('records_loaded', 0)}")
            print(f"   Уникальных студентов: {data.get('students', 0)}")
            
            if 'warnings' in data:
                print(f"\n⚠️  {data['warnings']}")
                if 'error_details' in data:
                    print("\nДетали ошибок:")
                    for error in data['error_details']:
                        print(f"   - {error}")
            
            return True
        else:
            print(f"\n❌ Ошибка загрузки:")
            try:
                error_data = response.json()
                print(f"   {error_data.get('detail', 'Неизвестная ошибка')}")
            except:
                print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Ошибка: Не удалось подключиться к серверу {API_URL}")
        print("   Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Использование: python scripts/upload_csv.py <путь_к_csv_файлу>")
        print("\nПримеры:")
        print("  python scripts/upload_csv.py example.csv")
        print("  python scripts/upload_csv.py data/grades.csv")
        print("\nПеременные окружения:")
        print("  API_URL - URL API сервера (по умолчанию: http://localhost:8000)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = upload_csv_file(file_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

