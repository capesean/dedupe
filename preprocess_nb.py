import pandas as pd

source_file_path = 'nb_sample.csv'
output_file_path = 'nb_preprocessed.csv'

# Read the original CSV file
df = pd.read_csv(source_file_path)

# Create a new DataFrame with the desired columns
new_df = pd.DataFrame()

# Map the existing columns to the new columns
new_df['id'] = df['nationbuilder_id']  # Assuming 'id' refers to 'nationbuilder_id'
new_df['first_name'] = df['first_name']
new_df['middle_name'] = df['middle_name']
new_df['last_name'] = df['last_name']
new_df['email'] = df['email']
new_df['email1'] = df['email1']
new_df['email2'] = df['email2']
new_df['email3'] = df['email3']
new_df['email4'] = df['email4']
new_df['phone_number'] = df['phone_number']
new_df['mobile_number'] = df['mobile_number']
new_df['primary_address1'] = df['primary_address1']
new_df['primary_address2'] = df['primary_address2']
new_df['primary_address3'] = df['primary_address3']
new_df['primary_city'] = df['primary_city']
new_df['primary_county'] = df['primary_county']
new_df['primary_state'] = df['primary_state']
new_df['primary_zip'] = df['primary_zip']
new_df['primary_country_code'] = df['primary_country_code']
new_df['sex'] = df['sex']
new_df['born_at'] = df['born_at']

new_df.to_csv(output_file_path, index=False)

print(f'New CSV file created at {output_file_path}')
