-- Миграция 001: Создание таблицы grades и индексов

-- Создание таблицы для оценок студентов
CREATE TABLE IF NOT EXISTS grades (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    grade INTEGER NOT NULL CHECK (grade IN (2, 3, 4, 5)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_grades_full_name ON grades(full_name);
CREATE INDEX IF NOT EXISTS idx_grades_grade ON grades(grade);

