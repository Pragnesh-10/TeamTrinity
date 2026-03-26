const API_URL = "https://mfxray-backend-xyz.onrender.com";

export async function analyzePortfolio(file, scenario, taxRegime) {
  const formData = new FormData();
  if (file) {
    formData.append("file", file);
  }
  if (scenario) {
    formData.append("scenario", scenario);
  }
  if (taxRegime) {
    formData.append("tax_regime", taxRegime);
  }
  
  const res = await fetch(`${API_URL}/analyze-portfolio`, {
    method: "POST",
    body: formData,
  });
  
  return res.json();
}
