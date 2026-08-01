import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
PUBLIC_DIR.mkdir(exist_ok=True)

def read_file_safe(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

# Load files to bundle into stlite
files = {}

# 1. Main Streamlit App
streamlit_app_code = read_file_safe(BASE_DIR / "web" / "streamlit_app.py")
files["web/streamlit_app.py"] = streamlit_app_code

# 2. CSS Stylesheet
css_code = read_file_safe(BASE_DIR / "web" / "static" / "css" / "style.css")
files["web/static/css/style.css"] = css_code

# 3. App Python modules
app_dir = BASE_DIR / "app"
for root, dirs, filenames in os.walk(app_dir):
    if "__pycache__" in root:
        continue
    for fname in filenames:
        if fname.endswith(".py"):
            full_p = Path(root) / fname
            rel_p = str(full_p.relative_to(BASE_DIR)).replace("\\", "/")
            files[rel_p] = read_file_safe(full_p)

# 4. Data Ontologies
ontologies_dir = BASE_DIR / "data" / "ontologies"
for fname in os.listdir(ontologies_dir):
    if fname.endswith(".json"):
        full_p = ontologies_dir / fname
        rel_p = f"data/ontologies/{fname}"
        files[rel_p] = read_file_safe(full_p)

# 5. Data Sample Resumes
samples_dir = BASE_DIR / "data" / "sample_resumes"
for fname in os.listdir(samples_dir):
    if fname.endswith(".txt"):
        full_p = samples_dir / fname
        rel_p = f"data/sample_resumes/{fname}"
        files[rel_p] = read_file_safe(full_p)

# Generate HTML file with embedded Stlite runner
html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Resume Scanner & ATS Predictor</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.58.0/build/stlite.css"
    />
    <style>
      body {{
        margin: 0;
        padding: 0;
        background-color: #FFFFFF;
      }}
      #root {{
        height: 100vh;
      }}
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.58.0/build/stlite.js"></script>
    <script>
      stlite.mount(
        {{
          requirements: ["numpy", "pypdf", "python-docx"],
          entrypoint: "web/streamlit_app.py",
          files: {json.dumps(files, indent=2)}
        }},
        document.getElementById("root")
      );
    </script>
  </body>
</html>
"""

with open(PUBLIC_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Build complete! Bundled {len(files)} files into public/index.html")
