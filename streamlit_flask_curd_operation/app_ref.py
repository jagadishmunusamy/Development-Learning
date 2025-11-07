import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:5000"

st.set_page_config(page_title="Flask + Streamlit CRUD", page_icon="🧰")
st.title("🧰 Employees — CRUD (Flask API + Streamlit UI)")

# Health
try:
    r = requests.get(f"{API}/health", timeout=3)
    st.caption(f"Backend: {r.json()}")
except Exception as e:
    st.error(f"Cannot reach backend at {API} → {e}")

# Helpers
def load_rows():
    r = requests.get(f"{API}/employees", timeout=5)
    r.raise_for_status()
    return pd.DataFrame(r.json())

def create_row(name, dept, salary):
    r = requests.post(f"{API}/employees", json={"name": name, "department": dept, "salary": salary}, timeout=5)
    r.raise_for_status()
    return r.json()

def update_row(emp_id, name, dept, salary):
    r = requests.put(f"{API}/employees/{emp_id}",
                     json={"name": name, "department": dept, "salary": salary}, timeout=5)
    r.raise_for_status()
    return r.json()

def delete_row(emp_id):
    r = requests.delete(f"{API}/employees/{emp_id}", timeout=5)
    r.raise_for_status()
    return r.json()

# Tabs: Read / Create / Update / Delete
tab_read, tab_create, tab_update, tab_delete = st.tabs(["📖 Read", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab_read:
    st.subheader("All employees")
    if st.button("Refresh"):
        st.session_state["_ref"] = not st.session_state.get("_ref", False)
    try:
        df = load_rows()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Load failed: {e}")

with tab_create:
    st.subheader("Create new employee")
    c1, c2 = st.columns(2)
    name = c1.text_input("Name")
    dept = c2.text_input("Department")
    salary = st.number_input("Salary", min_value=0.0, step=100.0)
    if st.button("Create"):
        try:
            res = create_row(name, dept, salary)
            st.success(f"Created ID {res['id']}")
        except Exception as e:
            st.error(f"Create failed: {e}")

with tab_update:
    st.subheader("Update employee")
    try:
        df = load_rows()
        ids = df["id"].tolist() if not df.empty else []
        emp_id = st.selectbox("Choose ID", ids)
        if emp_id:
            row = df[df["id"] == emp_id].iloc[0]
            c1, c2 = st.columns(2)
            name_u = c1.text_input("Name", value=row["name"])
            dept_u = c2.text_input("Department", value=row["department"])
            salary_u = st.number_input("Salary", value=float(row["salary"] or 0.0), step=100.0)
            if st.button("Save changes"):
                try:
                    res = update_row(int(emp_id), name_u, dept_u, salary_u)
                    st.success(f"Updated ID {res['id']}")
                except Exception as e:
                    st.error(f"Update failed: {e}")
    except Exception as e:
        st.error(f"Could not load employees: {e}")

with tab_delete:
    st.subheader("Delete employee")
    try:
        df = load_rows()
        ids = df["id"].tolist() if not df.empty else []
        emp_id_d = st.selectbox("Choose ID to delete", ids, key="del_id")
        if st.button("Delete selected"):
            try:
                res = delete_row(int(emp_id_d))
                st.success(f"Deleted ID {res['deleted']}")
            except Exception as e:
                st.error(f"Delete failed: {e}")
    except Exception as e:
        st.error(f"Could not load employees: {e}")
