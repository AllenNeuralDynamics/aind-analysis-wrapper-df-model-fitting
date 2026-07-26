# hash:sha256:9be9da638ad9243a3f74bc4f5992f3a4aa177e59a4f326f12be2c970cd6a4f01
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

# Non-secret configuration now lives in code/settings.env, loaded by
# run_capsule.py via python-dotenv. Secrets are injected at run time.

RUN pip install -U --no-cache-dir \
    -e git+https://github.com/hanhou/analysis-pipeline-utils.git@72f92e1a07504f6735786442d78edbeee9f69893#egg=analysis-pipeline-utils \
    boto3==1.42.30 \
    pydantic-settings==2.9.1 \
    s3fs==2026.1.0 \
    -e git+https://github.com/AllenNeuralDynamics/aind-dynamic-foraging-data-utils.git@a31e50197da91699d4a97153501c8e97c95dcfa3#egg=aind-dynamic-foraging-data-utils \
    -e git+https://github.com/AllenNeuralDynamics/aind-dynamic-foraging-models.git@9ffc0bca115a826e4ab9f71f3b3fbdaf4d151e83#egg=aind-dynamic-foraging-models[rl]

COPY postInstall /
RUN /postInstall
