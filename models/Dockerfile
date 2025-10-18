# Use Jupyter Data Science Notebook as base image
FROM jupyter/datascience-notebook:latest

# Set the working directory
WORKDIR /home/jovyan/work

# Switch to root to install system packages if needed
USER root

# Install any system dependencies (optional, uncomment if needed)
# RUN apt-get update && apt-get install -y \
#     libgomp1 \
#     && rm -rf /var/lib/apt/lists/*

# Switch back to the notebook user
USER $NB_UID

# Install Python packages
RUN pip install --no-cache-dir \
    awswrangler \
    boto3 \
    torch \
    torchvision \
    torchaudio \
    onnx \
    onnxruntime \
    scikit-learn \
    matplotlib \
    seaborn \
    python-dotenv

# Copy the .env file into the container
COPY --chown=$NB_UID:$NB_GID .env /home/jovyan/.env

# Create a startup script that loads .env and starts Jupyter
RUN echo '#!/bin/bash' > /home/jovyan/start-with-env.sh && \
    echo 'set -a' >> /home/jovyan/start-with-env.sh && \
    echo '[ -f /home/jovyan/.env ] && source /home/jovyan/.env' >> /home/jovyan/start-with-env.sh && \
    echo 'set +a' >> /home/jovyan/start-with-env.sh && \
    echo 'exec "$@"' >> /home/jovyan/start-with-env.sh && \
    chmod +x /home/jovyan/start-with-env.sh

# Expose Jupyter port
EXPOSE 8888

# Set environment variables for AWS (can be overridden at runtime)
ENV AWS_DEFAULT_REGION=us-west-2

# Use the startup script as entrypoint to load .env before starting Jupyter
ENTRYPOINT ["/home/jovyan/start-with-env.sh"]
CMD ["start-notebook.sh"]

