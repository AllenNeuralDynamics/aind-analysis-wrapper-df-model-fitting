# hash:sha256:7d8fb61e67fa43b1dcca5a1ee89bc25c0fd59f5273af4fa49ea0980146040fc9
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip install -U --no-cache-dir \
    aind-dynamic-foraging-data-utils==0.1.56 \
    aind-dynamic-foraging-models[rl]==0.19.0 \
    analysis-pipeline-utils==0.2.8 \
    boto3==1.42.30 \
    pydantic-settings==2.9.1 \
    s3fs==2026.1.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
