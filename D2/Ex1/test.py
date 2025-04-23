import pandas as pd

# Step 1: Read the CSV file
input_file_path = 'input.csv'
data = pd.read_csv(input_file_path)

# Step 2: Process the Data
filtered_data = data[data['value'] > 10]
aggregated_data = filtered_data.groupby('category')['amount'].sum().reset_index()
sorted_data = aggregated_data.sort_values(by='amount', ascending=False).reset_index(drop=True)

# Step 3: Write the output to a new CSV file
output_file_path = 'output.csv'
sorted_data.to_csv(output_file_path, index=False)
