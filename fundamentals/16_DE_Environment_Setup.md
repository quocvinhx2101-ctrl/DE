# DE Environment Setup - Complete Guide

## Dev Environment, Docker, CI/CD, Kubernetes & Production-Ready Infrastructure

---

## 📋 Mục Lục

1. [Local Development Environment](#phần-1-local-development-environment)
2. [Python Environment Management](#phần-2-python-environment-management)
3. [IDE Setup — VS Code](#phần-3-ide-setup--vs-code)
4. [Docker for Data Engineering](#phần-4-docker-for-data-engineering)
5. [Docker Compose Templates](#phần-5-docker-compose-templates)
6. [CI/CD for Data Projects](#phần-6-cicd-for-data-projects)
7. [Infrastructure as Code](#phần-7-infrastructure-as-code)
8. [Kubernetes for DE](#phần-8-kubernetes-for-de)
9. [Monitoring & Observability Stack](#phần-9-monitoring--observability-stack)
10. [Production Readiness Checklist](#phần-10-production-readiness-checklist)
11. [Project Templates](#phần-11-project-templates)
12. [Environment Management (Dev/Staging/Prod)](#phần-12-environment-management)
13. [Security Hardening](#phần-13-security-hardening)

---

## PHẦN 1: LOCAL DEVELOPMENT ENVIRONMENT

### 1.1 System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores | 8+ cores (Apple M3) |
| RAM | 8 GB | 16-32 GB |
| Storage | 256 GB SSD | 512 GB+ NVMe SSD |
| OS | Ubuntu 22.04+ / macOS 14+ | Ubuntu 24.04 / macOS / Fedora 40+ |
| Docker | 4 GB RAM | 8+ GB RAM allocated |

Why these specs?
- Spark local mode needs 4+ GB RAM
- Docker Compose stacks (Kafka+Flink+Postgres) need 6+ GB
- IDE + Docker + tests running simultaneously

### 1.2 Shell Setup (Linux/macOS)

```bash
# ============================================================
# Fish Shell (recommended for DE — great autocomplete)
# ============================================================

# Install fish (Ubuntu)
sudo apt-add-repository ppa:fish-shell/release-3
sudo apt update
sudo apt install fish

# Install fish (macOS)
brew install fish

# Set as default shell
chsh -s $(which fish)

# Fish config: ~/.config/fish/config.fish
set -gx EDITOR code
set -gx VISUAL code
set -gx LANG en_US.UTF-8

# Data Engineering paths
set -gx SPARK_HOME $HOME/spark
set -gx JAVA_HOME (/usr/libexec/java_home -v 17 2>/dev/null; or echo /usr/lib/jvm/java-17-openjdk)
fish_add_path $SPARK_HOME/bin

# Aliases
alias k='kubectl'
alias dc='docker compose'
alias dbt='cd ~/projects/dbt-project && dbt'
alias lg='lazygit'
alias tf='terraform'


# ============================================================
# Starship Prompt (cross-shell, fast, informative)
# ============================================================

# Install
curl -sS https://starship.rs/install.sh | sh

# Fish integration: ~/.config/fish/config.fish
starship init fish | source

# Config: ~/.config/starship.toml
# Shows: git branch, Python version, Docker context, K8s namespace
"""
[python]
format = '[${symbol}${pyenv_prefix}(${version})]($style) '

[docker_context]
format = '[🐳 $context]($style) '

[kubernetes]
disabled = false
format = '[☸ $context:$namespace]($style) '

[git_branch]
format = '[$symbol$branch(:$remote_branch)]($style) '

[directory]
truncation_length = 3
"""


# ============================================================
# Zsh Alternative (if not using fish)
# ============================================================

# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Plugins: ~/.zshrc
plugins=(
    git
    docker
    docker-compose
    kubectl
    python
    virtualenv
    zsh-autosuggestions
    zsh-syntax-highlighting
)
```

### 1.3 Essential CLI Tools

```bash
# ============================================================
# Core development tools
# ============================================================

# Package managers
# macOS
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Ubuntu/Debian
sudo apt update && sudo apt install -y \
    build-essential curl wget git unzip jq \
    software-properties-common apt-transport-https

# ============================================================
# Data Engineering CLI tools
# ============================================================

# Docker & Docker Compose
# Ubuntu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# macOS
brew install --cask docker

# Verify
docker --version
docker compose version

# ============================================================
# Database CLIs
# ============================================================

# PostgreSQL client
sudo apt install -y postgresql-client  # Ubuntu
brew install libpq                     # macOS

# MySQL client
sudo apt install -y mysql-client       # Ubuntu
brew install mysql-client              # macOS

# Redis CLI
sudo apt install -y redis-tools        # Ubuntu
brew install redis                     # macOS

# DuckDB CLI
# Download from https://duckdb.org/docs/installation/
wget https://github.com/duckdb/duckdb/releases/download/v1.1.0/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
sudo mv duckdb /usr/local/bin/

# ============================================================
# Cloud CLIs
# ============================================================

# AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# ============================================================
# Kubernetes tools (if using K8s)
# ============================================================

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# k9s — TUI for Kubernetes
brew install derailed/k9s/k9s

# ============================================================
# Productivity tools
# ============================================================

# lazygit — Git TUI
brew install lazygit           # macOS
sudo apt install lazygit       # Ubuntu (via PPA)

# bat — better cat
brew install bat               # macOS
sudo apt install bat           # Ubuntu

# ripgrep — faster grep
brew install ripgrep           # macOS
sudo apt install ripgrep       # Ubuntu

# fd — faster find
brew install fd                # macOS
sudo apt install fd-find       # Ubuntu

# fzf — fuzzy finder
brew install fzf               # macOS
sudo apt install fzf           # Ubuntu

# tldr — simplified man pages
npm install -g tldr            # or pip install tldr

# httpie — better curl for APIs
brew install httpie            # macOS
pip install httpie             # Any OS
```

---

## PHẦN 2: PYTHON ENVIRONMENT MANAGEMENT

### 2.1 Python Version Management with pyenv

```bash
# ============================================================
# pyenv — manage multiple Python versions
# ============================================================

# Install pyenv
curl https://pyenv.run | bash

# Add to shell (~/.bashrc or ~/.config/fish/config.fish)
# Bash/Zsh:
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Fish:
set -gx PYENV_ROOT $HOME/.pyenv
fish_add_path $PYENV_ROOT/bin
pyenv init - | source

# Install Python versions
pyenv install 3.11.10
pyenv install 3.12.7

# Set global default
pyenv global 3.12.7

# Set local version per project
cd my-project/
pyenv local 3.11.10   # Creates .python-version file

# List available / installed
pyenv install --list | grep "3.1[12]"
pyenv versions
```

### 2.2 UV — Modern Package Manager (Recommended)

```bash
# ============================================================
# UV: 10-100x faster than pip, replaces pip + venv + pip-tools
# ============================================================

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# ============================================================
# Project workflow
# ============================================================

# Initialize new project
uv init my-de-pipeline
cd my-de-pipeline

# Add production dependencies
uv add polars duckdb pyarrow
uv add sqlalchemy psycopg2-binary
uv add pydantic-settings structlog
uv add tenacity httpx

# Add development dependencies
uv add --dev pytest pytest-cov
uv add --dev ruff mypy
uv add --dev pre-commit
uv add --dev ipython

# Lock dependencies (creates uv.lock)
uv lock

# Sync environment from lock file
uv sync

# Run commands in the environment
uv run python -m src.main
uv run pytest tests/
uv run ruff check src/

# ============================================================
# UV with specific Python version
# ============================================================

# Use specific Python version for project
uv python install 3.12
uv init --python 3.12 my-project

# Pin Python version
uv python pin 3.12
```

### 2.3 pyproject.toml — Complete Configuration

```toml
# pyproject.toml — Single source of truth for DE project config

[project]
name = "my-de-pipeline"
version = "0.1.0"
description = "Data pipeline for order analytics"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [
    { name = "Data Team", email = "data@company.com" },
]

dependencies = [
    # Data processing
    "polars>=1.0",
    "pyarrow>=17.0",
    "duckdb>=1.0",
    
    # Database connectivity
    "sqlalchemy>=2.0",
    "psycopg2-binary>=2.9",
    
    # Configuration
    "pydantic-settings>=2.0",
    "python-dotenv>=1.0",
    
    # Observability
    "structlog>=24.0",
    "tenacity>=9.0",
    
    # HTTP
    "httpx>=0.27",
]

[project.optional-dependencies]
spark = [
    "pyspark>=3.5",
]
airflow = [
    "apache-airflow>=2.9",
]

[project.scripts]
run-pipeline = "src.main:main"
run-backfill = "src.backfill:main"

# ============================================================
# Tool configurations (all in one file!)
# ============================================================

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-timeout>=2.3",
    "ruff>=0.8",
    "mypy>=1.13",
    "pre-commit>=4.0",
    "ipython>=8.0",
    "types-requests",
    "types-PyYAML",
]

[tool.ruff]
target-version = "py311"
line-length = 100
fix = true

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "TCH", "RUF", "PERF"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["src"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true

[tool.mypy]
python_version = "3.11"
warn_return_any = true
disallow_untyped_defs = true
check_untyped_defs = true
no_implicit_optional = true

[[tool.mypy.overrides]]
module = ["pyspark.*", "airflow.*", "great_expectations.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "integration: Integration tests (need Docker)",
    "slow: Slow tests (>30s)",
]
timeout = 60

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "scripts/*"]

[tool.coverage.report]
show_missing = true
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "if TYPE_CHECKING:",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## PHẦN 3: IDE SETUP — VS CODE

### 3.1 Essential Extensions

```json
// .vscode/extensions.json — Team-shared recommended extensions
{
    "recommendations": [
        // Python
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        
        // SQL
        "mtxr.sqltools",
        "mtxr.sqltools-driver-pg",
        "dorzey.vscode-sqlfluff",
        
        // Docker & K8s
        "ms-azuretools.vscode-docker",
        "ms-kubernetes-tools.vscode-kubernetes-tools",
        
        // Data / dbt
        "innoverio.vscode-dbt-power-user",
        "mechatroner.rainbow-csv",
        "RandomFractalsInc.vscode-data-preview",
        
        // Git
        "eamodio.gitlens",
        "mhutchie.git-graph",
        
        // Productivity
        "esbenp.prettier-vscode",
        "redhat.vscode-yaml",
        "tamasfe.even-better-toml",
        "usernamehw.errorlens",
        "streetsidesoftware.code-spell-checker",
        
        // Markdown / Docs
        "yzhang.markdown-all-in-one",
        "bierner.markdown-mermaid"
    ]
}
```

### 3.2 VS Code Settings for DE

```jsonc
// .vscode/settings.json — Project-level settings
{
    // Python
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    
    // Ruff (replaces black, isort, flake8)
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },
    
    // SQL
    "[sql]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "dorzey.vscode-sqlfluff"
    },
    
    // YAML (Airflow, dbt, docker-compose)
    "[yaml]": {
        "editor.defaultFormatter": "redhat.vscode-yaml",
        "editor.formatOnSave": true
    },
    
    // Docker
    "[dockerfile]": {
        "editor.defaultFormatter": "ms-azuretools.vscode-docker"
    },
    
    // General
    "editor.rulers": [100],
    "editor.renderWhitespace": "boundary",
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.ruff_cache": true,
        "**/dbt_packages": true,
        "**/target": true
    },
    
    // SQLTools connection
    "sqltools.connections": [
        {
            "name": "Local Postgres",
            "driver": "PostgreSQL",
            "server": "localhost",
            "port": 5432,
            "database": "analytics",
            "username": "dev",
            "password": "dev_password"
        }
    ]
}
```

### 3.3 VS Code Debug Configurations

```jsonc
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Pipeline",
            "type": "debugpy",
            "request": "launch",
            "module": "src.main",
            "console": "integratedTerminal",
            "env": {
                "ENVIRONMENT": "development",
                "LOG_LEVEL": "DEBUG"
            },
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Run Tests",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v", "--tb=short"],
            "console": "integratedTerminal"
        },
        {
            "name": "Debug Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Airflow Task",
            "type": "debugpy",
            "request": "launch",
            "module": "airflow",
            "args": ["tasks", "test", "dag_id", "task_id", "2024-01-01"],
            "console": "integratedTerminal"
        }
    ]
}
```

---

## PHẦN 4: DOCKER FOR DATA ENGINEERING

### 4.1 Dockerfile Best Practices

```dockerfile
# ============================================================
# Production Dockerfile for Python Data Pipeline
# Multi-stage build, non-root user, minimal attack surface
# ============================================================

# ---- Stage 1: Build dependencies ----
FROM python:3.12-slim AS builder

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (layer caching!)
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies (cached unless pyproject.toml changes)
RUN uv sync --frozen --no-dev --no-editable


# ---- Stage 2: Runtime image ----
FROM python:3.12-slim AS runtime

# Install runtime-only system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (security!)
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy installed packages from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
WORKDIR /app
COPY src/ ./src/
COPY config/ ./config/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "-m", "src.main"]


# ============================================================
# Dockerfile for Spark Jobs
# ============================================================

# FROM apache/spark-py:v3.5.3
# 
# USER root
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# 
# COPY src/ /opt/spark/work-dir/src/
# 
# USER spark
# ENTRYPOINT ["/opt/spark/bin/spark-submit"]
# CMD ["--master", "local[*]", "/opt/spark/work-dir/src/main.py"]
```

### 4.2 Docker Compose Best Practices

```yaml
# docker-compose.yml — Best practices template

# ============================================================
# RULE 1: Pin image versions (never use :latest in production)
# RULE 2: Set resource limits
# RULE 3: Use health checks
# RULE 4: Named volumes for persistence
# RULE 5: Use .env file for configuration
# ============================================================

services:
  postgres:
    image: postgres:16.4              # Pinned version!
    container_name: de-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER:-dev}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-dev_password}
      POSTGRES_DB: ${DB_NAME:-analytics}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-dev}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"

  redis:
    image: redis:7.4-alpine           # Alpine = smaller image
    container_name: de-redis
    restart: unless-stopped
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 512M

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
```

### 4.3 .dockerignore

```
# .dockerignore — Reduce build context, faster builds

# Version control
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
.ruff_cache
htmlcov
.coverage
*.egg-info
dist
build

# Virtual environments
.venv
venv
env

# IDE
.vscode
.idea
*.swp
*.swo

# Docker
docker-compose*.yml
Dockerfile*

# Documentation
docs/
*.md
LICENSE

# Data files (don't send to Docker!)
data/
*.csv
*.parquet
*.json
!config/*.json

# Environment files with secrets
.env
.env.local
.env.production

# OS
.DS_Store
Thumbs.db

# Notebooks
*.ipynb
.ipynb_checkpoints
```

---

## PHẦN 5: DOCKER COMPOSE TEMPLATES

### 5.1 Template: dbt + Postgres + Airflow

```yaml
# docker-compose-dbt-airflow.yml
# Stack: PostgreSQL + Airflow + dbt (Analytics Engineering)

services:
  # Source database
  postgres:
    image: postgres:16.4
    container_name: source-db
    environment:
      POSTGRES_USER: source
      POSTGRES_PASSWORD: source_pass
      POSTGRES_DB: production
    ports:
      - "5432:5432"
    volumes:
      - source_data:/var/lib/postgresql/data
      - ./seed/source_data.sql:/docker-entrypoint-initdb.d/01_seed.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U source"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Analytics warehouse
  warehouse:
    image: postgres:16.4
    container_name: analytics-warehouse
    environment:
      POSTGRES_USER: analytics
      POSTGRES_PASSWORD: analytics_pass
      POSTGRES_DB: warehouse
    ports:
      - "5433:5432"
    volumes:
      - warehouse_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U analytics"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Airflow (standalone mode for dev)
  airflow:
    image: apache/airflow:2.10.4-python3.12
    container_name: airflow
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@airflow-db:5432/airflow
      AIRFLOW__CORE__FERNET_KEY: "81HqDtbqAywKSOumSha3BhWNOdQ26slT6K0YaZeZyPs="
      AIRFLOW__CORE__LOAD_EXAMPLES: "false"
      AIRFLOW__WEBSERVER__EXPOSE_CONFIG: "true"
      _AIRFLOW_DB_MIGRATE: "true"
      _AIRFLOW_WWW_USER_CREATE: "true"
      _AIRFLOW_WWW_USER_USERNAME: admin
      _AIRFLOW_WWW_USER_PASSWORD: admin
    ports:
      - "8080:8080"
    volumes:
      - ./dags/:/opt/airflow/dags/:ro
      - ./dbt_project/:/opt/airflow/dbt/:ro
      - airflow_logs:/opt/airflow/logs
    depends_on:
      airflow-db:
        condition: service_healthy
    command: airflow standalone

  airflow-db:
    image: postgres:16.4
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - airflow_db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airflow"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  source_data:
  warehouse_data:
  airflow_db_data:
  airflow_logs:
```

### 5.2 Template: Kafka + Flink + Iceberg

```yaml
# docker-compose-streaming.yml
# Stack: Kafka + Schema Registry + Flink + Iceberg + MinIO

services:
  # Kafka (KRaft mode — no ZooKeeper needed)
  kafka:
    image: confluentinc/cp-kafka:7.7.1
    container_name: kafka
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT"
      KAFKA_ADVERTISED_LISTENERS: "PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092"
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:29093"
      KAFKA_LISTENERS: "PLAINTEXT://kafka:29092,CONTROLLER://kafka:29093,PLAINTEXT_HOST://0.0.0.0:9092"
      KAFKA_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_LOG_RETENTION_HOURS: 168
    ports:
      - "9092:9092"
    volumes:
      - kafka_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s

  schema-registry:
    image: confluentinc/cp-schema-registry:7.7.1
    container_name: schema-registry
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: "kafka:29092"
    ports:
      - "8081:8081"
    depends_on:
      kafka:
        condition: service_healthy

  # Flink (JobManager + TaskManager)
  flink-jobmanager:
    image: apache/flink:1.20-java17
    container_name: flink-jobmanager
    command: jobmanager
    environment:
      FLINK_PROPERTIES: |
        jobmanager.rpc.address: flink-jobmanager
        state.backend: rocksdb
        state.checkpoints.dir: file:///opt/flink/checkpoints
    ports:
      - "8082:8081"
    volumes:
      - flink_checkpoints:/opt/flink/checkpoints
      - ./flink-jobs/:/opt/flink/usrlib/:ro

  flink-taskmanager:
    image: apache/flink:1.20-java17
    container_name: flink-taskmanager
    command: taskmanager
    environment:
      FLINK_PROPERTIES: |
        jobmanager.rpc.address: flink-jobmanager
        taskmanager.numberOfTaskSlots: 4
        state.backend: rocksdb
        state.checkpoints.dir: file:///opt/flink/checkpoints
    volumes:
      - flink_checkpoints:/opt/flink/checkpoints
    depends_on:
      - flink-jobmanager

  # MinIO (S3-compatible object storage)
  minio:
    image: minio/minio:RELEASE.2024-11-07T00-52-20Z
    container_name: minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Kafka UI for debugging
  kafka-ui:
    image: provectuslabs/kafka-ui:v0.7.2
    container_name: kafka-ui
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_SCHEMAREGISTRY: http://schema-registry:8081
    ports:
      - "8083:8080"
    depends_on:
      kafka:
        condition: service_healthy

volumes:
  kafka_data:
  flink_checkpoints:
  minio_data:
```

### 5.3 Template: Observability Stack

```yaml
# docker-compose-observability.yml
# Stack: Prometheus + Grafana + Loki (logs) + Alertmanager

services:
  prometheus:
    image: prom/prometheus:v2.54.1
    container_name: prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.retention.time=30d"

  grafana:
    image: grafana/grafana:11.3.0
    container_name: grafana
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning/:/etc/grafana/provisioning/:ro
    depends_on:
      - prometheus

  loki:
    image: grafana/loki:3.2.0
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml

  alertmanager:
    image: prom/alertmanager:v0.27.0
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

---

## PHẦN 6: CI/CD FOR DATA PROJECTS

### 6.1 GitHub Actions — Complete Workflow

```yaml
# .github/workflows/ci.yml
name: Data Pipeline CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.12"

jobs:
  # ============================================================
  # Job 1: Lint & Type Check
  # ============================================================
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      
      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: uv sync --frozen
      
      - name: Ruff lint
        run: uv run ruff check src/ tests/
      
      - name: Ruff format check
        run: uv run ruff format --check src/ tests/
      
      - name: Type check (mypy)
        run: uv run mypy src/ --ignore-missing-imports
      
      - name: SQL lint (if SQL files exist)
        run: |
          if find . -name "*.sql" -not -path "./dbt_packages/*" | head -1 | grep -q .; then
            uv run sqlfluff lint models/ --dialect postgres
          fi

  # ============================================================
  # Job 2: Unit Tests
  # ============================================================
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: uv sync --frozen
      
      - name: Run unit tests
        run: uv run pytest tests/unit/ -v --tb=short --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  # ============================================================
  # Job 3: Integration Tests (with Docker services)
  # ============================================================
  integration:
    runs-on: ubuntu-latest
    needs: test
    services:
      postgres:
        image: postgres:16.4
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U test"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7.4-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: uv sync --frozen
      
      - name: Run integration tests
        env:
          DB_HOST: localhost
          DB_PORT: 5432
          DB_USER: test
          DB_PASSWORD: test
          DB_NAME: test_db
          REDIS_HOST: localhost
          REDIS_PORT: 6379
        run: uv run pytest tests/integration/ -v --timeout=120

  # ============================================================
  # Job 4: dbt Tests (if dbt project exists)
  # ============================================================
  dbt:
    runs-on: ubuntu-latest
    needs: lint
    if: hashFiles('dbt_project.yml') != ''
    services:
      warehouse:
        image: postgres:16.4
        env:
          POSTGRES_USER: dbt
          POSTGRES_PASSWORD: dbt
          POSTGRES_DB: warehouse
        ports:
          - 5433:5432
        options: >-
          --health-cmd "pg_isready -U dbt"
          --health-interval 10s
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}
      
      - name: Install dbt
        run: uv pip install dbt-postgres
      
      - name: dbt deps
        run: dbt deps
        working-directory: ./dbt_project
      
      - name: dbt build (run + test)
        env:
          DBT_PROFILES_DIR: ./
        run: dbt build --target ci
        working-directory: ./dbt_project

  # ============================================================
  # Job 5: Build & Push Docker Image
  # ============================================================
  build:
    runs-on: ubuntu-latest
    needs: [test, integration]
    if: github.ref == 'refs/heads/main'
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 6.2 Pre-commit CI Configuration

```yaml
# .pre-commit-config.yaml
# See fundamentals/15_Clean_Code_Data_Engineering.md for full config

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
        args: [--unsafe]
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: no-commit-to-branch
        args: [--branch, main]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: [--baseline, .secrets.baseline]
```

---

## PHẦN 7: INFRASTRUCTURE AS CODE

### 7.1 Terraform — AWS Data Platform

```hcl
# terraform/main.tf — AWS Data Platform infrastructure

terraform {
  required_version = ">= 1.9"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "data-platform/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "data-platform"
      ManagedBy   = "terraform"
      Team        = "data-engineering"
    }
  }
}

# ============================================================
# S3 Data Lake
# ============================================================

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-${var.environment}-data-lake"
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  rule {
    id     = "archive-old-data"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 365
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# ============================================================
# RDS PostgreSQL (Source/Metadata)
# ============================================================

resource "aws_db_instance" "metadata" {
  identifier     = "${var.project_name}-${var.environment}-metadata"
  engine         = "postgres"
  engine_version = "16.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "metadata"
  username = "admin"
  password = var.db_password  # From secrets
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  deletion_protection     = var.environment == "production"
  skip_final_snapshot     = var.environment != "production"
  
  performance_insights_enabled = true
}

# ============================================================
# Variables
# ============================================================

variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
}

variable "project_name" {
  default = "data-platform"
}

variable "db_instance_class" {
  default = "db.t3.medium"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

### 7.2 Terraform Project Structure

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf          # Module calls with dev values
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
│
├── modules/
│   ├── data-lake/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── database/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── airflow/
│       ├── main.tf           # MWAA or ECS
│       ├── variables.tf
│       └── outputs.tf
│
└── README.md
```

---

## PHẦN 8: KUBERNETES FOR DE

### 8.1 Airflow on Kubernetes (Helm)

```bash
# ============================================================
# Deploy Apache Airflow on K8s using official Helm chart
# ============================================================

# Add Helm repo
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Create namespace
kubectl create namespace airflow

# Create secrets
kubectl create secret generic airflow-db-password \
    --from-literal=connection='postgresql://airflow:airflow@postgres:5432/airflow' \
    -n airflow

# Install with custom values
helm install airflow apache-airflow/airflow \
    --namespace airflow \
    --values airflow-values.yaml \
    --timeout 10m
```

```yaml
# airflow-values.yaml — Production-ready Airflow on K8s

# Executor: KubernetesExecutor (each task = separate pod)
executor: KubernetesExecutor

# Git sync for DAGs (pull from repo automatically)
dags:
  gitSync:
    enabled: true
    repo: https://github.com/company/airflow-dags.git
    branch: main
    subPath: dags/
    wait: 60  # seconds between syncs

# Webserver
webserver:
  replicas: 2
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

# Scheduler
scheduler:
  replicas: 2   # HA scheduler
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

# Worker pod template (for KubernetesExecutor)
workers:
  resources:
    requests:
      memory: "2Gi"
      cpu: "1000m"
    limits:
      memory: "4Gi"
      cpu: "2000m"

# Database (use external for production)
postgresql:
  enabled: false  # Use external managed database

data:
  metadataConnection:
    protocol: postgresql
    host: your-rds-endpoint.rds.amazonaws.com
    port: 5432
    db: airflow
    login: airflow
    passwordSecretName: airflow-db-password

# Logging to S3
config:
  AIRFLOW__LOGGING__REMOTE_LOGGING: "True"
  AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER: "s3://airflow-logs/logs"
  AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID: "aws_default"
```

### 8.2 Spark on Kubernetes

```yaml
# spark-job.yaml — Submit Spark job to K8s

apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: daily-orders-pipeline
  namespace: spark
spec:
  type: Python
  mode: cluster
  image: ghcr.io/company/spark-pipeline:latest
  imagePullPolicy: Always
  mainApplicationFile: local:///opt/spark/work-dir/src/main.py
  
  sparkVersion: "3.5.3"
  
  arguments:
    - "--date"
    - "{{ ds }}"     # Templated by Airflow
    - "--env"
    - "production"
  
  driver:
    cores: 1
    memory: "2g"
    serviceAccount: spark
    labels:
      app: orders-pipeline
      component: driver
  
  executor:
    cores: 2
    instances: 3      # 3 executors × 2 cores = 6 parallel tasks
    memory: "4g"
    labels:
      app: orders-pipeline
      component: executor
  
  restartPolicy:
    type: OnFailure
    onFailureRetries: 3
    onFailureRetryInterval: 30
    onSubmissionFailureRetries: 2
  
  monitoring:
    exposeDriverMetrics: true
    exposeExecutorMetrics: true
    prometheus:
      jmxExporterJar: /prometheus/jmx_prometheus_javaagent.jar
```

---

## PHẦN 9: MONITORING & OBSERVABILITY STACK

### 9.1 Prometheus Configuration

```yaml
# monitoring/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - alerts.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

scrape_configs:
  # Airflow metrics
  - job_name: airflow
    static_configs:
      - targets: ["airflow-webserver:8080"]
    metrics_path: /admin/metrics

  # Flink metrics
  - job_name: flink
    static_configs:
      - targets: ["flink-jobmanager:9249"]

  # Application metrics (custom pipeline metrics)
  - job_name: pipeline-metrics
    static_configs:
      - targets: ["pipeline-app:8000"]
    metrics_path: /metrics

  # PostgreSQL metrics
  - job_name: postgres
    static_configs:
      - targets: ["postgres-exporter:9187"]

  # Node metrics (system resources)
  - job_name: node
    static_configs:
      - targets: ["node-exporter:9100"]
```

### 9.2 Pipeline Alerts

```yaml
# monitoring/alerts.yml

groups:
  - name: pipeline_alerts
    rules:
      # Pipeline didn't run
      - alert: PipelineMissedSLA
        expr: |
          time() - pipeline_last_success_timestamp{pipeline="orders_daily"} > 7200
        for: 15m
        labels:
          severity: critical
          team: data-platform
        annotations:
          summary: "Pipeline {{ $labels.pipeline }} missed SLA"
          description: |
            Pipeline {{ $labels.pipeline }} hasn't completed successfully
            in {{ $value | humanizeDuration }}.
            Expected: every 2 hours.

      # High failure rate
      - alert: PipelineHighFailureRate
        expr: |
          rate(pipeline_runs_total{status="failed"}[1h]) 
          / rate(pipeline_runs_total[1h]) > 0.3
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline failure rate > 30%"

      # Data quality degradation
      - alert: DataQualityDrop
        expr: pipeline_quality_score < 0.95
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Data quality score dropped below 95%"
          description: "Current score: {{ $value }}"

      # Pipeline duration spike
      - alert: PipelineSlow
        expr: |
          pipeline_duration_seconds > 
          pipeline_duration_seconds offset 7d * 2
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline running 2x slower than last week"
```

### 9.3 Custom Pipeline Metrics (Python)

```python
"""Expose pipeline metrics via Prometheus client."""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    start_http_server,
)

# ============================================================
# Define metrics
# ============================================================

# Counter: total pipeline runs
PIPELINE_RUNS = Counter(
    "pipeline_runs_total",
    "Total pipeline executions",
    ["pipeline", "status"],  # Labels
)

# Gauge: current value (last success timestamp)
PIPELINE_LAST_SUCCESS = Gauge(
    "pipeline_last_success_timestamp",
    "Timestamp of last successful run",
    ["pipeline"],
)

# Histogram: duration distribution
PIPELINE_DURATION = Histogram(
    "pipeline_duration_seconds",
    "Pipeline execution duration",
    ["pipeline", "step"],
    buckets=[10, 30, 60, 120, 300, 600, 1800, 3600],
)

# Gauge: data quality score
QUALITY_SCORE = Gauge(
    "pipeline_quality_score",
    "Data quality score (0-1)",
    ["pipeline", "check"],
)

# Counter: rows processed
ROWS_PROCESSED = Counter(
    "pipeline_rows_processed_total",
    "Total rows processed",
    ["pipeline", "stage"],
)


# ============================================================
# Usage in pipeline
# ============================================================

import time
from contextlib import contextmanager

@contextmanager
def track_pipeline_step(pipeline_name: str, step_name: str):
    """Context manager to track pipeline step metrics."""
    start = time.time()
    try:
        yield
        PIPELINE_RUNS.labels(pipeline=pipeline_name, status="success").inc()
    except Exception:
        PIPELINE_RUNS.labels(pipeline=pipeline_name, status="failed").inc()
        raise
    finally:
        duration = time.time() - start
        PIPELINE_DURATION.labels(
            pipeline=pipeline_name, step=step_name
        ).observe(duration)


# In pipeline code:
def run_orders_pipeline():
    with track_pipeline_step("orders_daily", "extract"):
        raw = extract_orders()
        ROWS_PROCESSED.labels(pipeline="orders_daily", stage="extract").inc(len(raw))
    
    with track_pipeline_step("orders_daily", "transform"):
        transformed = transform_orders(raw)
        ROWS_PROCESSED.labels(pipeline="orders_daily", stage="transform").inc(len(transformed))
    
    with track_pipeline_step("orders_daily", "load"):
        load_to_warehouse(transformed)
    
    PIPELINE_LAST_SUCCESS.labels(pipeline="orders_daily").set_to_current_time()
    QUALITY_SCORE.labels(pipeline="orders_daily", check="completeness").set(0.99)


# Start metrics server
if __name__ == "__main__":
    start_http_server(8000)  # Expose on :8000/metrics
    run_orders_pipeline()
```

---

## PHẦN 10: PRODUCTION READINESS CHECKLIST

### 10.1 The Checklist

```
╔══════════════════════════════════════════════════════════════╗
║            PRODUCTION READINESS CHECKLIST                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📦 CODE                                                     ║
║  □ All tests passing (unit + integration)                    ║
║  □ Code reviewed and approved                                ║
║  □ No hardcoded credentials or secrets                       ║
║  □ Type hints on all public functions                        ║
║  □ Linting clean (ruff + sqlfluff + mypy)                    ║
║  □ No TODO/FIXME/HACK in production code                     ║
║                                                              ║
║  🐳 INFRASTRUCTURE                                           ║
║  □ Docker images built and tested                            ║
║  □ Resource limits set (CPU, memory)                         ║
║  □ Health checks configured                                  ║
║  □ Persistent volumes for stateful services                  ║
║  □ Network policies configured                               ║
║  □ Auto-scaling rules defined                                ║
║                                                              ║
║  🔒 SECURITY                                                 ║
║  □ Secrets in secrets manager (not env vars)                 ║
║  □ Non-root user in Docker containers                        ║
║  □ Database connections encrypted (SSL)                      ║
║  □ PII handling compliant (masking, encryption)              ║
║  □ Network access restricted (security groups/firewalls)     ║
║  □ Dependency vulnerability scan passed                      ║
║                                                              ║
║  📊 OBSERVABILITY                                            ║
║  □ Structured logging configured (JSON to log aggregator)    ║
║  □ Metrics exposed (Prometheus/CloudWatch/Datadog)           ║
║  □ Dashboards created (pipeline health, data quality)        ║
║  □ Alerts configured (SLA breach, failure, quality drop)     ║
║  □ On-call rotation set up                                   ║
║  □ Runbook documented                                        ║
║                                                              ║
║  🔄 RELIABILITY                                              ║
║  □ Pipeline is idempotent (safe to re-run)                   ║
║  □ Retry logic with exponential backoff                      ║
║  □ Dead letter queue for failed records                      ║
║  □ Graceful shutdown handling                                ║
║  □ Backfill process documented and tested                    ║
║  □ Disaster recovery plan documented                         ║
║                                                              ║
║  📐 DATA QUALITY                                             ║
║  □ Schema validation at ingestion                            ║
║  □ Data quality checks (Great Expectations/dbt tests)        ║
║  □ Data freshness monitoring                                 ║
║  □ Anomaly detection for key metrics                         ║
║  □ Data lineage documented                                   ║
║                                                              ║
║  📄 DOCUMENTATION                                            ║
║  □ Architecture diagram up to date                           ║
║  □ Runbook for common operations                             ║
║  □ Incident response procedure documented                    ║
║  □ SLA defined and communicated                              ║
║  □ Downstream dependencies documented                        ║
║  □ Change log maintained                                     ║
║                                                              ║
║  🚀 DEPLOYMENT                                               ║
║  □ CI/CD pipeline configured                                 ║
║  □ Staging environment tested                                ║
║  □ Rollback procedure documented                             ║
║  □ Feature flags for risky changes                           ║
║  □ Blue/green or canary deployment ready                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## PHẦN 11: PROJECT TEMPLATES

### 11.1 Standard DE Project Structure

```
my-de-project/
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD pipeline
│
├── .vscode/
│   ├── extensions.json           # Recommended extensions
│   ├── settings.json             # Editor settings
│   └── launch.json               # Debug configurations
│
├── src/
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   │
│   ├── extractors/               # Data extraction
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract extractor
│   │   ├── postgres.py
│   │   ├── api.py
│   │   └── s3.py
│   │
│   ├── transformers/             # Data transformation
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract transformer
│   │   ├── orders.py
│   │   └── customers.py
│   │
│   ├── loaders/                  # Data loading
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract loader
│   │   ├── warehouse.py
│   │   └── s3.py
│   │
│   ├── validators/               # Data validation
│   │   ├── __init__.py
│   │   └── quality.py
│   │
│   └── utils/                    # Shared utilities
│       ├── __init__.py
│       ├── config.py             # Pydantic settings
│       ├── logging.py            # Structured logging setup
│       ├── metrics.py            # Prometheus metrics
│       └── retry.py              # Retry decorators
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures
│   ├── unit/
│   │   ├── test_transformers.py
│   │   └── test_validators.py
│   └── integration/
│       ├── test_extractors.py
│       └── test_pipeline.py
│
├── config/
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
│
├── scripts/
│   ├── seed_data.py
│   ├── setup_local.sh
│   └── run_backfill.py
│
├── monitoring/
│   ├── prometheus.yml
│   ├── alerts.yml
│   └── grafana/
│       └── dashboards/
│           └── pipeline-health.json
│
├── dbt_project/                  # If using dbt
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       └── marts/
│
├── docker-compose.yml            # Local development
├── Dockerfile                    # Production image
├── .dockerignore
│
├── pyproject.toml                # Dependencies + tool config
├── uv.lock                      # Locked dependencies
├── Makefile                      # Standard commands
│
├── .pre-commit-config.yaml       # Git hooks
├── .gitignore
├── .env.example                  # Template (not .env!)
│
├── CHANGELOG.md
├── LICENSE
└── README.md
```

### 11.2 .gitignore for DE Projects

```gitignore
# .gitignore for Data Engineering projects

# ============================================================
# Python
# ============================================================
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
.eggs/

# Virtual environments
.venv/
venv/
env/
ENV/

# Testing
.pytest_cache/
.coverage
htmlcov/
coverage.xml

# Type checking
.mypy_cache/

# Linting
.ruff_cache/

# ============================================================
# IDE
# ============================================================
.idea/
*.swp
*.swo
*~

# VS Code (keep settings, ignore personal)
# .vscode/        # Uncomment if NOT sharing settings
.vscode/launch.json  # Personal debug configs

# ============================================================
# Data files (NEVER commit data!)
# ============================================================
*.csv
*.tsv
*.parquet
*.avro
*.orc
*.json
!config/**/*.json
!.vscode/**/*.json
!package.json
data/
tmp/
temp/

# ============================================================
# Secrets & Environment
# ============================================================
.env
.env.local
.env.*.local
*.pem
*.key
*.p12
.secrets.baseline

# ============================================================
# Docker
# ============================================================
docker-compose.override.yml

# ============================================================
# dbt
# ============================================================
dbt_packages/
target/
logs/
dbt_modules/

# ============================================================
# Spark
# ============================================================
metastore_db/
derby.log
spark-warehouse/

# ============================================================
# Terraform
# ============================================================
.terraform/
*.tfstate
*.tfstate.*
*.tfplan

# ============================================================
# Jupyter Notebooks
# ============================================================
.ipynb_checkpoints/

# ============================================================
# OS
# ============================================================
.DS_Store
Thumbs.db
desktop.ini
```

### 11.3 .env.example

```bash
# .env.example — Copy to .env and fill in values
# NEVER commit .env to git!

# ============================================================
# Environment
# ============================================================
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# ============================================================
# Database (Source)
# ============================================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=production
DB_USER=dev
DB_PASSWORD=change_me

# ============================================================
# Data Warehouse
# ============================================================
DWH_HOST=localhost
DWH_PORT=5433
DWH_NAME=warehouse
DWH_USER=analytics
DWH_PASSWORD=change_me

# ============================================================
# Object Storage
# ============================================================
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=data-lake

# ============================================================
# Kafka
# ============================================================
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SCHEMA_REGISTRY_URL=http://localhost:8081

# ============================================================
# Redis
# ============================================================
REDIS_HOST=localhost
REDIS_PORT=6379

# ============================================================
# Monitoring
# ============================================================
SENTRY_DSN=
PROMETHEUS_PORT=8000

# ============================================================
# API Keys (from secrets manager in production)
# ============================================================
# API_KEY=your_api_key_here
```

---

## PHẦN 12: ENVIRONMENT MANAGEMENT

### 12.1 Dev / Staging / Production Strategy

```
╔══════════════════════════════════════════════════════════════╗
║              ENVIRONMENT STRATEGY                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  DEVELOPMENT (Local)                                         ║
║  ├── Purpose: Rapid iteration, debugging                     ║
║  ├── Data: Sample data (1000 rows), seed data                ║
║  ├── Infra: Docker Compose on laptop                         ║
║  ├── Secrets: .env file (local only)                         ║
║  ├── Deploy: Manual (make run-pipeline)                      ║
║  └── Cost: $0                                                ║
║                                                              ║
║  STAGING                                                     ║
║  ├── Purpose: Pre-production validation                      ║
║  ├── Data: Anonymized production subset (10%)                ║
║  ├── Infra: Cloud (same services, smaller instances)         ║
║  ├── Secrets: Cloud secrets manager                          ║
║  ├── Deploy: CI/CD on merge to develop branch                ║
║  └── Cost: ~20% of production                                ║
║                                                              ║
║  PRODUCTION                                                  ║
║  ├── Purpose: Live data processing                           ║
║  ├── Data: Full production data                              ║
║  ├── Infra: Cloud (auto-scaling, HA)                         ║
║  ├── Secrets: Cloud secrets manager + rotation               ║
║  ├── Deploy: CI/CD on merge to main (with approval)          ║
║  └── Cost: 100%                                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### 12.2 Config per Environment

```python
# src/utils/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    
    # Environment
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    
    # Database
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="analytics")
    db_user: str = Field(default="dev")
    db_password: str = Field(default="dev_password")
    
    # Feature flags per environment
    enable_data_quality_checks: bool = Field(default=True)
    enable_slack_notifications: bool = Field(default=False)
    sample_data_fraction: float = Field(default=1.0)
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Usage
settings = get_settings()

if settings.is_development:
    # Use sample data for faster iteration
    df = df.sample(frac=settings.sample_data_fraction)

if settings.enable_slack_notifications:
    send_slack_alert(...)
```

---

## PHẦN 13: SECURITY HARDENING

### 13.1 Docker Security

```dockerfile
# Security-hardened Dockerfile

# 1. Use specific version (not :latest)
FROM python:3.12.7-slim-bookworm

# 2. Don't run as root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 3. Don't store secrets in image layers
# ❌ BAD: COPY .env /app/.env
# ❌ BAD: ENV API_KEY=secret123
# ✅ GOOD: Mount secrets at runtime

# 4. Use COPY instead of ADD (ADD can untar/download URLs)
COPY requirements.txt .

# 5. Pin package versions
RUN pip install --no-cache-dir -r requirements.txt

# 6. Remove package manager cache
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 7. Read-only filesystem where possible
# docker run --read-only --tmpfs /tmp my-app

# 8. Set no-new-privileges
# docker run --security-opt=no-new-privileges my-app

USER appuser
```

### 13.2 Network Security

```yaml
# docker-compose.yml — Network isolation

services:
  app:
    networks:
      - frontend
      - backend
  
  postgres:
    networks:
      - backend    # NOT exposed to frontend!
    # No ports mapping = not accessible from host
  
  nginx:
    networks:
      - frontend
    ports:
      - "443:443"  # Only HTTPS exposed

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access!
```

### 13.3 Dependency Security Scanning

```yaml
# .github/workflows/security.yml

name: Security Scan

on:
  schedule:
    - cron: "0 6 * * 1"  # Weekly Monday 6 AM
  push:
    branches: [main]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Python dependency audit
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Audit dependencies
        run: uv pip audit
      
      # Docker image scan
      - name: Build Docker image
        run: docker build -t scan-target .
      
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: scan-target
          format: table
          severity: "CRITICAL,HIGH"
          exit-code: "1"
      
      # Secret detection
      - name: Detect secrets
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

---

## 📦 Verified Resources

**Package Management:**
- [astral-sh/uv](https://github.com/astral-sh/uv) — 36k⭐, extremely fast Python package manager
- [pyenv/pyenv](https://github.com/pyenv/pyenv) — 40k⭐, Python version management

**Docker:**
- [docker/compose](https://github.com/docker/compose) — Docker Compose v2
- [hadolint/hadolint](https://github.com/hadolint/hadolint) — 10k⭐, Dockerfile linter

**CI/CD:**
- [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) — GitHub Action for uv
- [pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) — 13k⭐, git hook framework

**Monitoring:**
- [prometheus/prometheus](https://github.com/prometheus/prometheus) — 57k⭐, metrics & alerting
- [grafana/grafana](https://github.com/grafana/grafana) — 66k⭐, dashboards & visualization

**Kubernetes:**
- [apache/airflow](https://github.com/apache/airflow) — 44k⭐, includes Helm chart
- [derailed/k9s](https://github.com/derailed/k9s) — 28k⭐, K8s TUI

**Shell & Productivity:**
- [fish-shell/fish-shell](https://github.com/fish-shell/fish-shell) — 27k⭐, friendly interactive shell
- [starship/starship](https://github.com/starship/starship) — 46k⭐, cross-shell prompt
- [jesseduffield/lazygit](https://github.com/jesseduffield/lazygit) — 55k⭐, Git TUI

---

## 🔗 Liên Kết

- [Clean Code for DE](15_Clean_Code_Data_Engineering.md) — Code standards & review
- [Testing & CI/CD](11_Testing_CICD.md) — Testing strategies
- [Python for DE](13_Python_Data_Engineering.md) — Python fundamentals (incl. UV)
- [Git & Version Control](14_Git_Version_Control.md) — Git workflows
- [Monitoring & Observability](12_Monitoring_Observability.md) — Metrics, alerting
- [Cloud Platforms](10_Cloud_Platforms.md) — AWS, GCP, Azure
- [Tools: Airflow](../tools/08_Apache_Airflow_Complete_Guide.md) — Orchestration

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Coverage: Local Dev, Docker, CI/CD, Terraform, K8s, Monitoring, Security, Templates*
