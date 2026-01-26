FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
    locales \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen ja_JP.UTF-8 && update-locale LANG=ja_JP.UTF-8

ENV LANG=ja_JP.UTF-8 \
    LANGUAGE=ja_JP:ja \
    LC_ALL=ja_JP.UTF-8

ENV MINICONDA_VERSION=latest \
    CONDA_DIR=/opt/conda

RUN curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p ${CONDA_DIR} && \
    rm /tmp/miniconda.sh && \
    ${CONDA_DIR}/bin/conda clean -afy

ENV PATH=${CONDA_DIR}/bin:${PATH}

WORKDIR /app

COPY environment.yml requirements.txt ./

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

RUN conda env create -f environment.yml && \
    conda clean -afy

SHELL ["conda", "run", "-n", "anotherme_tts", "/bin/bash", "-c"]

COPY . .

CMD ["conda", "run", "--no-capture-output", "-n", "anotherme_tts", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
