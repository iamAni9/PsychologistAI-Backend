import os

creds_path = os.path.join(os.path.dirname(__file__), "..", "app", "credentials", "service_account.json")

with open(creds_path, "w") as f:
    f.write(os.environ["GOOGLE_CREDENTIALS"])

print("Credentials file created successfully...")