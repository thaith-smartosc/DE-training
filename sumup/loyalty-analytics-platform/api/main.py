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

@app.get("/")
def list_apis():
    return JSONResponse({
        "message": "Welcome to the Loyalty Analytics API",
        "endpoints": [
            "/top-customers/{n}",
            "/avg-spend",
            "/churn-risk",
            "/vip-customers",
            "/export-report",
            "/customer-metrics/{customer_id}"
        ]
    })

@app.get("/top-customers/{n}")
def get_top_customers(n: int, tier: Optional[str] = None):
    query = """
        SELECT 
            customer_id,
            total_transactions,
            total_purchased,
            total_items_purchased,
            days_since_last_purchase
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        ORDER BY total_purchased DESC
        LIMIT @limit
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", n)
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        return JSONResponse({
            "top_customers": [{
                "customer_id": row.customer_id,
                "total_transactions": row.total_transactions,
                "total_purchased": float(row.total_purchased),
                "total_items": row.total_items_purchased,
                "days_since_last_purchase": row.days_since_last_purchase
            } for row in results]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-avg-spend")
def get_avg_spend(start_date: str, end_date: str):
    query = """
        SELECT 
            AVG(total_purchased / total_transactions) as avg_spend
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        WHERE last_update_time BETWEEN @start_date AND @end_date
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
        
        return JSONResponse({
            "avg_spend": float(row.avg_spend) if row.avg_spend else 0.0
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/churn-risk")
def get_churn_risk(risk_level: str = "High", limit: int = 10):
    query = """
        SELECT 
            customer_id,
            total_transactions,
            days_since_last_purchase
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        WHERE 
            CASE 
                WHEN @risk_level = 'High' THEN days_since_last_purchase > 90
                WHEN @risk_level = 'Medium' THEN days_since_last_purchase BETWEEN 60 AND 90
                WHEN @risk_level = 'Low' THEN days_since_last_purchase BETWEEN 30 AND 60
            END
        ORDER BY days_since_last_purchase DESC
        LIMIT @limit
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("risk_level", "STRING", risk_level),
            bigquery.ScalarQueryParameter("limit", "INT64", limit)
        ]
    )
    if risk_level not in ["High", "Medium", "Low"]:
        raise HTTPException(status_code=400, detail="Invalid risk level. Choose from 'High', 'Medium', or 'Low'.")
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        return JSONResponse({
            "customers": [{
                "customer_id": row.customer_id,
                "total_transactions": row.total_transactions,
                "days_inactive": row.days_since_last_purchase
            } for row in results]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vip-customers")
def get_vip_customers():
    query = """
        SELECT 
            customer_id,
            total_purchased as total_sales,
            total_transactions,
            total_items_purchased,
            days_since_last_purchase
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        WHERE 
            total_purchased > (
                SELECT AVG(total_purchased) * 2 
                FROM `de-sumup.loyalty_analytics.loyalty_analytics`
            )
            AND total_transactions > 10
            AND days_since_last_purchase < 30
        ORDER BY total_purchased DESC
    """
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        
        return JSONResponse({
            "vip_customers": [{
                "customer_id": row.customer_id,
                "total_sales": float(row.total_sales),
                "total_transactions": row.total_transactions,
                "total_items": row.total_items_purchased,
                "days_since_last_purchase": row.days_since_last_purchase
            } for row in results]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/export-report")
# def export_report(limit: int = 100):
#     query = """
#         SELECT 
#             customer_id,
#             total_transactions,
#             total_purchased,
#             total_items_purchased,
#             total_discounts_received,
#             days_since_last_purchase,
#             last_update_time,
#             (total_purchased / total_transactions) as avg_transaction_value,
#             CASE 
#                 WHEN days_since_last_purchase > 90 THEN 'High'
#                 WHEN days_since_last_purchase > 60 THEN 'Medium'
#                 WHEN days_since_last_purchase > 30 THEN 'Low'
#                 ELSE 'Active'
#             END as churn_risk
#         FROM `de-sumup.loyalty_analytics.loyalty_analytics`
#         ORDER BY total_purchased DESC
#         LIMIT @limit
#     """
    
#     job_config = bigquery.QueryJobConfig(
#         query_parameters=[
#             bigquery.ScalarQueryParameter("limit", "INT64", limit)
#         ]
#     )
    
#     try:
#         query_job = client.query(query, job_config=job_config)
#         df = query_job.to_dataframe()
        
#         # Create CSV in memory
#         stream = io.StringIO()
#         df.to_csv(stream, index=False)
#         stream.seek(0)
        
#         return FileResponse(
#             io.BytesIO(stream.getvalue().encode()),
#             media_type="text/csv",
#             filename="customer_report.csv"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/customer-metrics/{customer_id}")
def get_customer_metrics(customer_id: str):
    query = """
        SELECT 
            customer_id,
            total_transactions,
            total_purchased / total_transactions as avg_transaction_value,
            total_items_purchased,
            total_discounts_received,
            days_since_last_purchase,
            last_update_time,
            CASE 
                WHEN days_since_last_purchase > 90 THEN 'High'
                WHEN days_since_last_purchase > 60 THEN 'Medium'
                WHEN days_since_last_purchase > 30 THEN 'Low'
                ELSE 'Active'
            END as churn_risk
        FROM `de-sumup.loyalty_analytics.loyalty_analytics`
        WHERE customer_id = @customer_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "INT64", customer_id)
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
            "avg_transaction_value": float(row.avg_transaction_value),
            "total_items_purchased": row.total_items_purchased,
            "total_discounts_received": float(row.total_discounts_received),
            "days_since_last_purchase": row.days_since_last_purchase,
            "last_update_time": row.last_update_time.isoformat(),
            "churn_risk": row.churn_risk
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
