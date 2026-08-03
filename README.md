# MLRERAG

## Как запустить

Создайте папку для проекта. Откройте её в терминале и введите:

```bash
git clone https://github.com/Akevilli/MLRERAG && cd MLRERAG
```

Далее нужно настроить переменные окружения, как в корневой папке так и в папках проектов:

```bash
cp .env.example .env
```

Далее необходимо сбилдить проект, чтобы создать сеть и все волюмы, контейнер с neo4j не запуститься т.к. скачивается ломаный плагин (если всё таки запуститься, то остальное можно пропустить):

```bash
docker compose -f "docker-compose.services.yaml" -f "docker-compose.app.yaml" up --build
```

Полсе билда скачаиваем плагин вручную по этой [ссылке](https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/2026.04.0/apoc-2026.04.0-extended.jar).

Далее копируем плагин в волюм neo4j контейнера:

```bash
docker cp <путь к плагину>/apoc-2026.04.0-extended.jar neo4j-MLRERAG:/plugins/
```

Перезапускаем контейнеры через комбинацию Ctrl + C и комманду:

```bash
docker compose -f "docker-compose.services.yaml" -f "docker-compose.app.yaml" up
```

Проверьте работу контейнеров в докере, если все контейнеры стартовали значит скорее всего проблем нет.