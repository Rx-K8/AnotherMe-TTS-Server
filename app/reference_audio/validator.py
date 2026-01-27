"""音声ファイルのバリデーション"""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pydub


@dataclass
class ValidationResult:
    """バリデーション結果"""

    is_valid: bool
    errors: list[str]
    sample_rate: int | None = None
    duration_seconds: float | None = None


class AudioValidator:
    """音声ファイルのバリデータ"""

    ALLOWED_MIME_TYPES = {
        "audio/wav",
        "audio/wave",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
    }

    ALLOWED_EXTENSIONS = {".wav", ".mp3"}

    MAX_FILE_SIZE = 10 * 1024 * 1024

    MAX_DURATION_SECONDS = 30.0
    MIN_DURATION_SECONDS = 0.5

    def __init__(
        self,
        max_file_size: int = MAX_FILE_SIZE,
        max_duration: float = MAX_DURATION_SECONDS,
        min_duration: float = MIN_DURATION_SECONDS,
    ) -> None:
        self.max_file_size = max_file_size
        self.max_duration = max_duration
        self.min_duration = min_duration

    def _validate_extension(self, filename: str) -> tuple[str, list[str]]:
        """
        ファイル拡張子をバリデーション

        Args:
            filename: ファイル名

        Returns:
            tuple[str, list[str]]: (拡張子, エラーリスト)
        """
        errors = []
        extension = Path(filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            errors.append(
                f"Unsupported file extension: {extension}. "
                f"Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        return extension, errors

    def _validate_mime_type(self, content_type: str) -> list[str]:
        """MIMEタイプをバリデーション

        Args:
            content_type: MIMEタイプ

        Returns:
            list[str]: エラーリスト
        """
        errors = []

        if content_type not in self.ALLOWED_MIME_TYPES:
            errors.append(
                f"Unsupported MIME type: {content_type}. "
                f"Allowed: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )

        return errors

    def _validate_file_size(self, file: BinaryIO) -> tuple[int, list[str]]:
        """ファイルサイズをバリデーション

        Args:
            file: 音声ファイルのバイナリストリーム

        Returns:
            tuple[int, list[str]]: (ファイルサイズ, エラーリスト)
        """
        errors = []

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > self.max_file_size:
            errors.append(
                f"File size {file_size} bytes exceeds maximum "
                f"{self.max_file_size} bytes"
            )

        return file_size, errors

    def _validate_audio_content(
        self,
        file: BinaryIO,
        extension: str,
    ) -> tuple[int | None, float | None, list[str]]:
        """音声コンテンツをバリデーション（パース・サンプルレート・音声長）

        Args:
            file: 音声ファイルのバイナリストリーム
            extension: ファイル拡張子（.付き）

        Returns:
            tuple[int | None, float | None, list[str]]:
                (サンプルレート, 音声長（秒）, エラーリスト)
        """
        errors = []
        sample_rate = None
        duration_seconds = None

        try:
            audio = pydub.AudioSegment.from_file(
                BytesIO(file.read()),
                format=extension[1:],
            )
            file.seek(0)

            sample_rate = audio.frame_rate
            duration_seconds = len(audio) / 1000.0

            if duration_seconds > self.max_duration:
                errors.append(
                    f"Audio duration {duration_seconds:.2f}s exceeds maximum "
                    f"{self.max_duration}s"
                )

            if duration_seconds < self.min_duration:
                errors.append(
                    f"Audio duration {duration_seconds:.2f}s is below minimum "
                    f"{self.min_duration}s"
                )

        except Exception as e:
            errors.append(f"Failed to parse audio file: {str(e)}")

        return sample_rate, duration_seconds, errors

    async def validate(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> ValidationResult:
        """
        音声ファイルをバリデーション

        Args:
            file: 音声ファイルのバイナリストリーム
            filename: ファイル名
            content_type: MIMEタイプ

        Returns:
            ValidationResult: バリデーション結果
        """
        all_errors: list[str] = []

        extension, ext_errors = self._validate_extension(filename)
        all_errors.extend(ext_errors)

        mime_errors = self._validate_mime_type(content_type)
        all_errors.extend(mime_errors)

        _, size_errors = self._validate_file_size(file)
        all_errors.extend(size_errors)

        sample_rate, duration_seconds, content_errors = self._validate_audio_content(
            file, extension
        )
        all_errors.extend(content_errors)

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            sample_rate=sample_rate,
            duration_seconds=duration_seconds,
        )


# TODO: jsonvalidator追加
