import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DATABRICKS_HOST")
token = os.getenv("DATABRICKS_TOKEN")

print(f"Host: {host}")
print(f"Token: {token[:10]}...{token[-4:]}" if token else "No token")

try:
    from databricks.sdk import WorkspaceClient
    client = WorkspaceClient(host=host, token=token)
    
    # Test user connection
    me = client.current_user.me()
    print(f"Connected as: {me.user_name}")
    
    # Try to upload a test file
    test_content = b'{"test": true}'
    volume_path = "/Volumes/main/ps_assistant/data/test.json"
    
    print(f"\nTrying to upload to: {volume_path}")
    try:
        client.files.upload(volume_path, test_content, overwrite=True)
        print("✅ Upload successful!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        
        # Check if volume exists
        print("\nChecking catalogs...")
        try:
            catalogs = list(client.catalogs.list())
            print(f"Catalogs: {[c.name for c in catalogs]}")
        except Exception as e2:
            print(f"Cannot list catalogs: {e2}")
    
except Exception as e:
    print(f"Connection error: {e}")
