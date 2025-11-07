from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

# ---- Config ----
DB_URL = "sqlite:///company.db"  # swap later for MySQL/MSSQL
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

# ---- Model ----
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    department = Column(String(120), nullable=False)
    salary = Column(Float, nullable=False)

Base.metadata.create_all(engine)

# ---- App ----
app = Flask(__name__)
# Allow Streamlit (default http://localhost:8501)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8501", "http://127.0.0.1:8501"]}})

@app.get("/health")
def health():
    return {"status": "ok"}

# Read (list)
@app.get("/employees")
def list_employees():
    s = SessionLocal()
    rows = s.query(Employee).order_by(Employee.id.desc()).all()
    out = [{"id": r.id, "name": r.name, "department": r.department, "salary": r.salary} for r in rows]
    s.close()
    return jsonify(out)

# Create
@app.post("/employees")
def create_employee():
    data = request.get_json(force=True)
    required = ["name", "department", "salary"]
    missing = [k for k in required if data.get(k) in (None, "")]
    if missing:
        return {"message": f"Missing: {', '.join(missing)}"}, 400
    s = SessionLocal()
    emp = Employee(name=data["name"], department=data["department"], salary=float(data["salary"]))
    s.add(emp)
    s.commit()
    out = {"id": emp.id, "name": emp.name, "department": emp.department, "salary": emp.salary}
    s.close()
    return out, 201

# Update
@app.put("/employees/<int:emp_id>")
def update_employee(emp_id):
    data = request.get_json(force=True)
    s = SessionLocal()
    emp = s.query(Employee).get(emp_id)
    if not emp:
        s.close()
        return {"message": "Not found"}, 404
    if "name" in data and data["name"] != "": emp.name = data["name"]
    if "department" in data and data["department"] != "": emp.department = data["department"]
    if "salary" in data and data["salary"] is not None: emp.salary = float(data["salary"])
    s.commit()
    out = {"id": emp.id, "name": emp.name, "department": emp.department, "salary": emp.salary}
    s.close()
    return out

# Delete
@app.delete("/employees/<int:emp_id>")
def delete_employee(emp_id):
    s = SessionLocal()
    emp = s.query(Employee).get(emp_id)
    if not emp:
        s.close()
        return {"message": "Not found"}, 404
    s.delete(emp)
    s.commit()
    s.close()
    return {"deleted": emp_id}

if __name__ == "__main__":
    app.run(port=5000, debug=True)
