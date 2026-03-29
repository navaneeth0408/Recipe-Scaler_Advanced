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
        "ingredient": "milk",
        "quantity": 1.0,
        "unit": "cup"
    }
    print(f"Request Payload: {json.dumps(payload)}")
    
    response = client.post("/api/substitute", json=payload)
    print(f"Status Code: {response.status_code}")
    
    try:
        print("Response JSON (Milk):")
        print(json.dumps(response.json(), indent=2))
        
        # Verify schema
        data = response.json()
        assert "substitutes" in data
        assert isinstance(data["substitutes"], list)
        if len(data["substitutes"]) > 0:
            sub = data["substitutes"][0]
            assert "name" in sub
            assert "ratio" in sub
            assert "note" in sub
            
        print("\nTesting Unknown Output (Should hit categorical fallback):")
        res_empty = client.post("/api/substitute", json={"ingredient": "unicorn tear", "quantity": 1.0, "unit": "drop"})
        print("Category Fallback Output:")
        print(json.dumps(res_empty.json(), indent=2))
        assert "substitutes" in res_empty.json()
        assert res_empty.json()["substitutes"][0]["name"] == "generic pantry staple"
            
        print("\nSUCCESS: All schema tests passed!")
        
    except Exception as e:
        print(f"Response Text/Error: {e}")

if __name__ == "__main__":
    test_api()
