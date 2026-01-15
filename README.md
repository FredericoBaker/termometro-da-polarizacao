# termometro-da-polarizacao

run docker compose database: docker compose up -d db
Ver logs: docker compose logs -f db
Acessar db: docker exec -it termopol-db psql -U admin -d termopol
Docker down: docker compose down -v
