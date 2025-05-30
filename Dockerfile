# Use PostgreSQL 16 for AGE compatibility
FROM postgres:16

# Set the working directory
WORKDIR /app

# Install build tools, PostgreSQL dev headers, and flex/bison
RUN apt-get update && apt-get install -y \
    git build-essential postgresql-server-dev-16 \
    libreadline-dev zlib1g-dev flex bison

# Set pg_config path explicitly
ENV PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config

# Clone and build Apache AGE from PG16-compatible branch
RUN git clone --branch release/PG16/1.5.0 https://github.com/apache/age.git /age && \
    cd /age && \
    make && \
    make install

# Copy your application files to the container
COPY . /app

# Copy the requirements file
COPY graphRAG/requirements.txt /app/requirements.txt

# Install Python 3.12 and other dependencies
RUN apt-get update && \
    apt-get install -y wget libffi-dev libssl-dev zlib1g-dev libncurses5-dev \
    libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev \
    libbz2-dev libexpat1-dev liblzma-dev tk-dev && \
    wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz && \
    tar -xvf Python-3.12.0.tgz && \
    cd Python-3.12.0 && \
    ./configure --enable-optimizations && \
    make -j 4 && \
    make altinstall && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3.12 get-pip.py && \
    apt-get install -y wget && \
    wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y powershell && \
    rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3.12 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt
# Upgrade to the latest OpenAI SDK (Azure-compatible)
RUN /app/venv/bin/pip install --upgrade openai

# Install Jupyter
RUN pip install jupyter

# Ensure the graphrag-folder exists
RUN mkdir -p /app/graphrag-folder \
    /app/graphrag-folder/input \
    /app/graphrag-folder/output \
    /app/graphrag-folder/cache \
    /app/graphrag-folder/prompts \
    /app/graphrag-folder/logs \
    /app/graphrag-folder/update_output \
    /app/graphrag-folder/restore \
    /app/plugins


# Expose necessary ports
EXPOSE 5432 8081 8082 8083 8888

