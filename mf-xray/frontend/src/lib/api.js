const API_URL = import.meta.env.VITE_API_URL || "https://teamtrinity.onrender.com";

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

export async function getFirePlan(input) {
  const res = await fetch(`${API_URL}/fire/plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Failed to compute FIRE plan");
  }

  return res.json();
}
