const API_URL = import.meta.env.VITE_API_URL || "https://teamtrinity.onrender.com"; // UPDATE this once you host your own backend on Render

function messageFromDetail(detail) {
  if (detail == null) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === "object" && d?.msg ? d.msg : String(d)))
      .join("; ");
  }
  if (typeof detail === "object" && detail.msg) return String(detail.msg);
  try {
    return JSON.stringify(detail);
  } catch {
    return "Request failed";
  }
}

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

  let res;
  try {
    res = await fetch(`${API_URL}/analyze-portfolio`, {
      method: "POST",
      body: formData,
    });
  } catch (err) {
    throw new Error(
      err?.message?.includes("Failed to fetch")
        ? "Cannot reach the API (network, CORS, or server down). Check VITE_API_URL if running the app locally."
        : err?.message || "Network error"
    );
  }

  const text = await res.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error(
        `Server returned non-JSON (${res.status}). The service may be restarting or overloaded.`
      );
    }
  }

  if (!res.ok) {
    const fromDetail = messageFromDetail(data.detail);
    throw new Error(
      fromDetail || data.message || `Request failed (${res.status})`
    );
  }

  return data;
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
