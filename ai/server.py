import grpc
from concurrent import futures
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import kalorianaliz_pb2
import kalorianaliz_pb2_grpc
from src.nlu import parse_text
from src.calorie_bridge import calculate_calories
from src.fusion import fuse_results
from src.vision import VisionEngine  

vision_engine = VisionEngine()

class CalorieService(kalorianaliz_pb2_grpc.CalorieServiceServicer):
    def Predict(self, request, context):
        print(f"\n Yeni İstek Geldi. Kullanıcı ID: {request.user_id}")
        
        nlu_data = None
        if request.text_input:
            print(f" Gelen Metin: '{request.text_input}'")
            nlu_data = parse_text(request.text_input)
            
        vision_data = None
        if request.image_data and len(request.image_data) > 0:
            print(" Fotoğraf alındı yapay zeka analiz ediyor...")
            vision_data = vision_engine.predict(request.image_data)
            if vision_data:
                print(f" Göz Motoru Tahmini: {vision_data['food']} (Güven: %{vision_data['confidence']*100:.2f})")
            
        fusion_result = fuse_results(vision_data, nlu_data)
        print(f" Füzyon Kararı: {fusion_result.get('food')} ({fusion_result.get('quantity')} {fusion_result.get('unit')})")
        
        calorie_result = calculate_calories(fusion_result)
        hesaplanan_kalori = calorie_result.get("calculated_calories")
        print(f" Hesaplanan Kalori: {hesaplanan_kalori} kcal")
        
        return kalorianaliz_pb2.PredictResponse(
            food_name=fusion_result.get("food") or "Bilinmiyor",
            confidence=fusion_result.get("confidence", 0.0),
            calories=hesaplanan_kalori if hesaplanan_kalori is not None else 0.0,
            gradcam_b64="base64_heatmap_string_placeholder",
            low_confidence=fusion_result.get("confidence", 1.0) < 0.70,
            source=fusion_result.get("source", "unknown")
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kalorianaliz_pb2_grpc.add_CalorieServiceServicer_to_server(CalorieService(), server)
    server.add_insecure_port('[::]:50051')
    print(" Python gRPC Yapay Zeka Sunucusu GERÇEK MOTORLA başlatıldı!")
    print(" C# Backend'den gelecek istekler bekleniyor...\n" + "-"*50)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()