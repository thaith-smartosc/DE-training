from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection parameters
DB_HOST = os.environ.get('DB_HOST', 'mypgserver12345.postgres.database.azure.com')
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'myuser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'mypassword')

def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require' # Use SSL for Azure PostgreSQL
    )

@app.route('/')
def index():
    return "Welcome to the Employee Management API!"

@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    department = data.get('department')

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO employees (name, email, phone, address, department)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (name, email, phone, address, department)
    )
    emp_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Employee created", "employee_id": emp_id}), 201

@app.route('/employees', methods=['GET'])
def get_employees():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, phone, address, department FROM employees;")
    employees = cur.fetchall()
    cur.close()
    conn.close()

    employee_list = [
        {
            "id": emp[0],
            "name": emp[1],
            "email": emp[2],
            "phone": emp[3],
            "address": emp[4],
            "department": emp[5]
        }
        for emp in employees
    ]
    return jsonify(employee_list)

@app.route('/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, phone, address, department FROM employees WHERE id = %s;", (emp_id,))
    employee = cur.fetchone()
    cur.close()
    conn.close()

    if employee:
        emp_data = {
            "id": employee[0],
            "name": employee[1],
            "email": employee[2],
            "phone": employee[3],
            "address": employee[4],
            "department": employee[5]
        }
        return jsonify(emp_data)
    else:
        return jsonify({"error": "Employee not found"}), 404

@app.route('/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    department = data.get('department')

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE employees
        SET email = %s, phone = %s, address = %s, department = %s
        WHERE id = %s;
        """,
        (email, phone, address, department, emp_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": f"Employee {emp_id} updated."})

@app.route('/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id = %s;", (emp_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": f"Employee {emp_id} deleted."})

if __name__ == '__main__':
    # Ensure table exists
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(15),
            address VARCHAR(255),
            department VARCHAR(50) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

    app.run(host='0.0.0.0', port=5000)
