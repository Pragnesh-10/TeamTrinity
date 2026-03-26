const API_URL = "http://localhost:8000/api";

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function triggerDemo() {
  const res = await fetch(`${API_URL}/demo`, { method: "POST" });
  return res.json();
}

export async function getStatus(jobId) {
  const res = await fetch(`${API_URL}/status/${jobId}`);
  return res.json();
}

export async function getResult(jobId) {
  const res = await fetch(`${API_URL}/result/${jobId}`);
  return res.json();
}
