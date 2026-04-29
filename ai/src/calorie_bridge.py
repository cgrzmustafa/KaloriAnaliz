import json
import os
import requests

def load_local_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "..", "data", "turkish_foods.json")
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def fetch_from_open_food_facts(food_name):
    search_query = food_name.replace("_", " ")
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={search_query}&search_simple=1&action=process&fields=product_name,nutriments&json=1&page_size=5"
    
    headers = {
        "User-Agent": "ZeroMindAI/1.0 (StudentProject)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f" API Yanıt Kodu: {response.status_code}") 
        
        if response.status_code == 200:
            data = response.json()
            if data.get("products") and len(data["products"]) > 0:
                for product in data["products"]:
                    nutriments = product.get("nutriments", {})
                    calories_100g = nutriments.get("energy-kcal_100g") or nutriments.get("energy-kcal_value") or nutriments.get("energy-kcal")
                    
                    if calories_100g:
                        print(f" API'den '{product.get('product_name', search_query)}' için kalori bulundu: {calories_100g} kcal/100g")
                        return float(calories_100g)
                        
                print(" API ürünleri buldu ama hiçbirinde kalori verisi yok.")
            else:
                print(" API boş liste döndürdü.")
        else:
            print(f" API İsteği Reddetti! Sebep: {response.reason}")
            
    except Exception as e:
        print(f" API Bağlantı Hatası: {e}")
        
    return None

def calculate_calories(nlu_data):
    db = load_local_db()
    food = nlu_data.get("food")
    quantity = nlu_data.get("quantity", 1)
    
    if not food:
        return {"food": None, "calculated_calories": 0.0, "source": "unknown"}

    if food in db:
        food_info = db[food]
        total_grams = quantity * food_info["grams_per_unit"]
        total_calories = (total_grams / 100) * food_info["calories_per_100g"]
        return {
            "food": food,
            "calculated_calories": round(total_calories, 2),
            "source": "local_db"
        }
    
    print(f" '{food}' yerel DB'de bulunamadı. API aranıyor...")
    api_calories_100g = fetch_from_open_food_facts(food)
    
    if api_calories_100g:
        assumed_grams_per_unit = 200 
        total_grams = quantity * assumed_grams_per_unit
        total_calories = (total_grams / 100) * api_calories_100g
        
        return {
            "food": food,
            "calculated_calories": round(total_calories, 2),
            "source": "open_food_facts_api"
        }

    return {
        "food": food,
        "calculated_calories": 0.0,
        "source": "not_found"
    }