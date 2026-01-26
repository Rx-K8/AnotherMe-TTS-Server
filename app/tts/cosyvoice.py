import sys

sys.path.append("third_party/CosyVoice")
sys.path.append("third_party/Matcha-TTS")
from collections.abc import AsyncIterator

import torch
from app.schema import SynthesisParams
from app.tts.base import TTSProvider
from cosyvoice.cli.cosyvoice import CosyVoice2

from app.converter import AudioConverterFactory


class CosyVoiceTTSProvider(TTSProvider):
    SAMPLE_RATE = 22050

    def __init__(self, prompt_voice_path: str, prompt_text: str) -> None:
        self.cosyvoice = CosyVoice2(
            "pretrained_models/CosyVoice2-0.5B",
            load_jit=False,
            load_trt=False,
            load_vllm=False,
            fp16=False,
        )
        self.prompt_text = prompt_text
        self.prompt_voice_path = prompt_voice_path

    def _generate_pcm(self, params: SynthesisParams) -> bytes:
        """音声を合成してPCMデータを生成する（内部メソッド）"""
        audio_tensors = []
        for output in self.cosyvoice.inference_zero_shot(
            params.text,
            self.prompt_text,
            self.prompt_voice_path,
            speed=params.speed,
        ):
            audio_tensors.append(output["tts_speech"])

        if not audio_tensors:
            return b""

        combined_audio_tensor = torch.cat(audio_tensors, dim=1)

        audio_on_cpu = (
            combined_audio_tensor.cpu()
            if combined_audio_tensor.is_cuda
            else combined_audio_tensor
        )
        audio_numpy = audio_on_cpu.numpy()

        pcm_data: bytes = (audio_numpy * 32767).astype("int16").tobytes()
        return pcm_data

    async def synthesize(self, params: SynthesisParams) -> bytes:
        pcm_audio_data = self._generate_pcm(params)

        if not pcm_audio_data:
            return b""

        audio_converter = AudioConverterFactory.get_converter(params.format)
        return audio_converter.convert(pcm_audio_data, self.SAMPLE_RATE)

    async def synthesize_stream(self, params: SynthesisParams) -> AsyncIterator[bytes]:
        raise NotImplementedError("Streaming synthesis is not yet implemented")
        yield b""  # Make this an async generator  # pragma: no cover
