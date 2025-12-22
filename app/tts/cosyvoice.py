import sys

sys.path.append("third_party/CosyVoice")
sys.path.append("third_party/Matcha-TTS")
from collections.abc import AsyncIterator

import torch
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav

from app.converter import AudioConverterFactory
from app.schema import SynthesisParams
from app.tts.base import TTSProvider


class CosyVoiceTTSProvider(TTSProvider):
    # CosyVoice2のデフォルトサンプルレート
    SAMPLE_RATE = 22050

    def __init__(self, prompt_voice_path: str, prompt_text: str) -> None:
        self.cosyvoice = CosyVoice2(
            "pretrained_models/CosyVoice2-0.5B",
            load_jit=False,
            load_trt=False,
            load_vllm=False,
            fp16=False,
        )
        self.prompt_speech_text = prompt_text
        self.prompt_speech_voice = load_wav(prompt_voice_path, 16000)

    def _generate_pcm(self, params: SynthesisParams) -> bytes:
        """音声を合成してPCMデータを生成する（内部メソッド）"""
        audio_chunks = []
        for output in self.cosyvoice.inference_zero_shot(
            params.text,
            self.prompt_speech_text,
            self.prompt_speech_voice,
            speed=params.speed,
        ):
            audio_chunks.append(output["tts_speech"])

        if audio_chunks:
            audio = torch.cat(audio_chunks, dim=1)
            pcm_data: bytes = (audio * 32767).to(torch.int16).numpy().tobytes()
            return pcm_data

        return b""

    async def synthesize(self, params: SynthesisParams) -> bytes:
        pcm_data = self._generate_pcm(params)

        if not pcm_data:
            return b""

        converter = AudioConverterFactory.get_converter(params.format)
        return converter.convert(pcm_data, self.SAMPLE_RATE)

    async def synthesize_stream(self, params: SynthesisParams) -> AsyncIterator[bytes]:
        raise NotImplementedError("Streaming synthesis is not yet implemented")
        yield b""  # Make this an async generator  # pragma: no cover
