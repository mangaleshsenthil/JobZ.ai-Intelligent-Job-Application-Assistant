import google.generativeai as genai
from config.settings import GEMINI_API_KEY, MODEL_NAME

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(MODEL_NAME)

def generate_response(prompt: str, is_json: bool = False):
    config = {
        "temperature": 0.3,
        "top_p": 1,
        "max_output_tokens": 8192
    }
    if is_json:
        config["response_mime_type"] = "application/json"
        
    try:
        response = model.generate_content(prompt, generation_config=config)
        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "resource_exhausted" in error_msg:
            print("Gemini API Quota Exceeded. Please try again later or check your billing/tier.")
            return '{"error": "API Quota Exceeded. Please wait a few seconds/minutes."}' if is_json else "API Quota Exceeded. Please try again later."
        raise e
