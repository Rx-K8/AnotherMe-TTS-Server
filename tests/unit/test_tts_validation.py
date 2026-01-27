from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.api.routes.tts import MAX_AUDIO_SIZE_BYTES, _validate_audio_file


class TestValidateAudioFile:
    async def test_valid_wav_file(self) -> None:
        content = b"fake wav content"
        upload_file = UploadFile(filename="test.wav", file=BytesIO(content))
        result = await _validate_audio_file(upload_file)
        assert result == content

    async def test_valid_wav_uppercase_extension(self) -> None:
        content = b"fake wav content"
        upload_file = UploadFile(filename="test.WAV", file=BytesIO(content))
        result = await _validate_audio_file(upload_file)
        assert result == content

    async def test_reject_mp3_extension(self) -> None:
        upload_file = UploadFile(filename="test.mp3", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await _validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400
        assert "WAVのみ" in str(exc_info.value.detail)

    async def test_reject_no_extension(self) -> None:
        upload_file = UploadFile(filename="testfile", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await _validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_reject_empty_filename(self) -> None:
        upload_file = UploadFile(filename="", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await _validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_reject_oversized_file(self) -> None:
        large_content = b"x" * (MAX_AUDIO_SIZE_BYTES + 1)
        upload_file = UploadFile(filename="test.wav", file=BytesIO(large_content))
        with pytest.raises(HTTPException) as exc_info:
            await _validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400
        assert "10MB" in str(exc_info.value.detail)

    async def test_accept_exactly_max_size(self) -> None:
        content = b"x" * MAX_AUDIO_SIZE_BYTES
        upload_file = UploadFile(filename="test.wav", file=BytesIO(content))
        result = await _validate_audio_file(upload_file)
        assert len(result) == MAX_AUDIO_SIZE_BYTES
