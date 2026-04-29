import spacy
import re

def parse_text(text):
    
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    units = ["tabak", "kase", "dilim", "adet", "porsiyon", "gram", "gr"]
    
    result = {"food": None, "quantity": 1, "unit": "porsiyon", "confidence": 0.0}
    
    sayilar = re.findall(r'\d+', text)
    if sayilar:
        result["quantity"] = float(sayilar[0])
        
    temiz_metin = text.lower()
    for unit in units:
        if unit in temiz_metin:
            result["unit"] = unit
            break
            
    if result["unit"] in temiz_metin:
        temiz_metin = temiz_metin.replace(result["unit"], "")
    for num in sayilar:
        temiz_metin = temiz_metin.replace(num, "")
        
    temiz_metin = temiz_metin.replace("yedim", "").replace("içtim", "").replace("biraz", "").strip()
    
    if temiz_metin:
        result["food"] = temiz_metin
        result["confidence"] = 0.85 
    else:
        result["confidence"] = 0.3 
        
    return result

if __name__ == "__main__":
    test_cumlesi = "2 tabak manti yedim"
    print(f"Test Cümlesi: '{test_cumlesi}'")
    print(f"Çıktı: {parse_text(test_cumlesi)}")