import csv
import requests
import re
import time

# Email validation regex pattern
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# Path to the output CSV file
csv_file_path = 'output/credentials_output.csv'

# Function to check if email is compromised
def check_email_leak(email):
    url = f"https://leakcheck.io/api/public?check={email}&type=email"
    try:
        response = requests.get(url)

        # Check for 200 status code
        if response.status_code == 200:
            try:
                data = response.json()
                # Print the response data for each email
                print("="*50)
                print(f"Response for {email}:")
                print(data)
                print("="*50)
            except ValueError:
                print(f"Error: Invalid JSON response for {email}. Response: {response.text}")
        elif response.status_code == 429:
            # Rate limit exceeded
            retry_after = response.headers.get('Retry-After', 60)  # Default to 60 seconds
            print(f"Rate limit exceeded for {email}. Retrying after {retry_after} seconds.")
            time.sleep(int(retry_after))  # Wait for the specified time before retrying
            check_email_leak(email)  # Retry the request
        else:
            print(f"Error: Non-200 status code for {email}: {response.status_code}")

    except Exception as e:
        print(f"Error checking {email}: {e}")

# Read the CSV file
with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)

    # Skip the header if there is one
    header = next(reader, None)

    # Loop through each row and extract the email (assuming email is in the first column)
    for row in reader:
        if row:  # Skip empty rows
            email = row[0].strip()  # Assuming email is in the first column (adjust if needed)

            # Check if the email is valid using regex
            if re.match(email_regex, email):
                # If valid email, check if it has been compromised
                check_email_leak(email)
            else:
                print(f"Skipping invalid email: {email}")
