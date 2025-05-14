from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List
import psycopg2
import csv
import io

app = FastAPI()

# Database connection
conn = psycopg2.connect(
    dbname="loyalty_db",
    user="admin",
    password="admin",
    host="postgres"
)

class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    tier: str

@app.get("/top-customers/{n}")
def get_top_customers(n: int, tier: str = None):
    cur = conn.cursor()

    query = """
        SELECT customer_id, total_spend
        FROM customer_metrics
        ORDER BY total_spend DESC
        LIMIT %s
    """
    params = [n]

    if tier:
        query = query.replace(";", "") + " WHERE tier = %s;"
        params.append(tier)

    cur.execute(query, params)
    results = cur.fetchall()

    return JSONResponse({
        "top_customers": [
            {"customer_id": row[0], "total_spend": row[1]}
            for row in results
        ]
    })

@app.get("/avg-spend")
def get_avg_spend(start_date: str, end_date: str):
    cur = conn.cursor()

    cur.execute("""
        SELECT AVG(amount)
        FROM transactions
        WHERE timestamp BETWEEN %s AND %s
    """, (start_date, end_date))

    avg_spend = cur.fetchone()[0]

    return JSONResponse({"avg_spend": avg_spend})

@app.get("/churn-risk")
def get_churn_risk(risk_level: str = "high"):
    cur = conn.cursor()

    cur.execute("""
        SELECT customer_id, transaction_count
        FROM customer_metrics
        WHERE churn_risk = %s
    """, (risk_level,))

    results = cur.fetchall()

    return JSONResponse({
        "customers": [
            {"customer_id": row[0], "transaction_count": row[1]}
            for row in results
        ]
    })

@app.get("/export-report")
def export_report():
    cur = conn.cursor()

    cur.execute("""
        SELECT customer_id, total_spend, transaction_count, churn_risk
        FROM customer_metrics
        ORDER BY total_spend DESC
    """)

    results = cur.fetchall()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["customer_id", "total_spend", "transaction_count", "churn_risk"])
    writer.writerows(results)

    output.seek(0)

    return FileResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        filename="customer_report.csv"
    )
