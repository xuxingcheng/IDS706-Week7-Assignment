"""Run with: streamlit run app.py"""
import json
import os
from pathlib import Path

import pandas as pd
import psycopg2
import requests
import streamlit as st

from services import sign_in, sign_up, run_query, save_answer, load_answer

st.set_page_config(page_title="Campus Food SQL Quiz", page_icon="🍽️")
st.title("Campus Food SQL Quiz")
st.write("Five questions · 4 points each · 20 points total")
st.write("Write SQL using our six fictional restaurants. Run your answer, compare the result with the hint, and save your work.")

# Community Cloud supplies root-level secrets as environment variables.
required = ["SUPABASE_URL", "SUPABASE_KEY", "DB_HOST", "POSTGRES_USER", "POSTGRES_PASSWORD"]
if any(not os.getenv(key) for key in required):
    st.info("The quiz needs Supabase configuration. Follow the setup steps in README.md.")
    st.stop()

with st.sidebar:
    st.header("Your account")
    if st.session_state.get("token"):
        st.write(st.session_state.get("email", "Signed in"))
        if st.button("Sign out"):
            st.session_state.clear()
            st.rerun()
    else:
        with st.form("login", clear_on_submit=False):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Sign in")
            register = st.form_submit_button("Create account")
        try:
            if login:
                st.session_state.token = sign_in(email.strip(), password)
                st.session_state.email = email.strip()
                st.rerun()
            if register:
                result = sign_up(email.strip(), password)
                if result.get("access_token"):
                    st.session_state.token = result["access_token"]
                    st.session_state.email = email.strip()
                    st.rerun()
                st.success("Check your inbox and spam folder for a confirmation email, then sign in. If you already registered, try Sign in instead.")
        except ValueError as exc:
            st.error(str(exc))
        except requests.RequestException:
            st.error("Could not reach Supabase. Check your internet connection and try again.")

token = st.session_state.get("token")
if not token:
    st.info("Sign in to run queries and save answers.")

st.code("restaurants(id, name, cuisine, avg_cost, rating, distance_miles)", language="text")
st.caption("avg_cost is dollars, rating is out of 5, and distance_miles is miles from campus.")
questions = json.loads(Path(__file__).with_name("questions.json").read_text())
question = st.selectbox("Choose a question", questions,
                        format_func=lambda q: f"Q{q['id']}. {q['title']} — {q['points']} points")
st.write(question["question"])
with st.expander("Hint: expected SQL and result"):
    st.code(question["sql"], language="sql")
    st.dataframe(pd.DataFrame(question["rows"], columns=question["columns"]), hide_index=True)

editor_key = "answer_" + str(question["id"])
if editor_key not in st.session_state:
    st.session_state[editor_key] = ""
if st.button("Load my saved answer", disabled=not token):
    try:
        st.session_state[editor_key] = load_answer(token, question["id"])
        st.success("Saved answer loaded (blank if you have not saved one).")
    except (ValueError, requests.RequestException):
        st.error("Could not load your answer. Try signing in again.")
query = st.text_area("Your SQL", key=editor_key, height=160, placeholder="SELECT ... FROM restaurants ...;")
run_col, save_col = st.columns(2)
run = run_col.button("Run SQL", disabled=not token, type="primary")
save = save_col.button("Save answer", disabled=not token)
try:
    if run:
        columns, rows = run_query(token, query)
        st.subheader("Your query result")
        st.dataframe(pd.DataFrame(rows, columns=columns), hide_index=True)
        st.caption(f"{len(rows)} row(s). Compare the values and ordering with the hint. This app does not automatically assign grades.")
    if save:
        save_answer(token, question["id"], query)
        st.success("Answer saved to your account.")
except ValueError as exc:
    st.error(str(exc))
except psycopg2.Error:
    st.error("The database could not run this query. Check column names and SQL syntax; the host may also need to check the database setup.")
except requests.RequestException:
    st.error("Could not reach Supabase. Please try again.")
