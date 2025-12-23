-- Миграция 002: Делаем поле subject опциональным (NULL)

-- Изменяем поле subject, чтобы оно могло быть NULL
ALTER TABLE grades ALTER COLUMN subject DROP NOT NULL;

-- Обновляем существующие записи с пустым subject на NULL (если есть)
UPDATE grades SET subject = NULL WHERE subject = '';

