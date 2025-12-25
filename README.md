## インストール

### サブモジュールの初期化

```bash
git submodule update --init
```

### Conda環境のセットアップ

```bash
# 本番環境
conda env create -f environment.yml

# 開発環境
conda env create -f environment-dev.yml
```

### Linuxでの追加設定

```bash
# ubuntuの場合
apt install sox libsox-dev
```

## 音声モデルのダウンロード

```bash
# git lfsが必要です。
mkdir -p pretrained_models
git clone https://www.modelscope.cn/iic/CosyVoice2-0.5B.git pretrained_models/CosyVoice2-0.5B
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
