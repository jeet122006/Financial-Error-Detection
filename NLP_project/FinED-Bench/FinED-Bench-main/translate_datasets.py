import json
import os
from pathlib import Path

# Install google-generativeai if not already installed
# pip install google-generativeai

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("google-generativeai package is required. Install it via pip.")

# Set your Gemini API key here or via environment variable GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def translate_text(chinese_text: str) -> str:
    """Translate Chinese text to English using Gemini model."""
    prompt = f"Translate the following Chinese text to fluent English, preserving any formatting or placeholders.\n\nChinese: {chinese_text}\n\nEnglish:" 
    response = model.generate_content(prompt)
    return response.text.strip()

def translate_entry(entry: dict) -> dict:
    translated = {}
    for key, value in entry.items():
        if isinstance(value, str):
            # Translate string fields
            try:
                translated[key] = translate_text(value)
            except Exception as e:
                print(f"Failed to translate field {key}: {e}")
                translated[key] = value
        else:
            # Keep non-string fields as is (e.g., numbers, lists)
            translated[key] = value
    return translated

def translate_file(input_path: Path, output_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        translated_data = [translate_entry(item) for item in data]
    else:
        translated_data = translate_entry(data)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
    print(f"Translated {input_path} -> {output_path}")

if __name__ == "__main__":
    base_dir = Path(__file__).parent / "FinED-Bench-main"
    datasets = [
        (base_dir / "fined_bench" / "eval_data.json", base_dir / "fined_bench" / "eval_data_en.json"),
        (base_dir / "fined_bench" / "eval_data_hard.json", base_dir / "fined_bench" / "eval_data_hard_en.json"),
        (base_dir / "sft_data" / "sft_data_wo_errors.json", base_dir / "sft_data" / "sft_data_wo_errors_en.json"),
        (base_dir / "sft_data" / "sft_data_w_errors.json", base_dir / "sft_data" / "sft_data_w_errors_en.json"),
    ]
    for inp, outp in datasets:
        if inp.exists():
            translate_file(inp, outp)
        else:
            print(f"Input file {inp} not found.")
