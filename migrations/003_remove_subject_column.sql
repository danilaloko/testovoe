-- Миграция 003: Удаление поля subject из таблицы grades

-- Удаляем колонку subject из таблицы grades
ALTER TABLE grades DROP COLUMN IF EXISTS subject;

