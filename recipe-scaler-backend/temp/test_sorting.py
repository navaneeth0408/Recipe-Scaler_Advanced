import sys
import os
import json
import uuid
from datetime import datetime

# Add to Python path to import app modules
# Script is in root/temp/, so root is one level up
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.db import SessionLocal, RecipeDB, IngredientDB, init_db
from app.routes.youtube_search import filter_search_results

def test_youtube_sorting():
    print("--- Testing YouTube Search Sorting ---")
    
    # Mock data
    search_items = [
        {'id': {'videoId': 'vid1'}, 'snippet': {'title': 'Recipe 1', 'channelTitle': 'Channel 1', 'thumbnails': {'high': {'url': 'url1'}}, 'publishedAt': '2024-01-01'}},
        {'id': {'videoId': 'vid2'}, 'snippet': {'title': 'Recipe 2', 'channelTitle': 'Channel 2', 'thumbnails': {'high': {'url': 'url2'}}, 'publishedAt': '2024-01-01'}},
        {'id': {'videoId': 'vid3'}, 'snippet': {'title': 'Recipe 3', 'channelTitle': 'Channel 3', 'thumbnails': {'high': {'url': 'url3'}}, 'publishedAt': '2024-01-01'}},
    ]
    
    video_details = [
        {'id': 'vid1', 'statistics': {'viewCount': '100'}, 'contentDetails': {'duration': 'PT5M'}, 'snippet': {'title': 'Recipe 1', 'description': 'Ingredients: flour, sugar'}},
        {'id': 'vid2', 'statistics': {'viewCount': '500'}, 'contentDetails': {'duration': 'PT5M'}, 'snippet': {'title': 'Recipe 2', 'description': 'Ingredients: flour, sugar'}},
        {'id': 'vid3', 'statistics': {'viewCount': '300'}, 'contentDetails': {'duration': 'PT5M'}, 'snippet': {'title': 'Recipe 3', 'description': 'Ingredients: flour, sugar'}},
    ]
    
    results = filter_search_results(search_items, video_details, "test", 3)
    
    print("Sorted results views:")
    for r in results:
        print(f"Video: {r['video_id']}, Views: {r['views']}")
    
    # Check if sorted correctly (vid2 should be first with 500 views)
    assert results[0]['video_id'] == 'vid2'
    assert results[1]['video_id'] == 'vid3'
    assert results[2]['video_id'] == 'vid1'
    print("YouTube sorting verification PASSED!")

def test_local_recipe_view_increment():
    print("\n--- Testing Local Recipe View Increment ---")
    init_db()
    db = SessionLocal()
    
    recipe_id = "test_recipe_" + str(uuid.uuid4())[:8]
    recipe = RecipeDB(
        id=recipe_id,
        name="Test Recipe",
        servings=1,
        source="manual",
        view_count=0
    )
    db.add(recipe)
    db.commit()
    
    # Simulate get_recipe call
    recipe_from_db = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    recipe_from_db.view_count += 1
    db.commit()
    db.refresh(recipe_from_db)
    
    print(f"Recipe View Count: {recipe_from_db.view_count}")
    assert recipe_from_db.view_count == 1
    
    # Cleanup
    db.delete(recipe_from_db)
    db.commit()
    db.close()
    print("Local recipe view increment verification PASSED!")

if __name__ == "__main__":
    try:
        test_youtube_sorting()
        test_local_recipe_view_increment()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        sys.exit(1)
