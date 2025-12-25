import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schema import TTSErrorResponse, TTSRequest, TTSResponse
from app.dependencies import get_tts_service
from app.schema import SynthesisParams
from app.service import TTSService
from app.utils import encode_audio_base64

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


def _convert_request(request: TTSRequest) -> SynthesisParams:
    """TTSリクエストを内部パラメータに変換"""
    return SynthesisParams(
        text=request.input,
        format=request.response_format,
        speed=request.speed,
    )


@router.post(
    "/synthesize",
    response_model=TTSResponse,
    responses={
        400: {"model": TTSErrorResponse, "description": "不正なリクエスト"},
        500: {"model": TTSErrorResponse, "description": "内部サーバーエラー"},
    },
    summary="テキストから音声を合成",
    description="指定されたテキストを音声に変換し、Base64エンコードされた音声データを返します。",
)
async def synthesize_text(
    request: TTSRequest,
    tts_service: TTSService = Depends(get_tts_service),
) -> TTSResponse:
    """
    テキストを音声に合成するエンドポイント

    - input: 音声合成するテキスト
    - response_format: 出力フォーマット (wav, mp3)
    - speed: 再生速度 (デフォルト: 1.0)
    """
    try:
        params = _convert_request(request)
        audio_data = await tts_service.synthesize(params)
        encoded_audio = encode_audio_base64(audio_data)

        return TTSResponse(
            audio_data=encoded_audio,
            format=request.response_format,
            sample_rate=22050,
        )
    except ValueError as e:
        logger.error(f"不正なリクエストパラメータ: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"音声合成中にエラーが発生しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音声合成中にエラーが発生しました: {str(e)}",
        )
