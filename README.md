## インストール

### サブモジュールの初期化

```bash
git submodule update --init
```

### uv環境のセットアップ

```bash
# uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 本番環境
uv sync

# 開発環境
uv sync --group dev
```

### Linuxでの追加設定

```bash
# ubuntuの場合
apt install sox libsox-dev python3.10-dev
```

## 音声モデルのダウンロード

```bash
mkdir -p pretrained_models
git clone https://www.modelscope.cn/iic/CosyVoice2-0.5B.git pretrained_models/CosyVoice2-0.5B
```

## サーバーの起動

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Docker イメージのビルドと起動

### Docker イメージのビルド

```bash
docker build -t nvidia-anotherme/tts-server:12.8.1-cudnn-runtime-ubuntu22.04 .
```

### Docker コンテナの起動

```bash
docker run --rm -p 8001:8001 --gpus '"device=1"' nvidia-anotherme/tts-server:12.8.1-cudnn-runtime-ubuntu22.04
```
