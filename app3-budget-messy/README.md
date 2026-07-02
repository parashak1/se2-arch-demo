# BudgetFlow v1 — The Challenge App

**SE-II Session 3 — App 3 Group Activity**

A personal budget tracker. Add income and expenses, see your balance, filter by category. It works perfectly.

## Run it

```bash
pip install flask
python app.py
```

Open http://localhost:5000

## Your task

Do NOT fix the code yet. Read it first.

Find as many architectural problems as you can. Look for:

- Logic that does not belong in a route function
- Calculations that appear more than once
- A growing if/elif chain that would hurt to extend
- Side effects (logging, printing) mixed in with business logic
- Missing layers — what would you name them?

Then answer:

1. What are the violations? List at least five with line numbers.
2. How would you split this into layers? Name the files.
3. Where does Strategy pattern apply and why?
4. Where does Observer pattern apply and why?
5. What single change request would hurt the most in this codebase right now?

## Hint

The violations follow the same patterns you saw in TaskFlow v1.
Same problems. Different domain. Different enough that you have to think.
