"""音声コンバーターファクトリー"""

from .base import AudioFormatConverter
from .mp3 import MP3Converter
from .pcm import PCMConverter
from .wav import WAVConverter


class AudioConverterFactory:
    """音声コンバーターのファクトリークラス

    サポートされているフォーマット:
        - pcm: 生のPCMデータ (ストリーミング対応)
        - wav: WAVフォーマット (ストリーミング対応)
        - mp3: MP3フォーマット (完全なデータが必要)
    """

    _converters: dict[str, type[AudioFormatConverter]] = {
        "pcm": PCMConverter,
        "wav": WAVConverter,
        "mp3": MP3Converter,
    }

    @classmethod
    def get_converter(cls, format_type: str, **kwargs) -> AudioFormatConverter:
        """指定されたフォーマットのコンバーターを取得

        Args:
            format_type: フォーマットタイプ ("pcm", "wav", "mp3")
            **kwargs: コンバーター固有のオプション
                - bitrate (MP3のみ): ビットレート (例: "128k", "192k", "320k")

        Returns:
            AudioFormatConverter: 指定されたフォーマットのコンバーター

        Raises:
            ValueError: サポートされていないフォーマットの場合

        Examples:
            >>> factory = AudioConverterFactory()
            >>> wav_converter = factory.get_converter("wav")
            >>> mp3_converter = factory.get_converter("mp3", bitrate="192k")
        """
        converter_class = cls._converters.get(format_type.lower())
        if converter_class is None:
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {list(cls._converters.keys())}"
            )

        if format_type.lower() == "mp3" and "bitrate" in kwargs:
            return converter_class(bitrate=kwargs["bitrate"])

        return converter_class()

    @classmethod
    def register_converter(
        cls, format_type: str, converter_class: type[AudioFormatConverter]
    ) -> None:
        """新しいコンバーターを登録 (OCP: 拡張のために開放)

        Args:
            format_type: フォーマットタイプ
            converter_class: AudioFormatConverterを継承したクラス

        Examples:
            >>> class OggConverter(AudioFormatConverter):
            ...     def convert(self, pcm_data, sample_rate, channels=1):
            ...         # 実装
            ...         pass
            >>> AudioConverterFactory.register_converter("ogg", OggConverter)
        """
        cls._converters[format_type.lower()] = converter_class

    @classmethod
    def supported_formats(cls) -> list[str]:
        """サポートされているフォーマットの一覧を取得

        Returns:
            list[str]: サポートされているフォーマットのリスト
        """
        return list(cls._converters.keys())
