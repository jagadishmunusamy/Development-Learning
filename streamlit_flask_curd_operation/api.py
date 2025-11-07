from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, asc
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

#---- Config ----
DB_URL = "sqlite:///company_db" #swaplater for mysql/mssql
engine = create_engine(DB_URL, connect_args={"check_same_thread":False})
Session_Local = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

#---- Model ----
class Employees(Base):
    __tablename__ = "employees"
    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    department = Column(String(120), nullable=False)
    salary = Column(Float, nullable=False)

Base.metadata.create_all(engine)

#---- App ----
app = Flask(__name__)

#allow streamlit (default http://localhost:8501)
CORS(app, resources={r"/*":{"origins":["http://localhost:8501","http://127.0.0.1:8501"]}})

@app.get("/health")
def health():
    return jsonify({"status" : "ok"})

# [READ] get employees
@app.get("/employees")
def employees_details():
    s = Session_Local()
    try:
        rows = s.query(Employees).order_by(Employees.id.asc()).all()
        out = [{"id": r.id, "name": r.name, "department": r.department, "salary": r.salary} for r in rows]
        return jsonify(out), 200
    except Exception as e:
        return jsonify({"message": f"Read failed: {e}"}), 500
    finally:
        s.close()

# [CREATE] create new employee
@app.post("/employees")
def create_employees():
    data = request.get_json(force=True)
    required = ["name", "department", "salary"]
    missing = [k for k in required if data.get(k) in (None, "")]
    if missing:
        return {"message" : f"missing : {', '.join(missing)}"}, 400
    s = Session_Local()
    emp = Employees(name=data['name'], department=data['department'], salary=data['salary'])
    s.add(emp)
    s.commit()
    out = {"id" : emp.id, "name" : emp.name, "department" : emp.department, "salary" : emp.salary}
    s.close()
    return out, 201

# [UPDATE]
@app.put('/employees/<int:emp_id>')
def update_employee(emp_id):
    data =request.get_json()
    s = Session_Local()
    emp = s.query(Employees).get(emp_id)
    if not emp:
        s.close()
        return jsonify({"message" : "Employee not found"}), 404
    if "name" in data and data["name"] != "": emp.name = data["name"]
    if "department" in data and data["department"] != "": emp.department = data["department"]
    if "salary" in data and data["salary"] is not None: emp.salary = float(data["salary"])
    s.commit()
    out = {"id": emp.id, "name" : emp.name, "department" : emp.department, "salary" : emp.salary}
    s.close()
    return out, 200

# [DELETE] remove employee
@app.delete('/employees/<int:emp_id>')
def delete_employee(emp_id):
    s = Session_Local()
    try:
        emp = s.query(Employees).get(emp_id)
        if not emp:
            s.close()
            return jsonify({"message": "Employee not found"}), 404
        s.delete(emp)
        s.commit()                              # ✅ commit the deletion
        return jsonify({"deleted": emp_id}), 200
    except Exception as e:
        s.rollback()
        return jsonify({"message": f"Delete failed: {e}"}), 500
    finally:
        s.close()

if __name__ == "__main__":
    app.run(port=5000, debug=True)