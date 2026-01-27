import logging

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.api.schema import TTSErrorResponse, TTSResponse
from app.tts.qwen3 import Qwen3TTSProvider
from app.utils import encode_audio_base64

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


def _get_tts_provider(request: Request) -> Qwen3TTSProvider:
    return request.app.state.tts_provider  # type: ignore[no-any-return]


async def _validate_audio_file(audio_file: UploadFile) -> bytes:
    filename = audio_file.filename or ""
    if not filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="対応している音声形式はWAVのみです",
        )

    content = await audio_file.read()

    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルサイズが上限（10MB）を超えています",
        )

    return content


@router.post(
    "/voice-clone",
    response_model=TTSResponse,
    responses={
        400: {"model": TTSErrorResponse, "description": "不正なリクエスト"},
        500: {"model": TTSErrorResponse, "description": "内部サーバーエラー"},
    },
    summary="Voice Cloneによる音声合成",
    description="アップロードされた参照音声を使用して音声合成を行います。",
)
async def synthesize_voice_clone(
    request: Request,
    audio_file: UploadFile = File(..., description="参照音声ファイル（WAV形式）"),
    input: str = Form(..., description="合成するテキスト"),
    ref_text: str = Form(..., description="参照音声のテキスト書き起こし"),
    speed: float = Form(default=1.0, description="再生速度"),
) -> TTSResponse:
    try:
        tts_provider = _get_tts_provider(request)
        audio_bytes = await _validate_audio_file(audio_file)
        audio_data = await tts_provider.synthesize_with_reference(
            text=input,
            ref_audio_bytes=audio_bytes,
            ref_text=ref_text,
            speed=speed,
        )
        encoded_audio = encode_audio_base64(audio_data)

        return TTSResponse(audio_data=encoded_audio)
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"不正なリクエストパラメータ: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Voice Clone合成中にエラーが発生しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice Clone合成中にエラーが発生しました: {str(e)}",
        )
