from fastapi import APIRouter, HTTPException
from app.api.v1 import schemas
from app.services.gemini_client import GeminiClient
from app.utils.logging_conf import get_logger

logger = get_logger("routes")
router = APIRouter(prefix="/api/v1", tags=["v1"])

gemini_client = GeminiClient()

# === Generic text generation ===
@router.post("/generate", response_model=schemas.GenerateResponse)
async def generate_text(req: schemas.GenerateRequest):
    try:
        res_text = await gemini_client.generate_text(req.prompt, req.max_tokens or 256)
        return schemas.GenerateResponse(result=res_text)
    except Exception as e:
        logger.exception("Error calling Gemini")
        raise HTTPException(status_code=500, detail=str(e))

# === English Lesson ===
@router.post("/english/lesson", response_model=schemas.LessonResponse)
async def english_lesson(req: schemas.LessonRequest):
    try:
        prompt = (
            f"Give a short English lesson for beginners about the topic: {req.topic}. "
            "Include: explanation, 2 simple examples, and a short exercise."
        )
        res_text = await gemini_client.generate_text(prompt, req.max_tokens or 300)
        return schemas.LessonResponse(topic=req.topic, lesson=res_text)
    except Exception as e:
        logger.exception("Error generating lesson")
        raise HTTPException(status_code=500, detail=str(e))

# === Paragraph with vocabularies ===
@router.post("/generate-paragraph", response_model=schemas.ParagraphResponse)
async def generate_paragraph(req: schemas.ParagraphRequest):
    try:
        base_prompt = (
            f"Write a {req.length} paragraph in {req.language} "
            f"at {req.level} level with a {req.tone} tone. The paragraph must include these vocabularies: "
            f"{', '.join(req.vocabularies)}."
        )
        if req.prompt:
            final_prompt = f"{base_prompt}\nAdditional instruction: {req.prompt}"
        else:
            final_prompt = base_prompt

        res_text = await gemini_client.generate_text(final_prompt)
        return schemas.ParagraphResponse(result=res_text, status=True)
    except Exception as e:
        logger.exception("Error generating paragraph")
        # Return error response with status
        return schemas.ParagraphResponse(
            result=f"Failed to generate paragraph: {str(e)}", 
            status=False
        )
