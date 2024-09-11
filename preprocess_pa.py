import pandas as pd

source_file_path = 'pa.csv'
output_file_path = 'pa_preprocessed.csv'

# Read the original CSV file
df = pd.read_csv(source_file_path)

# Create a new DataFrame with the desired columns
new_df = pd.DataFrame()

# Map the existing columns to the new columns
new_df['id'] = df['ID']
new_df['first_name'] = df['First name']
new_df['middle_name'] = df['Middle name']
new_df['last_name'] = df['Last name']
new_df['email'] = df['email1']  # Assuming you want to copy 'email1' to 'email'
new_df['email1'] = df['email1']
new_df['email2'] = df.get('email2', '')  # Assuming email2, email3, email4 columns exist or fill with empty
new_df['email3'] = df.get('email3', '')
new_df['email4'] = df.get('email4', '')
new_df['phone_number'] = df['phone_number']
new_df['mobile_number'] = df['mobile_number']
new_df['primary_address1'] = df['Number'].astype(str) + ' ' + df['Street']
new_df['primary_address2'] = df.get('nb_address1', '')
new_df['primary_address3'] = ''  # Add if you have a corresponding column or fill with empty
new_df['primary_city'] = df['City']
new_df['primary_county'] = df.get('Region', '')
new_df['primary_state'] = df['State']
new_df['primary_zip'] = df['Postal code']
new_df['primary_country_code'] = df['Ctry ISO']
new_df['sex'] = ''  # Add if you have a corresponding column or fill with empty
new_df['born_at'] = df['DOB']

new_df.to_csv(output_file_path, index=False)

print(f'New CSV file created at {output_file_path}')
