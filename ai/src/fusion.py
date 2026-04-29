def fuse_results(vision_result, nlu_result):
    
    final_result = {
        "food": None,
        "quantity": 1.0,
        "unit": "porsiyon",
        "confidence": 0.0,
        "source": "fusion",
        "warnings": []
    }

    if not vision_result and nlu_result:
        final_result.update(nlu_result)
        final_result["source"] = "nlp_only"
        return final_result

    if vision_result and not nlu_result:
        final_result["food"] = vision_result.get("food")
        final_result["confidence"] = vision_result.get("confidence", 0.0)
        final_result["source"] = "vision_only"
        if final_result["confidence"] < 0.70:
            final_result["warnings"].append("Düşük güven skoru. Farklı açıdan çeker misiniz?")
        return final_result

    final_result["quantity"] = nlu_result.get("quantity", 1.0)
    final_result["unit"] = nlu_result.get("unit", "porsiyon")

    if nlu_result.get("confidence", 0.0) > 0.8:
        final_result["food"] = nlu_result.get("food")
        final_result["confidence"] = nlu_result.get("confidence")
    else:
        final_result["food"] = vision_result.get("food")
        final_result["confidence"] = vision_result.get("confidence")
        final_result["warnings"].append("Metinden yemek adı anlaşılamadı, görsel tahmin kullanıldı.")

    return final_result

if __name__ == "__main__":
    test_vision = {"food": "manti", "confidence": 0.95}
    test_nlu = {"food": None, "quantity": 2.5, "unit": "tabak", "confidence": 0.3}

    print(" Füzyon Motoru Test Ediliyor...")
    print(f"Göz Motoru: {test_vision}")
    print(f"Dil Motoru: {test_nlu}")
    print("-" * 30)
    print(f"Füzyon Kararı: {fuse_results(test_vision, test_nlu)}")