from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

app = FastAPI()

DATABASE_URL = 'postgresql://postgres:root@localhost:5432/chicago'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    DepartmentID = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    Region = Column(String)
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    EmployeeID = Column(Integer, primary_key=True, index=True)
    DepartmentID = Column(Integer, ForeignKey('departments.DepartmentID'))
    Name = Column(String)
    Birthday = Column(String)
    Salary = Column(Float)
    Job = Column(String)
    department = relationship("Department", back_populates="employees")
    job_histories = relationship("JobHistory", back_populates="employee")

class JobHistory(Base):
    __tablename__ = "job_histories"
    JobHistoryID = Column(Integer, primary_key=True, index=True)
    EmployeeID = Column(Integer, ForeignKey('employees.EmployeeID'))
    Title = Column(String)
    StartDate = Column(String)
    EndDate = Column(String)
    Salary = Column(Float)
    Job = Column(String)
    employee = relationship("Employee", back_populates="job_histories")

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# -------- CRUD para Department --------- #
@app.get("/departments")
def read_departments():
    departments = session.query(Department).all()
    departments_list = [{"DepartmentID": department.DepartmentID, "Name": department.Name, "Region": department.Region} for department in departments]
    return JSONResponse(content=departments_list)

@app.get("/departments/{department_id}")
def read_department(department_id: int):
    department = session.query(Department).filter(Department.DepartmentID == department_id).first()
    if not department:
        return JSONResponse(content={"detail": "Department not found"}, status_code=404)
    
    employees = session.query(Employee).filter(Employee.DepartmentID == department_id).all()
    employees_list = []
    
    for employee in employees:
        employee_data = {
            "EmployeeID": employee.EmployeeID,
            "Name": employee.Name,
            "Birthday": employee.Birthday,
            "Salary": employee.Salary,
            "Job": employee.Job,
            "JobHistories": []
        }
        
        job_histories = session.query(JobHistory).filter(JobHistory.EmployeeID == employee.EmployeeID).all()
        for job_history in job_histories:
            job_history_data = {
                "JobHistoryID": job_history.JobHistoryID,
                "Title": job_history.Title,
                "StartDate": job_history.StartDate,
                "EndDate": job_history.EndDate,
                "Salary": job_history.Salary,
                "Job": job_history.Job
            }
            employee_data["JobHistories"].append(job_history_data)
        
        employees_list.append(employee_data)
    
    return JSONResponse(content={"DepartmentID": department.DepartmentID, "Name": department.Name, "Region": department.Region, "Employees": employees_list})


@app.post("/departments")
def create_department(name: str, region: str):
    department = Department(Name=name, Region=region)
    session.add(department)
    session.commit()
    return JSONResponse(content={"DepartmentID": department.DepartmentID, "Name": department.Name, "Region": department.Region})

@app.put("/departments/{department_id}")
def update_department(department_id: int, name: str, region: str):
    department = session.query(Department).filter(Department.DepartmentID == department_id).first()
    if not department:
        return JSONResponse(content={"detail": "Department not found"}, status_code=404)
    department.Name = name
    department.Region = region
    session.commit()
    return JSONResponse(content={"DepartmentID": department.DepartmentID, "Name": department.Name, "Region": department.Region})

@app.delete("/departments/{department_id}")
def delete_department(department_id: int):
    department = session.query(Department).filter(Department.DepartmentID == department_id).first()
    if not department:
        return JSONResponse(content={"detail": "Department not found"}, status_code=404)
    session.delete(department)
    session.commit()
    return JSONResponse(content={"Departament deleted with ID": department.DepartmentID })

# -------- CRUD para Employee --------- #
@app.get("/employees")
def read_employees():
    employees = session.query(Employee).all()
    employees_list = [{"EmployeeID": employee.EmployeeID, "Name": employee.Name, "Birthday": employee.Birthday, "Salary": employee.Salary, "Job": employee.Job, "DepartmentID": employee.DepartmentID} for employee in employees]
    return JSONResponse(content=employees_list)

@app.get("/employees/{employee_id}")
def read_employee(employee_id: int):
    employee = session.query(Employee).filter(Employee.EmployeeID == employee_id).first()
    if not employee:
        return JSONResponse(content={"detail": "Employee not found"}, status_code=404)
    job_histories = session.query(JobHistory).filter(JobHistory.EmployeeID == employee_id).all()
    job_histories_list = [{"JobHistoryID": job_history.JobHistoryID, "Title": job_history.Title, "StartDate": job_history.StartDate , "EndDate": job_history.EndDate , "Salary": job_history.Salary, "Job": job_history.Job} for job_history in job_histories]
    return JSONResponse(content={"EmployeeID": employee.EmployeeID, "Name": employee.Name, "Birthday": employee.Birthday , "Salary": employee.Salary, "Job": employee.Job, "DepartmentID": employee.DepartmentID, "JobHistories": job_histories_list})

@app.post("/employees")
def create_employee(name: str, birthday: str, salary: float, job: str, department_id: int):
    
    employee = Employee(Name=name, Birthday=birthday , Salary=salary, Job=job, DepartmentID=department_id)
    session.add(employee)
    session.commit()
    return JSONResponse(content={"EmployeeID": employee.EmployeeID, "Name": employee.Name, "Birthday": employee.Birthday , "Salary": str(employee.Salary), "Job": employee.Job, "DepartmentID": employee.DepartmentID})

@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, name: str, birthday: str, salary: float, job: str, department_id: int):    
    employee = session.query(Employee).filter(Employee.EmployeeID == employee_id).first()
    if not employee:
        return JSONResponse(content={"detail": "Employee not found"}, status_code=404)
    employee.Name = name
    employee.Birthday = birthday
    employee.Salary = salary
    employee.Job = job
    employee.DepartmentID = department_id
    session.commit()
    return JSONResponse(content={"EmployeeID": employee.EmployeeID, "Name": employee.Name, "Birthday": employee.Birthday, "Salary": employee.Salary, "Job": employee.Job, "DepartmentID": employee.DepartmentID})

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    employee = session.query(Employee).filter(Employee.EmployeeID == employee_id).first()
    if not employee:
        return JSONResponse(content={"detail": "Employee not found"}, status_code=404)
    session.delete(employee)
    session.commit()
    return JSONResponse(content={"EmployeeID": employee.EmployeeID, "Name": employee.Name, "Birthday": employee.Birthday, "Salary": employee.Salary, "Job": employee.Job, "DepartmentID": employee.DepartmentID})


# -------- CRUD para JobHistory --------- #

@app.get("/job_histories")
def read_job_histories():
    job_histories = session.query(JobHistory).all()
    job_histories_list = [{"JobHistoryID": job_history.JobHistoryID, "Title": job_history.Title, "StartDate": job_history.StartDate, "EndDate": job_history.EndDate, "Salary": str(job_history.Salary), "Job": job_history.Job, "EmployeeID": job_history.EmployeeID} for job_history in job_histories]
    return JSONResponse(content=job_histories_list)

@app.get("/job_histories/{job_history_id}")
def read_job_history(job_history_id: int):
    job_history = session.query(JobHistory).filter(JobHistory.JobHistoryID == job_history_id).first()
    if not job_history:
        return JSONResponse(content={"detail": "JobHistory not found"}, status_code=404)
    return JSONResponse(content={"JobHistoryID": job_history.JobHistoryID, "Title": job_history.Title, "StartDate": job_history.StartDate, "EndDate": job_history.EndDate, "Salary": str(job_history.Salary), "Job": job_history.Job, "EmployeeID": job_history.EmployeeID})

@app.post("/job_histories")
def create_job_history(title: str, start_date: str, end_date: str, salary: float, job: str, employee_id: int):

    job_history = JobHistory(Title=title, StartDate=start_date, EndDate=end_date, Salary=salary, Job=job, EmployeeID=employee_id)
    session.add(job_history)
    session.commit()
    return JSONResponse(content={"JobHistoryID": job_history.JobHistoryID, "Title": job_history.Title, "StartDate": job_history.StartDate, "EndDate": job_history.EndDate, "Salary": str(job_history.Salary), "Job": job_history.Job, "EmployeeID": job_history.EmployeeID})

@app.put("/job_histories/{job_history_id}")
def update_job_history(job_history_id: int, title: str, start_date: str, end_date: str, salary: float, job: str, employee_id: int):
    job_history = session.query(JobHistory).filter(JobHistory.JobHistoryID == job_history_id).first()
    if not job_history:
        return JSONResponse(content={"detail": "JobHistory not found"}, status_code=404)
    job_history.Title = title
    job_history.StartDate = start_date
    job_history.EndDate = end_date
    job_history.Salary = salary
    job_history.Job = job
    job_history.EmployeeID = employee_id
    session.commit()
    return JSONResponse(content={"JobHistoryID": job_history.JobHistoryID, "Title": job_history.Title, "StartDate": job_history.StartDate, "EndDate": job_history.EndDate, "Salary": str(job_history.Salary), "Job": job_history.Job, "EmployeeID": job_history.EmployeeID})

@app.delete("/job_histories/{job_history_id}")
def delete_job_history(job_history_id: int):
    job_history = session.query(JobHistory).filter(JobHistory.JobHistoryID == job_history_id).first()
    if not job_history:
        return JSONResponse(content={"detail": "JobHistory not found"}, status_code=404)
    session.delete(job_history)
    session.commit()
    return JSONResponse(content={"JobHistoryID": job_history.JobHistoryID, "Title": job_history.Title, "StartDate": job_history.StartDate, "EndDate": job_history.EndDate, "Salary": str(job_history.Salary), "Job": job_history.Job, "EmployeeID": job_history.EmployeeID})