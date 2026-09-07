"""
Environment Verification Diagnostic Script for Fact Knowledge Layer (EVIDRA)
Runs all D0 prerequisite checks deterministically.
"""
import sys
import json
import urllib.request
import os

def check_python_version():
    print("[1/5] Checking Python Version...")
    v = sys.version_info
    print(f"      Python {v.major}.{v.minor}.{v.micro} detected.")
    if v.major < 3 or (v.major == 3 and v.minor < 11):
        print("      FAIL: Python 3.11+ is required.")
        return False
    print("      PASS: Python version compatible.")
    return True

def check_dependencies():
    print("[2/5] Checking Core Dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "fitz",
        "pdfplumber",
        "langgraph",
        "langchain_core",
        "langchain_ollama",
        "sentence_transformers",
        "dateutil"
    ]
    missing = []
    for mod in required:
        try:
            __import__(mod)
            print(f"      Loaded module: {mod}")
        except ImportError as e:
            missing.append(mod)
            print(f"      FAIL: Missing module {mod}: {e}")
    if missing:
        return False
    print("      PASS: All core dependencies installed.")
    return True

def check_ollama_connection():
    print("[3/5] Checking Ollama Runtime Connection...")
    url = "http://127.0.0.1:11434/api/version"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"      Connected to Ollama version: {data.get('version')}")
            print("      PASS: Ollama daemon active.")
            return True
    except Exception as e:
        print(f"      FAIL: Could not connect to Ollama at {url}: {e}")
        return False

def check_ollama_model():
    print("[4/5] Checking Local LLM Model & Structured Generation...")
    url = "http://127.0.0.1:11434/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m["name"] for m in data.get("models", [])]
            print(f"      Available models: {models}")
            if not models:
                print("      FAIL: No models found in Ollama.")
                return False
            model_to_use = models[0]
            print(f"      Testing structured output with: {model_to_use}")
            
            gen_url = "http://127.0.0.1:11434/api/generate"
            body = json.dumps({
                "model": model_to_use,
                "prompt": "Return JSON with keys: entity (string) and test (string, value OK)",
                "stream": False,
                "format": "json"
            }).encode("utf-8")
            req = urllib.request.Request(gen_url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as g_resp:
                res = json.loads(g_resp.read().decode("utf-8"))
                parsed = json.loads(res.get("response", "{}"))
                print(f"      Model structured response: {parsed}")
                print("      PASS: LLM structured inference operational.")
                return True
    except Exception as e:
        print(f"      FAIL: Model check failed: {e}")
        return False

def check_embeddings():
    print("[5/5] Checking SentenceTransformer Embedding Cache...")
    try:
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        vec = model.encode("Operational revenue grew by 12 percent.")
        print(f"      Generated vector dimension: {len(vec)}")
        print("      PASS: BAAI/bge-small-en-v1.5 cached and operational.")
        return True
    except Exception as e:
        print(f"      FAIL: Embedding load failed: {e}")
        return False

def main():
    print("==================================================")
    print("  EVIDRA - Fact Knowledge Layer D0 Verification   ")
    print("==================================================")
    checks = [
        check_python_version(),
        check_dependencies(),
        check_ollama_connection(),
        check_ollama_model(),
        check_embeddings()
    ]
    print("==================================================")
    if all(checks):
        print("ALL D0 PREREQUISITE CHECKS PASSED SUCCESSFULLY.")
        sys.exit(0)
    else:
        print("SOME D0 PREREQUISITE CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
