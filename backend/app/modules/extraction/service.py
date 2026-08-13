"""
Module 5 -- Attribute Extraction (the core AI module).

Uses , matching the architecture you specified. This is the ONLY
module in the whole pipeline that calls an LLM -- everything else is
deterministic. Keep it that way; don't let AI creep into modules that
don't need it.

Requires _API_KEY to be set in the environment.

Every extracted attribute MUST include:
  - "evidence": the exact substring of the source text that justifies it,
    or null if the model is inferring rather than reading it directly.
  - "inferred": true/false.
This is what makes the downstream Confidence Engine (Module 7) real
instead of decorative -- confidence is computed FROM this evidence field,
never invented by asking the model "how sure are you."
"""
import os
import json

from dotenv import load_dotenv

load_dotenv()

SYSTEM_INSTRUCTIONS = """You are a product attribute extraction engine for an appliance distributor catalog.

Given a short, cryptic raw product  description, extract structured attributes.

STRICT RULES:
- Output ONLY valid JSON, no markdown fences, no prose.
- Every attribute MUST include "evidence": the exact substring of the input that justifies it, or null if inferred.
- Every attribute MUST include "inferred": true if you could not point to direct evidence, false otherwise.
- Do NOT invent specifications you cannot support. Prefer leaving a field out over guessing.
- Only include attributes that plausibly apply to this specific product type.

Return JSON matching this schema:
{
  "manufacturer_name": string,
  "brand_name": string,
  "attributes": [
    {"label": string, "value": string, "uom": string, "evidence": string|null, "inferred": boolean}
  ]
}
"""

try:
    import google.generativeai as genai  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - handled at runtime when the SDK is unavailable
    genai = None


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in environment.")
    return api_key


def _call_(part_desc: str, mfg_part_num: str) -> dict:
    if genai is None:
        raise RuntimeError(
            "The 'google-generativeai' package is not installed. Install it with: pip install google-generativeai"
        )

    api_key = _get_api_key()
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "models/gemini-flash-latest")
    model = genai.GenerativeModel(
        model_name,
        system_instruction=SYSTEM_INSTRUCTIONS,
    )
    prompt = f"Mfg_Part_Num: {mfg_part_num}\nPart_Desc: {part_desc}\n\nReturn ONLY the JSON object."
    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def extract_attributes(rows: list[dict]) -> list[dict]:
    have_key = bool(_get_api_key() if (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) else False)
    for r in rows:
        if not have_key:
            # Fail gracefully so the rest of the pipeline is still runnable
            # and demoable before the API key is wired in.
            r["manufacturer_name"] = ""
            r["brand_name"] = ""
            r["extracted_attributes"] = []
            r.setdefault("flags", []).append("extraction_skipped_no_api_key")
            continue
        try:
            result = _call_(r.get("part_desc_normalized") or r["part_desc"], r["mfg_part_num"])
            r["manufacturer_name"] = result.get("manufacturer_name", "")
            r["brand_name"] = result.get("brand_name", "")
            r["extracted_attributes"] = result.get("attributes", [])
        except Exception as e:
            r["extracted_attributes"] = []
            r.setdefault("flags", []).append(f"extraction_error: {e}")
    return rows
