from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import io
import csv
import os

app = FastAPI()

# Set up BigQuery client
credentials_path = os.path.abspath("gcp-credentials-key.json")
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    tier: str

@app.get("/")
def read_root():
    return {"message": "Loyalty Analytics API is running", "endpoints": {
        "top_customers": "/top-customers/{n}",
        "avg_spend": "/avg-spend?start_date=&end_date=",
        "churn_risk": "/churn-risk?risk_level=High",
        "vip_customers": "/vip-customers",
        "export_report": "/export-report",
        "customer_metrics": "/customer-metrics/{customer_id}"
    }}

@app.get("/top-customers/{n}")
def get_top_customers(n: int, tier: Optional[str] = None):
    query = """
        SELECT customer_id, total_sales as total_spend
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        ORDER BY total_sales DESC
        LIMIT @limit
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", n),
        ]
    )
    
    if tier:
        query = query.replace(";", "") + " WHERE tier = @tier;"
        job_config.query_parameters.append(
            bigquery.ScalarQueryParameter("tier", "STRING", tier)
        )

    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        return JSONResponse({
            "top_customers": [
                {"customer_id": row.customer_id, "total_spend": row.total_spend}
                for row in results
            ]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/avg-spend")
def get_avg_spend(start_date: str, end_date: str):
    query = """
        SELECT AVG(net_amount) as avg_spend
        FROM `de-sumup.store_dataset.transactions`
        WHERE transaction_date BETWEEN @start_date AND @end_date
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
            bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date),
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        row = next(results)
        
        return JSONResponse({"avg_spend": row.avg_spend})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/churn-risk")
def get_churn_risk(risk_level: str = "High"):
    query = """
        SELECT customer_id, total_transactions as transaction_count
        FROM `de-sumup.loyalty_analytics.churn_risk_customers`
        WHERE churn_risk_score = @risk_level
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("risk_level", "STRING", risk_level),
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        return JSONResponse({
            "customers": [
                {"customer_id": row.customer_id, "transaction_count": row.transaction_count}
                for row in results
            ]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vip-customers")
def get_vip_customers():
    query = """
        SELECT customer_id, total_sales, total_transactions
        FROM `de-sumup.loyalty_analytics.vip_customers`
        ORDER BY total_sales DESC
    """
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        
        return JSONResponse({
            "vip_customers": [
                {
                    "customer_id": row.customer_id,
                    "total_sales": row.total_sales,
                    "total_transactions": row.total_transactions
                }
                for row in results
            ]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export-report")
def export_report():
    query = """
        SELECT customer_id, total_sales as total_spend, 
               total_transactions as transaction_count, 
               CASE 
                   WHEN days_since_last_purchase > 90 THEN 'High'
                   WHEN days_since_last_purchase > 60 THEN 'Medium'
                   ELSE 'Low'
               END as churn_risk
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        ORDER BY total_sales DESC
    """
    
    try:
        query_job = client.query(query)
        df = query_job.to_dataframe()
        
        # Create CSV in memory
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        
        return FileResponse(
            io.BytesIO(stream.getvalue().encode()),
            media_type="text/csv",
            filename="customer_report.csv"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customer-metrics/{customer_id}")
def get_customer_metrics(customer_id: str):
    query = """
        SELECT *
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        WHERE customer_id = @customer_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        row = next(results, None)
        
        if not row:
            raise HTTPException(status_code=404, detail="Customer not found")
            
        return JSONResponse({
            "customer_id": row.customer_id,
            "total_transactions": row.total_transactions,
            "total_sales": row.total_sales,
            "avg_transaction_value": row.avg_transaction_value,
            "total_items_purchased": row.total_items_purchased,
            "total_discounts_received": row.total_discounts_received,
            "days_since_last_purchase": row.days_since_last_purchase,
            "last_transaction_date": str(row.last_transaction_date),
            "unique_products_purchased": row.unique_products_purchased
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))