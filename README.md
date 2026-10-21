# Campus Food SQL Quiz

A SQL quiz about six fictional restaurants near campus. There are **five questions worth 4 points each, for 20 points total**.

**Quiz website:** [Add the deployed Streamlit URL here.](https://ids706-week7-assignment-eal7qfhxltyx4amvaqtatz.streamlit.app/)

## How to use

1. Open the quiz website and click **Create account**. Confirm your email, then **Sign in**.
2. Choose a question and type your SQL query.
3. Click **Run SQL** to see the result table from the live database.
4. Expand **Hint: expected SQL and result** to compare your answer.
5. Click **Save answer** to save your work. Use **Load my saved answer** when you return.
6. Repeat for all five questions.

You must sign in to run queries or save answers. Only `SELECT` queries on the `restaurants` table are allowed. Answers are compared by their results, not exact SQL wording; the app does not automatically assign grades.

## How it works

The app uses Python and Streamlit, with Supabase PostgreSQL for the restaurant data and Supabase Auth for sign-in. Python connects through the Session pooler using SSL and a read-only database account. Saved answers are private to each user. The GitHub Actions workflow tests the app and checks the five expected results against the database using GitHub Secrets.
