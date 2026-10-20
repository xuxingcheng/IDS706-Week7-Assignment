# Campus Food SQL Quiz

A beginner SQL quiz using Python, Streamlit, and a hosted Supabase PostgreSQL database.
The topic is six fictional restaurants near campus. Five SQL questions are worth four
points each, for a total of **20 points**.

**Quiz site URL: not deployed yet. Replace this line with the real Streamlit URL before submitting.**

**Current status:** local implementation only. Supabase setup, live authentication,
cloud deployment, and a successful GitHub Actions run still need to be completed.
The presence of a workflow file does not mean Actions has run successfully.

## How it follows the class lab

The [class lesson](https://androidilicious.github.io/ids-706-postgresql/) used
Python, `psycopg2`, `python-dotenv`, a restaurant table, and a Supabase Session pooler.
This project keeps that approach and adds a Streamlit page and Supabase Auth.
The restaurant data here is fictional and separate from the class database.

- `app.py`: the quiz page, account form, SQL editor, and results table.
- `services.py`: sign-in, saving/loading answers, and database queries.
- `setup.sql`: creates the tables, sample data, and permissions.
- `questions.json`: all five questions, SQL hints, and expected result tables.
- `check_database.py`: checks the five hints against real hosted Postgres data.
- `.github/workflows/check.yml`: offline tests and the live database check.
- `.env.example`: configuration template containing no real credentials.

## 1. Create your Supabase project

1. Sign in at [Supabase](https://supabase.com/dashboard) and create a project.
2. Open **SQL Editor**, paste `setup.sql`, and run it once.
3. In a separate private SQL Editor query, set a strong password for the reader:

   ```sql
   ALTER ROLE quiz_reader WITH PASSWORD 'replace-with-your-own-long-random-password';
   ```

   Never paste the actual password into a tracked file. This is the **quiz_reader
   password**, not the project's postgres administrator password.
4. Open **Connect → Session pooler**. Copy the host and use port `5432`.
   Do not select Direct connection or Transaction pooler.
5. The app username is `quiz_reader.YOUR-PROJECT-REF`. Replace the `postgres`
   prefix in the connection example with `quiz_reader`, keeping the project suffix.
6. Find the project URL and publishable key (or legacy anon key) in the project's
   API settings/Connect dialog. Do not use a secret or service-role API key.
7. Under **Authentication → Providers**, ensure email/password login is enabled.
   With email confirmation enabled, users must confirm the email before signing in.

Supabase is the database/authentication service. GitHub stores the code, and
Streamlit Community Cloud will host the Python app. They have separate setup steps.

## 2. Run locally

Use Python 3.11 or newer. In the repository folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` on your computer:

```dotenv
SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
SUPABASE_KEY=YOUR-PUBLISHABLE-OR-ANON-KEY
POSTGRES_DB=postgres
POSTGRES_USER=quiz_reader.YOUR-PROJECT-REF
POSTGRES_PASSWORD=YOUR-QUIZ-READER-PASSWORD
DB_HOST=YOUR-SESSION-POOLER-HOST
DB_PORT=5432
DB_SSLMODE=require
```

Then start the app:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit. `.env` and `.streamlit/secrets.toml`
are ignored by Git. The connection code always enforces `sslmode=require`.

## 3. Use the quiz

1. Create an account in the sidebar. Confirm your email if required.
2. Sign in and select a question.
3. Write a `SELECT` query in the editor, then click **Run SQL**.
4. Your result table appears below. Open the hint to compare SQL and expected rows.
5. Click **Save answer** to store the current question's SQL in your account.
6. Return later, sign in, select the question, and click **Load my saved answer**.
7. Repeat for the remaining questions. Saving replaces your previous answer for
   that question; it does not submit a grade.

The questions cover filtering, sorting, `LIMIT`, `AND`, `COUNT`, `GROUP BY`,
and `AVG`. All expected rows are in `questions.json` and visible in the app.
Equivalent SQL is welcome; compare the result values and requested ordering,
not the query text. This app does not automatically grade answers.

Signed-out visitors can read questions and hints, but Run, Save, and Load are
disabled. The Python helpers also verify the session with Supabase on each action.
If the session expires, sign out and sign back in.

## 4. GitHub Actions and Secrets

Once you are ready to publish the local code to GitHub:

1. In this repository, open **Settings → Secrets and variables → Actions**.
2. Add these three **repository secrets** using the values from `.env`:

   | Secret | Value |
   | --- | --- |
   | `DB_HOST` | Session pooler hostname |
   | `POSTGRES_USER` | `quiz_reader.YOUR-PROJECT-REF` |
   | `POSTGRES_PASSWORD` | The reader password |

3. When the code is on `main`, open **Actions → Check SQL quiz → Run workflow**.
   Pushes to `main` also trigger it. Pull requests run offline tests only.
4. Confirm both `tests` and `live-database` are green. Open the live database step;
   it should print a matching-result message for each of the five questions.
5. Before submitting, record the successful workflow run URL here:
   **Successful Actions run: pending.**

The workflow reads the password from `${{ secrets.POSTGRES_PASSWORD }}`.
It fails if the secrets are absent or the real database results differ from the hints.
Do not paste credentials into the YAML. A skipped live check on a pull request
is not evidence that the hosted database works.

## 5. Host the quiz site

1. Once the repository code is published, sign in to
   [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Create an app using `xuxingcheng/IDS706-Week7-Assignment`, branch `main`,
   and entrypoint `app.py`. Select Python 3.11.
3. In **Advanced settings → Secrets**, enter these values as TOML:

   ```toml
   SUPABASE_URL = "https://YOUR-PROJECT-REF.supabase.co"
   SUPABASE_KEY = "YOUR-PUBLISHABLE-OR-ANON-KEY"
   POSTGRES_DB = "postgres"
   POSTGRES_USER = "quiz_reader.YOUR-PROJECT-REF"
   POSTGRES_PASSWORD = "YOUR-QUIZ-READER-PASSWORD"
   DB_HOST = "YOUR-SESSION-POOLER-HOST"
   DB_PORT = "5432"
   DB_SSLMODE = "require"
   ```

4. Deploy and copy the actual app URL into the top of this README.
5. In Supabase Authentication URL Configuration, set the Site URL to the deployed
   app URL so confirmation emails return visitors to the quiz.
6. Test a new account on the deployed site, run every hint, save an answer,
   sign out, sign back in, and load it. Use a second account to confirm saved
   answers are private.

GitHub Pages cannot run this Python server. Use the Streamlit URL as the quiz URL.
See [Streamlit's secrets instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
and [Supabase's password authentication guide](https://supabase.com/docs/guides/auth/passwords).

## Permissions and limitations

- Student SQL runs as `quiz_reader`, with SELECT access to the quiz data, in a
  read-only transaction. Never configure the app with the `postgres` admin login.
- The SQL parser permits basic SELECT expressions on `restaurants` only. It rejects
  multiple statements, writes, other tables, and arbitrary function calls. More
  advanced SQL is intentionally outside this beginner quiz.
- Each query has a five-second timeout, a 5,000-character input limit, and a
  200-row result limit.
- Saved answers use the user's Supabase token. Row-level security permits each
  authenticated user to read, insert, and update only their own answers.
- Saved SQL is sent as JSON data, never interpolated into an INSERT string. The
  quiz runner intentionally executes student SQL after validation; an entire
  SQL statement cannot be passed as a value parameter. We do not claim the
  optional parameterized-query extra credit.
- No audit log or audit-log-integrity extra credit is claimed.
- This is a small teaching app, not a general-purpose public SQL console.

## Tests and final checklist

```bash
python -m unittest discover -s tests -v
python check_database.py
```

The first command checks the fixed hints offline, rejects unsafe SQL, checks
session guards, and exercises the UI. The second requires your `.env` and checks
actual hosted PostgreSQL. Offline tests are not proof of a working deployment.

Before submitting:

- [ ] Supabase tables exist and the reader login works over the Session pooler.
- [ ] A classmate can create an account, sign in, run SQL, and see correct rows.
- [ ] Saved answers survive signing out and back in.
- [ ] Signed-out visitors cannot run or save.
- [ ] All five hints match the live results, totaling 20 points.
- [ ] GitHub Actions has a successful run using the repository Secrets.
- [ ] This README contains the actual quiz URL and successful Actions run URL.
- [ ] No real passwords, `.env`, or secrets files are committed.

Submit the GitHub repository URL:
https://github.com/xuxingcheng/IDS706-Week7-Assignment
