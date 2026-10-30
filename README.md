# KOWAN Lab 8 — Microservices: AWS Lambda + Dokku

Serverless calculator with two AWS Lambda services chained over HTTP
(Function URLs, `AuthType: NONE`) and an interactive frontend
(Tailwind CSS + Three.js) deployed on Dokku.

## Architecture

```
Browser (Dokku, static HTML)
  ├─ Square Area   POST {sisi}  ─▶ Lambda `luas-persegi`
  │                                └─▶ { luas_persegi, satuan }
  └─ Cube Surface  POST {rusuk} ─▶ Lambda `luas-permukaan-kubus`
                                   └─▶ HTTP POST {sisi} ─▶ Lambda `luas-persegi`
                                       └─▶ 6 × luas_sisi
```

## Repository structure

```
.
├── lambda/
│   ├── luas-persegi/lambda_function.py           # Service 1 (Ariana)
│   └── luas-permukaan-kubus/lambda_function.py   # Service 2 (Fikri)
├── frontend/index.html                           # UI (grid layout + 3D cube)
├── Dockerfile                                    # nginx static server for Dokku
└── README.md
```

## Task division

| Member | Name | NPM | Tasks |
|--------|------|-----|-------|
| 1 | Ariana Nurlayla Syabandini | 2206081950 | Lambda `luas-persegi` + Function URL, frontend UI, initial repo & push |
| 2 | Fikri Massaid Wahab | 2206083395 | Lambda `luas-permukaan-kubus`, HTTP call to Lambda 1, UI wiring, Dokku deploy |

## Setup — Member 1 (luas-persegi)

Deployed as a Lambda Function URL with `AuthType: NONE`:

| Item | Value |
|------|-------|
| Function name | `luas-persegi` |
| Runtime | Python 3.12 |
| Function URL | `https://<id>.lambda-url.us-east-1.on.aws/` |

Test outside the console:

```powershell
Invoke-RestMethod -Method Post -Uri "https://<id>.lambda-url.us-east-1.on.aws/" -ContentType "application/json" -Body '{"sisi": 5}'
# { luas_persegi: 25, satuan: "cm^2" }
```

Console test event (supported directly):

```json
{ "sisi": 5 }
```

## Setup — Member 2 (luas-permukaan-kubus)

1. Create Lambda `luas-permukaan-kubus` (Python 3.12) from
   `lambda/luas-permukaan-kubus/lambda_function.py`.
2. Configuration → **Environment variables**:
   `LUAS_PERSEGI_URL` = `<Function URL of luas-persegi>`
3. Configuration → **Function URL** → Create, `AuthType: NONE`.
4. Paste the new URL into `CONFIG.luasKubusUrl` in `frontend/index.html`.
5. Test both menus, commit, and deploy to Dokku:

```bash
dokku apps:create lab8-frontend
git remote add dokku dokku@<host>:lab8-frontend
git push dokku main
```

## Run locally

Open `frontend/index.html` directly in a browser, or:

```bash
docker build -t lab8-frontend .
docker run --rm -p 8080:80 lab8-frontend
```
