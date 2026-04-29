using Grpc.Net.Client;
using System.Threading.Tasks;

namespace KaloriAnaliz.Grpc
{
    public class KaloriGrpcClient
    {
        private readonly CalorieService.CalorieServiceClient _client;

        public KaloriGrpcClient()
        {
            
            var channel = GrpcChannel.ForAddress("http://localhost:50051");
            _client = new CalorieService.CalorieServiceClient(channel);
        }

        public async Task<PredictResponse> AnalyzeCalorieAsync(byte[] imageBytes, string textInput)
        {
            
            var request = new PredictRequest
            {
                ImageData = imageBytes != null ? Google.Protobuf.ByteString.CopyFrom(imageBytes) : Google.Protobuf.ByteString.Empty,
                TextInput = textInput ?? string.Empty,
                UserId = "csharp_web_user"
            };

            return await _client.PredictAsync(request);
        }
    }
}