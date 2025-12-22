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
