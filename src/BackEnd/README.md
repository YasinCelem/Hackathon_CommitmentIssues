
```
BackEnd/
├─ app/
│  ├─ __init__.py           # creates Flask app, loads swagger config
│  ├─ config.py             # environment and Mongo settings
│  ├─ routes/
│  │   ├─ __init__.py
│  │   ├─ documents.py      # /api/documents endpoints
│  │   ├─ approvals.py      # /api/approvals endpoints
│  │   └─ schedules.py      # /api/schedules endpoints
│  ├─ services/
│  │   ├─ db.py             # Mongo connection
│  │   ├─ diffs.py          # diff helper
│  │   └─ docs.py           # business logic
│  └─ swagger/
│      └─ definitions.yml   # reusable swagger specs (optional)
│
├─ .env
├─ requirements.txt
├─ wsgi.py
└─ README.md

```