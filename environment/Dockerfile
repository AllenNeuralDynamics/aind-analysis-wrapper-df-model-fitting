# hash:sha256:e939999f828c09d1d3840e8f6e4cd3242ce5240633edb467b8c853836ec6d960
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip install -U --no-cache-dir \
    aind-dynamic-foraging-data-utils==0.1.56 \
    aind-dynamic-foraging-models[rl]==0.12.3 \
    analysis-pipeline-utils==0.2.8 \
    boto3==1.42.30 \
    pydantic-settings==2.9.1 \
    s3fs==2026.1.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
