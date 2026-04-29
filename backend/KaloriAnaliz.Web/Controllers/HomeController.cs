using Microsoft.AspNetCore.Mvc;
using KaloriAnaliz.Grpc;
using System.IO;
using System.Threading.Tasks;

namespace KaloriAnaliz.Web.Controllers
{
    public class HomeController : Controller
    {
        private readonly KaloriGrpcClient _grpcClient;

        public HomeController(KaloriGrpcClient grpcClient)
        {
            _grpcClient = grpcClient;
        }

        [HttpGet]
        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> Analyze(IFormFile imageFile, string textInput)
        {
            byte[] imageBytes = null;

            if (imageFile != null && imageFile.Length > 0)
            {
                using (var ms = new MemoryStream())
                {
                    await imageFile.CopyToAsync(ms);
                    imageBytes = ms.ToArray();
                }
            }

            var response = await _grpcClient.AnalyzeCalorieAsync(imageBytes, textInput);

            return View("Index", response);
        }
    }
}