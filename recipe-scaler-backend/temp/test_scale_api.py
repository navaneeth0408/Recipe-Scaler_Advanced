import sys
import os
import json
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_api():
    payload = {
      "ingredients": [{"name": "flour", "quantity": 1.0, "unit": "cup"}],
      "value": 2,
      "type": "servings"
    }
    
    response = client.post("/api/scale", json=payload)
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
        assert data["scale_factor"] == 2.0
        assert data["ingredients"][0]["quantity"] == 2.0
        print("SUCCESS! UI payload handled dynamically.")
    except Exception as e:
        print(f"Response Text/Error: {response.text}")

if __name__ == "__main__":
    test_api()
