-- Description: Query to select all records from the sales dataset
SELECT * FROM `kestra-thaith.sales_dataset.sales`

-- Description: Revenue by Region and Segment
SELECT 
  Region,
  Segment,
  COUNT(*) AS total_opportunities,
  SUM(`Forecasted Monthly Revenue`) AS total_forecasted_revenue,
  SUM(`Weighted Revenue`) AS total_weighted_revenue
FROM `kestra-thaith.sales_dataset.sales`
GROUP BY Region, Segment
ORDER BY total_forecasted_revenue DESC;

-- Description: Shows how many leads a salesperson has, how many they closed, and their conversion rate.
SELECT 
  Salesperson,
  COUNT(*) AS total_leads,
  SUM(CASE WHEN `Closed Opportunity` = TRUE THEN 1 ELSE 0 END) AS closed_leads,
  ROUND(SAFE_DIVIDE(SUM(CAST(`Closed Opportunity` AS INT64)), COUNT(*)) * 100, 2) AS conversion_rate_percent
FROM `kestra-thaith.sales_dataset.sales`
GROUP BY Salesperson
ORDER BY conversion_rate_percent DESC;
