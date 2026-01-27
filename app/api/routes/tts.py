import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.api.schema import TTSErrorResponse, TTSResponse
from app.tts.qwen3 import Qwen3TTSProvider
from app.utils import encode_audio_base64

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".wav", ".mp3"}

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


def _get_tts_provider(request: Request) -> Qwen3TTSProvider:
    return request.app.state.tts_provider  # type: ignore[no-any-return]


async def _validate_audio_file(audio_file: UploadFile) -> tuple[bytes, str]:
    """音声ファイルを検証し、内容と拡張子を返す。

    Args:
        audio_file: アップロードされた音声ファイル

    Returns:
        tuple[bytes, str]: (ファイル内容, 拡張子)

    Raises:
        HTTPException: ファイル形式が不正またはサイズ超過の場合
    """
    filename = audio_file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"対応している音声形式は{', '.join(sorted(ALLOWED_EXTENSIONS))}です",
        )

    content = await audio_file.read()

    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルサイズが上限（10MB）を超えています",
        )

    return content, ext


@router.post(
    "/voice-clone",
    response_model=TTSResponse,
    responses={
        400: {"model": TTSErrorResponse, "description": "不正なリクエスト"},
        500: {"model": TTSErrorResponse, "description": "内部サーバーエラー"},
    },
    summary="Voice Cloneによる音声合成",
    description="参照音声を使用して音声合成を行います。対応形式: WAV, MP3",
)
async def synthesize_voice_clone(
    request: Request,
    audio_file: UploadFile = File(..., description="参照音声ファイル（WAV/MP3形式）"),
    input: str = Form(..., description="合成するテキスト"),
    ref_text: str = Form(..., description="参照音声のテキスト書き起こし"),
    speed: float = Form(default=1.0, description="再生速度"),
) -> TTSResponse:
    try:
        tts_provider = _get_tts_provider(request)
        audio_bytes, audio_ext = await _validate_audio_file(audio_file)
        audio_data = await tts_provider.synthesize_with_reference(
            text=input,
            ref_audio_bytes=audio_bytes,
            ref_audio_ext=audio_ext,
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
