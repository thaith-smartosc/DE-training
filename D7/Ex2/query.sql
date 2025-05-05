CREATE OR REPLACE TABLE `kestra-thaith.sales_dataset.sales_partitioned`
PARTITION BY target_close_date AS
SELECT
  Date AS created_date,
  Salesperson,
  `Lead Name`,
  Segment,
  Region,
  `Target Close` AS target_close_date,
  `Forecasted Monthly Revenue`,
  `Opportunity Stage`,
  `Weighted Revenue`,
  `Closed Opportunity`,
  `Active Opportunity`,
  `Latest Status Entry`
FROM `kestra-thaith.sales_dataset.sales`;

-- Filter by Partition Range 
SELECT
  Region,
  COUNT(*) AS total_opportunities,
  SUM(`Weighted Revenue`) AS total_weighted_revenue
FROM `kestra-thaith.sales_dataset.sales_partitioned`
WHERE target_close_date BETWEEN '2011-01-01' AND '2011-06-30'
GROUP BY Region
ORDER BY total_weighted_revenue DESC;

