# termometro-da-polarizacao

## Database Commands

**Run docker compose database:**
```bash
docker compose up -d db
```

**View logs:**
```bash
docker compose logs -f db
```

**Access database:**
```bash
docker exec -it termopol-db psql -U admin -d termopol
```

**Stop database:**
```bash
docker compose down db
```

**Reset database (remove data and restart):**
```bash
docker compose down -v && docker compose up -d db
```

**Reset with orphan cleanup:**
```bash
docker compose down -v --remove-orphans && docker compose up -d db
```
