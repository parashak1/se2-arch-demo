# se2-arch-demos

Demo applications for **SE-II — Software Architecture & Design** (Sessions 2 & 3).

Each app is the same task manager — same features, same requirements — built a different way. The goal is to see how structural decisions affect your ability to change code over time.

---

## The arc

| App | Folder | Session | Concept |
|-----|--------|---------|---------|
| TaskFlow v1 | `app1-monolith/` | Session 2 | Everything in one file — routes, logic, data, and HTML all mixed together |
| TaskFlow v2 | `app2-layered/` | Session 3 | Same features, split into layers — routes, services, and data separated |
| TaskFlow v3 | `app3-challenge/` | Session 3 | A messy app — you diagnose it and decide how to fix it |

---

## Setup

You need Python 3.8+ and pip.

```bash
git clone https://github.com/[your-org]/se2-arch-demos.git
cd se2-arch-demos
```

Then go into whichever app folder your session needs and follow the README inside.

---

## The two change requests

In Sessions 2 and 3, the instructor will make the same two changes to both App 1 and App 2:

1. **Persist tasks to a file** — tasks should survive a server restart
2. **Sort pending tasks by priority** — high priority tasks appear at the top

Watch what code has to change each time, and where. That difference is the lesson.

---

## Note on `tasks.json`

When you run App 1 after Change Request 1, the app writes a `tasks.json` file locally. This file is gitignored — don't force-add it.