# Khukra Deployment Plan

Checklist for moving from local MVP to a hosted demo/pilot environment. Track progress via GitHub Issues labeled `deployment` and `ci-cd`.

**Repo:** https://github.com/Claymorrr/khukra  
**Default branch:** `main`

---

## 1. Decisions (fill in before deploy)

| Decision | Options | Choice |
|----------|---------|--------|
| **API host** | Railway, Render, Fly.io, Azure Container Apps, VPS + Docker | _TBD_ |
| **Frontend host** | Vercel, Netlify, same host as API, static behind CDN | _TBD_ |
| **Database** | DuckDB on persistent volume, managed Postgres + DuckDB attach, object store + DuckDB | _TBD_ |
| **Domain** | Custom domain + TLS | _TBD_ |
| **Auth in prod** | Change admin password; rotate `KHUKRA_SECRET_KEY` | Required |

---

## 2. Pre-deploy checklist

### Code & build

- [ ] `pip install -e .` and `pytest tests -q` pass on clean machine
- [ ] `cd frontend && npm ci && npm run build` passes
- [ ] Pin or document Python/Node versions (e.g. `.python-version`, `engines` in `package.json`)
- [ ] Production Dockerfile or platform build config (API + optional combined image)
- [ ] `scripts/start-dev.ps1` documented; production start command defined (e.g. `uvicorn` + `next start`)

### Configuration

- [ ] Document all env vars (see README + below)
- [ ] `KHUKRA_SECRET_KEY` — strong random value in host secrets
- [ ] `KHUKRA_ADMIN_EMAIL` / `KHUKRA_ADMIN_PASSWORD` — not dev defaults in prod
- [ ] `NEXT_PUBLIC_API_URL` (or equivalent) points to deployed API
- [ ] CORS allows only production frontend origin

### Data

- [ ] Persistent volume or bucket for `data/warehouse/khukra.duckdb`
- [ ] Persistent paths for `data/runs`, `data/datasets`, `data/synthetic` (or migrate to object storage)
- [ ] Backup strategy for warehouse (snapshot frequency, restore test)
- [ ] Migrations/bootstrap run on API startup (`bootstrap` service)

### Security

- [ ] HTTPS everywhere (API + UI)
- [ ] JWT expiry and refresh story documented
- [ ] No secrets in git; `.env` in `.gitignore` only
- [ ] Review default credentials removed from public docs for prod URL

### CI/CD

- [ ] GitHub Actions: backend test job on PR/push
- [ ] GitHub Actions: frontend build job on PR/push
- [ ] Optional: deploy workflow on tag or `main` (manual approval for prod)
- [ ] Branch protection on `main` (require CI green)

---

## 3. Deploy steps (template)

### Backend (FastAPI)

1. Build container or install package on host
2. Set env vars and data volume mount (`data/`)
3. Run: `khukra-api` or `uvicorn khukra.api.main:app --host 0.0.0.0 --port 8000`
4. Verify: `GET /docs`, `GET /api/health` (if added), auth login

### Frontend (Next.js)

1. `npm ci && npm run build`
2. Set `NEXT_PUBLIC_API_URL=https://api.<your-domain>`
3. `npm run start` or platform static export (if applicable)
4. Verify: login, `/research`, `/platform?module=overview`

### Post-deploy smoke

- [ ] Login with admin account
- [ ] `POST /api/inference` (or research run) succeeds
- [ ] `GET /api/platform/manifest` returns modules
- [ ] Warehouse file created/updated on disk
- [ ] Export endpoint returns CSV/PDF

---

## 4. Environment variables (production)

| Variable | Required | Notes |
|----------|----------|-------|
| `KHUKRA_SECRET_KEY` | Yes | JWT signing; rotate on compromise |
| `KHUKRA_ADMIN_EMAIL` | Yes | Bootstrap only if no users exist |
| `KHUKRA_ADMIN_PASSWORD` | Yes | Strong password; disable bootstrap after setup |
| `NEXT_PUBLIC_API_URL` | Yes (frontend) | Public API base URL |
| `KHUKRA_DATA_ROOT` | Optional | If data dir not `./data` |

---

## 5. Rollback

- Keep previous container image / release tag
- Restore warehouse snapshot before schema changes
- Document one-command rollback for API and UI hosts

---

## 6. After first deploy

- [ ] Open GitHub Issues for gaps found during deploy
- [ ] Update [roadmap.md](./roadmap.md) Phase 1 items to Done
- [ ] Schedule Phase 2 (roles, audit, observability)

---

## 7. Local reference (dev)

```powershell
cd C:\Users\ahmed\khukra
.venv\Scripts\Activate.ps1
khukra-api
# separate terminal
cd frontend; npm run dev
```

- UI: http://localhost:3000  
- API: http://localhost:8000/docs
