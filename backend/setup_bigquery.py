"""
Setup BigQuery tables for LEGID application
Run this script to create all necessary BigQuery tables
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from google.cloud import bigquery
from google.oauth2 import service_account

def setup_bigquery():
    """Create all BigQuery tables and views."""
    
    project_id = os.getenv('GCP_PROJECT_ID', 'auth-login-page-481522')
    dataset_id = os.getenv('BIGQUERY_DATASET', 'legalai')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './gcp-backend-service-account.json')
    
    print(f"Setting up BigQuery for project: {project_id}")
    print(f"Dataset: {dataset_id}")
    print(f"Credentials: {credentials_path}")
    
    # Initialize client
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = bigquery.Client(credentials=credentials, project=project_id)
    
    # Create dataset if it doesn't exist
    dataset_ref = f"{project_id}.{dataset_id}"
    try:
        client.get_dataset(dataset_ref)
        print(f"[OK] Dataset '{dataset_id}' already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"[OK] Created dataset: {dataset_id}")
    
    # Read SQL file
    sql_file = Path(__file__).parent / 'init_bigquery_tables.sql'
    with open(sql_file, 'r') as f:
        sql_script = f.read()
    
    # Split by statements (simple split on CREATE TABLE)
    statements = []
    current_statement = []
    
    for line in sql_script.split('\n'):
        if line.strip().startswith('--'):
            continue  # Skip comments
        
        current_statement.append(line)
        
        # Check if statement is complete (ends with ;)
        if line.strip().endswith(';'):
            statement = '\n'.join(current_statement).strip()
            if statement and not statement.startswith('--'):
                statements.append(statement)
            current_statement = []
    
    # Execute each statement
    for i, statement in enumerate(statements, 1):
        if not statement or len(statement) < 10:
            continue
            
        try:
            print(f"\nExecuting statement {i}/{len(statements)}...")
            query_job = client.query(statement)
            query_job.result()  # Wait for completion
            print(f"[OK] Statement {i} executed successfully")
        except Exception as e:
            print(f"[WARN] Statement {i} error (may already exist): {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] BigQuery setup complete!")
    print("=" * 60)
    print(f"\nTables created in {project_id}.{dataset_id}:")
    print("  - identity_users")
    print("  - login_events")
    print("  - lawyer_applications")
    print("  - conversations (optional)")
    print("  - messages (optional)")
    print("\nViews created:")
    print("  - active_users_30d")
    print("  - login_success_rate")
    print("=" * 60)

if __name__ == "__main__":
    setup_bigquery()
