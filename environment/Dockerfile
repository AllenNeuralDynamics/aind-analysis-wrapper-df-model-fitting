# hash:sha256:9ba17e9455b2117a759cc1987ae7db6dcb7fd974962efa614b36c23c3ada6e2c
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG AWS_ACCESS_KEY_ID
ARG AWS_DEFAULT_REGION
ARG AWS_SECRET_ACCESS_KEY
ARG CODEOCEAN_API_TOKEN

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

ENV DOCDB_HOST=api.allenneuraldynamics.org
ENV DOCDB_DATABASE=analysis
ENV DOCDB_COLLECTION=dynamic-foraging-model-fitting
ENV CODEOCEAN_DOMAIN=codeocean.allenneuraldynamics.org
ENV CODEOCEAN_EMAIL=han.hou@alleninstitute.org
ENV ANALYSIS_BUCKET=aind-analysis-prod-o5171v/dynamic-foraging-model-fitting

RUN pip install -U --no-cache-dir \
    pydantic-settings==2.9.1 \
    s3fs \
    -e git+https://github.com/AllenNeuralDynamics/analysis-pipeline-utils@8a69491c67b79e5dcfb84084513ecba33b0160ed#egg=analysis-pipeline-utils \
    -e git+https://github.com/AllenNeuralDynamics/aind-dynamic-foraging-data-utils.git@a31e50197da91699d4a97153501c8e97c95dcfa3#egg=aind-dynamic-foraging-data-utils \
    -e git+https://github.com/AllenNeuralDynamics/aind-dynamic-foraging-models.git@9ffc0bca115a826e4ab9f71f3b3fbdaf4d151e83#egg=aind-dynamic-foraging-models[rl]

COPY postInstall /
RUN /postInstall
