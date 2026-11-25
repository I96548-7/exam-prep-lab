# AGENTS.md

## О проекте
Лабораторная работа: приложение для подготовки к экзамену.
Стек: Python 3.12, Django 5.2, PostgreSQL 17, Docker Compose.
В SDD-версии дополнительно используется Valkey (кэш).

## Структура
- `vibe/` — вайб-версия приложения (оценка 4)
- `sdd/` — SDD-версия + Valkey (оценка 5)
- `docs/` — отчёты, журнал, скриншоты (`docs/img/`)
- `.opencode/skills/` — skills агента

## Команды
- `docker compose up --build -d` — собрать и запустить
- `docker compose exec web python manage.py migrate` — миграции
- `docker compose exec web python manage.py test` — тесты
- `docker compose logs -f web` — логи веб-сервиса

## Правила
- Общаться по-русски, код писать на английском.
- Сначала план, потом действия.
- Документацию смотреть через context7.
- Секреты только в `.env`; в git — `.env.example`.
- После изменений запускать тесты.
- Коммиты делать через skill `git-commit`.
- Без `git push` без явной просьбы.