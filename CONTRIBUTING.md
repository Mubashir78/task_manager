# Contributing to DevBoard

Welcome! DevBoard is an open-hours project built on top of the [Navas Task Manager API](https://dev.to/navas_herbert/building-a-rest-api-with-fastapi-from-scratch-full-crud-sqlite-middleware-cors-j92).
The goal is to evolve a basic FastAPI CRUD app into a full collaborative task board - one PR at a time.

Every merged contribution is a real open source commit on your GitHub profile. 

---

## How to Contribute

### 1. Fork the repo

Click the **Fork** button at the top right of this page.

### 2. Clone your fork

```bash
git clone git@github.com:Navashub/task_manager.git
cd task_manager
```

### 3. Create a branch

Use this naming convention:

```bash
git checkout -b feature/your-issue-name
# e.g. feature/add-priority-field
# e.g. fix/pagination-off-by-one
```

### 4. Make your changes

- Keep changes focused on the issue you picked.
- Follow the existing code style (snake_case, type hints, Pydantic schemas).
- Test your changes locally before submitting.

### 5. Commit with a clear message

```bash
git add .
git commit -m "feat: add priority field to Task model (#1)"
```

Prefix convention:
- `feat:` - new feature
- `fix:` - bug fix
- `docs:` - documentation only
- `test:` - adding or updating tests
- `refactor:` - code change with no feature/fix

### 6. Push and open a Pull Request

```bash
git push origin feature/your-issue-name
```

Then open a PR on GitHub against the `main` branch of `Navashub/task_manager`.

---

## PR Checklist

Before submitting, make sure:

- [ ] The app still runs (`uvicorn main:app --reload`)
- [ ] Your endpoint(s) appear and work in `/docs`
- [ ] You haven't introduced unused imports or dead code
- [ ] You've updated the README if you added a new endpoint or changed behaviour
- [ ] Your branch name matches the issue you're solving

---

## Picking an Issue

Issues are labelled by difficulty:

| Label | Who it's for |
|---|---|
| `good-first-issue` | Just getting started with FastAPI |
| `intermediate` | Comfortable with models, schemas, routers |
| `advanced` | Ready for auth, testing, or DevOps |
| `frontend` | HTML/CSS/JS or React work |
| `devops` | Docker, PostgreSQL, deployment |

Comment on an issue before starting so others know it's taken.

---

## Questions?

Reach out on WhatsApp or open a GitHub Discussion. Don't be afraid to ask - that's what open hours is for.
