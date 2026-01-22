from pathlib import Path
import os
import json

from flask import (
    Flask,
    render_template_string,
    request,
    jsonify,
    redirect,
    url_for,
    session,
)

from ocr_pdf_extract import ocr_pdf
from field_extractor import extract_insurance_fields

app = Flask(__name__)
app.secret_key = "motor-insurance-ocr-secret"


INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Motor Insurance OCR</title>

<style>
/* ===== ANIMATIONS ===== */

/* Fade + slide animation */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Orange glow pulse */
@keyframes glowPulse {
  0% {
    text-shadow: 0 0 0 rgba(255,140,40,0);
  }
  50% {
    text-shadow: 0 0 18px rgba(255,140,40,0.45);
  }
  100% {
    text-shadow: 0 0 0 rgba(255,140,40,0);
  }
}

/* Floating card */
@keyframes floatSlow {
  0% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0); }
}

/* ===== APPLY ===== */

/* Top heading */
.header h1 {
  animation: fadeUp 0.9s ease-out forwards, glowPulse 3.5s ease-in-out infinite;
}

/* Subtitle */
.header p {
  animation: fadeUp 1.2s ease-out forwards;
  opacity: 0;
}

/* Upload card */
.upload-section {
  animation: fadeUp 1.1s ease-out forwards, floatSlow 6s ease-in-out infinite;
}

/* Buttons */
.submit-btn,
.file-btn {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.submit-btn:hover,
.file-btn:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 0 18px rgba(255,140,40,0.55);
}

/* Results animation */
.results {
  animation: fadeUp 0.8s ease-out forwards;
}

:root {
  --bg-dark: #0b0b0e;
  --bg-card: rgba(18,18,22,0.78);
  --orange: #f97316;
  --orange-soft: #fb923c;
  --orange-glow: rgba(249,115,22,0.45);
  --text-main: #f8fafc;
  --text-muted: #9ca3af;
  --border: rgba(255,255,255,0.08);
  --success: #22c55e;
  --error: #ef4444;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  min-height: 100vh;
  padding: 32px 16px;
  background:
    radial-gradient(circle at 15% 20%, rgba(249,115,22,0.35), transparent 45%),
    radial-gradient(circle at 85% 10%, rgba(251,146,60,0.25), transparent 40%),
    linear-gradient(180deg, #0b0b0e, #050507);
  color: var(--text-main);
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 36px;
}

.header h1 {
  font-size: 2.4rem;
  font-weight: 900;
  background: linear-gradient(135deg, #f97316, #fb923c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header p {
  color: var(--text-muted);
  margin-top: 6px;
}

.card {
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  border-radius: 18px;
  border: 1px solid var(--border);
  padding: 28px;
  margin-bottom: 28px;
  box-shadow: 0 30px 80px rgba(0,0,0,0.65);
}

.upload-box {
  text-align: center;
  background-image:
    linear-gradient(rgba(249,115,22,0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(249,115,22,0.15) 1px, transparent 1px);
  background-size: 26px 26px;
  border-radius: 16px;
  padding: 44px 22px;
}

.upload-box h2 {
  font-size: 1.4rem;
  margin-bottom: 20px;
}

input[type="file"] {
  display: none;
}

.file-btn {
  display: inline-block;
  padding: 14px 28px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--orange), var(--orange-soft));
  color: #09090b;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 12px 35px var(--orange-glow);
}

.file-name {
  margin-top: 14px;
  color: var(--text-muted);
}

.submit-btn {
  margin-top: 26px;
  padding: 14px 36px;
  border-radius: 12px;
  background: #09090b;
  color: var(--orange-soft);
  border: 1px solid var(--border);
  font-weight: 800;
  cursor: pointer;
}

.loading {
  display: none;
  margin-top: 22px;
  color: var(--text-muted);
}

.loading.active {
  display: block;
}

.success {
  margin-top: 20px;
  background: rgba(34,197,94,0.12);
  border: 1px solid rgba(34,197,94,0.3);
  padding: 14px;
  border-radius: 12px;
  color: var(--success);
}

.error {
  margin-top: 20px;
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.3);
  padding: 14px;
  border-radius: 12px;
  color: var(--error);
}

.stats {
  display: flex;
  gap: 16px;
  margin-bottom: 26px;
}

.stat {
  flex: 1;
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  padding: 18px;
  text-align: center;
  border: 1px solid var(--border);
}

.stat .value {
  font-size: 1.7rem;
  font-weight: 900;
  color: var(--orange-soft);
}

.stat .label {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 6px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.fields {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}

.field {
  background: rgba(255,255,255,0.03);
  border-radius: 14px;
  padding: 14px;
  border: 1px solid var(--border);
}

.field .key {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--text-muted);
}

.field .value.empty {
  color: #6b7280;
  font-style: italic;
}

.toggle-json {
  margin-top: 20px;
  background: none;
  border: none;
  font-weight: 800;
  cursor: pointer;
  color: var(--orange-soft);
}

.json-box {
  display: none;
  margin-top: 16px;
  background: #020617;
  padding: 18px;
  border-radius: 14px;
  font-family: monospace;
  font-size: 0.85rem;
  border: 1px solid var(--border);
}

.json-box.active {
  display: block;
}
</style>
</head>

<body>
<div class="container">

<div class="header">
<h1>🏍️ Motor Insurance OCR</h1>
<p>Extract structured data from insurance policy PDFs</p>
</div>

<div class="card upload-box">
<h2>Upload Policy PDF</h2>

<form method="post" enctype="multipart/form-data" id="uploadForm">
  <input type="hidden" name="fresh_submit" value="1">
<label class="file-btn">
Choose PDF
<input type="file" name="file" id="file" accept="application/pdf" required />
</label>

<div class="file-name" id="fileName"></div>
<button class="submit-btn" id="submitBtn">Extract Data</button>
</form>

<div class="loading" id="loading">Processing PDF, please wait…</div>

{% if error %}<div class="error">{{ error }}</div>{% endif %}
{% if success %}<div class="success">{{ success }}</div>{% endif %}
</div>

{% if extracted_data %}
<div class="card results">
  <h2>Extracted Results</h2>

  <div class="stats">
    <div class="stat">
      <div class="label">Total Fields</div>
      <div class="value">{{ field_count }}</div>
    </div>

    <div class="stat">
      <div class="label">Fields Extracted</div>
      <div class="value">{{ filled_count }}</div>
    </div>

    <div class="stat">
      <div class="label">Completion Rate</div>
      <div class="value">{{ completion_rate }}%</div>
    </div>
  </div>

<div class="fields">
{% for key, value in extracted_data.items() %}
<div class="field">
<div class="key">{{ key }}</div>
<div class="value {% if not value %}empty{% endif %}">
{{ value if value else "Not found" }}
</div>
</div>
{% endfor %}
</div>

<button class="toggle-json" onclick="toggleJson()">Toggle JSON</button>
<div class="json-box" id="jsonBox"><pre>{{ json_data }}</pre></div>
</div>
{% endif %}

</div>

<!-- Reload Warning Modal -->
<div id="reloadModal" style="
  display:none;
  position:fixed;
  inset:0;
  background:rgba(0,0,0,0.65);
  backdrop-filter: blur(6px);
  z-index:9999;
  align-items:center;
  justify-content:center;
">
  <div style="
    background:#0b0b0e;
    border:1px solid rgba(255,255,255,0.1);
    border-radius:16px;
    padding:28px;
    width:90%;
    max-width:420px;
    box-shadow:0 40px 80px rgba(0,0,0,0.8);
    text-align:center;
  ">
    <h3 style="color:#fb923c;margin-bottom:12px;">
      Reload Warning
    </h3>

    <p style="color:#9ca3af;font-size:0.95rem;line-height:1.4;">
      Reloading will clear extracted results and return you to the home page.
    </p>

    <div style="margin-top:22px;display:flex;gap:12px;justify-content:center;">
      <button onclick="closeReloadModal()" style="
        padding:10px 18px;
        border-radius:10px;
        background:#09090b;
        color:#fb923c;
        border:1px solid rgba(255,255,255,0.15);
        font-weight:700;
        cursor:pointer;
      ">
        Cancel
      </button>

      <button onclick="confirmReload()" style="
        padding:10px 18px;
        border-radius:10px;
        background:linear-gradient(135deg,#f97316,#fb923c);
        color:#09090b;
        border:none;
        font-weight:800;
        cursor:pointer;
      ">
        Continue
      </button>
    </div>
  </div>
</div>

<script>
/* File name preview */
document.getElementById("file")?.addEventListener("change", e => {
  document.getElementById("fileName").textContent =
    e.target.files[0] ? e.target.files[0].name : "";
});

/* Submit loading state */
document.getElementById("uploadForm")?.addEventListener("submit", () => {
  document.getElementById("loading").classList.add("active");
  document.getElementById("submitBtn").disabled = true;
});

/* Toggle JSON */
function toggleJson() {
  document.getElementById("jsonBox").classList.toggle("active");
}

/* 🔹 Mark USER PAGE when results exist */
if (document.querySelector(".results")) {
  sessionStorage.setItem("onUserPage", "1");
}

/* 🔹 Detect RELOAD on USER PAGE */
window.addEventListener("load", () => {
  const isUserPage = sessionStorage.getItem("onUserPage") === "1";
  const isReload = performance.navigation.type === 1; // reload

  if (isReload && isUserPage) {
    const modal = document.getElementById("reloadModal");
    if (modal) modal.style.display = "flex";
  }
});

/* Modal actions */
function closeReloadModal() {
  document.getElementById("reloadModal").style.display = "none";
}

function confirmReload() {
  sessionStorage.removeItem("onUserPage");
  window.location.href = "/";
}
</script>


</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():

    # 🔹 CASE 1: Browser reload → POST resubmission (no fresh_submit)
    if request.method == "POST" and "fresh_submit" not in request.form:
        # Clear any previous session data and go to HOME page
        session.clear()
        return redirect(url_for("index"))

    # 🔹 CASE 2: Normal user PDF submission
    if request.method == "POST":
        uploaded = request.files.get("file")

        if not uploaded or uploaded.filename == "":
            session["error"] = "Please choose a PDF file."
            return redirect(url_for("index"))

        uploads_dir = Path("/tmp/uploads") if os.environ.get("VERCEL_ENV") else Path("uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        save_path = uploads_dir / Path(uploaded.filename).name

        try:
            uploaded.save(save_path)
            text = ocr_pdf(save_path)
            extracted_data = extract_insurance_fields(text)

            session["extracted_data"] = extracted_data
            session["json_data"] = json.dumps(extracted_data, indent=2)
            session["field_count"] = len(extracted_data)
            session["filled_count"] = sum(
                1 for v in extracted_data.values() if v and v.strip()
            )
            session["completion_rate"] = round(
                (session["filled_count"] / session["field_count"]) * 100, 1
            ) if session["field_count"] else 0

            session["success"] = (
            f"PDF processed successfully. "
            f"Found {session['filled_count']} out of {session['field_count']} fields."
)
            save_path.unlink(missing_ok=True)

        except Exception as e:
            session["error"] = str(e)

        return redirect(url_for("index"))

    # 🔹 CASE 3: Normal GET (HOME or redirected after POST)
    extracted_data = session.pop("extracted_data", None)
    json_data = session.pop("json_data", "")
    field_count = session.pop("field_count", 0)
    filled_count = session.pop("filled_count", 0)
    completion_rate = session.pop("completion_rate", 0)
    success = session.pop("success", "")
    error = session.pop("error", "")

    return render_template_string(
        INDEX_HTML,
        error=error,
        success=success,
        extracted_data=extracted_data,
        json_data=json_data,
        field_count=field_count,
        filled_count=filled_count,
        completion_rate=completion_rate,
    )

app.route("/api/extract", methods=["POST"])
def api_extract():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    uploaded = request.files["file"]
    uploads_dir = Path("/tmp/uploads") if os.environ.get("VERCEL_ENV") else Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    save_path = uploads_dir / Path(uploaded.filename).name

    uploaded.save(save_path)
    text = ocr_pdf(save_path)
    data = extract_insurance_fields(text)
    save_path.unlink(missing_ok=True)

    return jsonify(data)


if __name__ == "__main__":
    print("Starting Flask server…")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

