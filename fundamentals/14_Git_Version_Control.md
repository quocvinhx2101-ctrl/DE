# Git & Version Control - Complete Guide

## Version Control Best Practices cho Data Engineering Projects

---

## PHẦN 1: GIT FUNDAMENTALS

### 1.1 Git Là Gì?

Git là distributed version control system (DVCS) để:
- Track code changes over time
- Collaborate với team members
- Manage different versions of code
- Enable code review và quality control

**Tại sao quan trọng cho Data Engineering:**
- Track pipeline changes
- Collaborate on data transformations
- Rollback broken changes
- Audit trail cho compliance

### 1.2 Git Concepts

| git add |  |
|---|---|
| ----------------------> |  |
| git commit |  |
| -----------------------> |  |
| git push |  |
| --------------------> |  |
| git fetch |  |
| <-------------------- |  |
| git checkout |  |
| <---------------------- | ------------------------ |

### 1.3 Basic Git Commands

```bash
# SETUP

# Configure user info (required)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Configure default branch name
git config --global init.defaultBranch main

# Configure line endings (important for cross-platform)
git config --global core.autocrlf input  # Mac/Linux
git config --global core.autocrlf true   # Windows

# View configuration
git config --list


# STARTING A PROJECT

# Initialize new repository
git init

# Clone existing repository
git clone https://github.com/user/repo.git
git clone git@github.com:user/repo.git  # SSH


# BASIC WORKFLOW

# Check status
git status

# Stage changes
git add filename.py           # Single file
git add .                     # All changes
git add -p                    # Interactive staging

# Commit changes
git commit -m "Add feature X"
git commit -am "Quick commit" # Stage + commit tracked files

# View history
git log
git log --oneline            # Compact view
git log --graph              # Visual branch graph
git log -p                   # With diffs


# SYNCING

# Push to remote
git push origin main
git push -u origin feature   # Set upstream and push

# Fetch updates (download only)
git fetch origin

# Pull updates (fetch + merge)
git pull origin main
git pull --rebase origin main  # Rebase instead of merge
```

---

## PHẦN 2: BRANCHING STRATEGIES

### 2.1 Git Flow

```
GIT FLOW STRATEGY:

main (production)     ─────●─────────────────────●─────────────────
                           │                     │
                           │    release/v1.0     │
develop              ──●───●───●───●─────●───────●───●───●─────────
                       │       │         │               │
                       │       │         │               │
feature/login     ─────●───●───●         │               │
                                         │               │
feature/dashboard ───────────────────────●───●───●───────●

BRANCHES:
- main: Production-ready code
- develop: Integration branch
- feature/*: New features
- release/*: Prepare releases
- hotfix/*: Emergency fixes


WORKFLOW:

1. Create feature branch from develop
2. Work on feature
3. Merge feature to develop
4. Create release branch when ready
5. Test on release branch
6. Merge release to main + develop
7. Tag release on main
```

### 2.2 Trunk-Based Development

```
TRUNK-BASED DEVELOPMENT:

main (trunk)    ──●──●──●──●──●──●──●──●──●──●──●──●──
                      │              │         │
                      │              │         │
short-lived           ●──●           ●──●──●   ●──●
feature branches

PRINCIPLES:
- Single main branch
- Small, frequent commits
- Short-lived feature branches (< 2 days)
- Feature flags for incomplete work
- Continuous integration

BENEFITS:
- Simpler workflow
- Less merge conflicts
- Faster feedback
- Easier CI/CD
```

### 2.3 Branch Commands

```bash
# LIST BRANCHES

git branch               # Local branches
git branch -r            # Remote branches
git branch -a            # All branches


# CREATE BRANCH

git branch feature/new-etl         # Create branch
git checkout -b feature/new-etl    # Create and switch
git switch -c feature/new-etl      # Modern syntax


# SWITCH BRANCHES

git checkout main
git switch main          # Modern syntax


# DELETE BRANCH

git branch -d feature/old         # Delete merged
git branch -D feature/old         # Force delete
git push origin --delete feature  # Delete remote


# RENAME BRANCH

git branch -m old-name new-name
git branch -m new-name            # Rename current


# MERGE BRANCH

git checkout main
git merge feature/new-etl

# With commit message
git merge feature/new-etl -m "Merge new ETL feature"

# No fast-forward (preserve history)
git merge --no-ff feature/new-etl


# REBASE

git checkout feature
git rebase main

# Interactive rebase
git rebase -i main
# Options: pick, squash, reword, drop
```

---

## PHẦN 3: WORKING WITH REMOTES

### 3.1 Remote Commands

```bash
# VIEW REMOTES

git remote -v


# ADD REMOTE

git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git


# UPDATE REMOTE URL

git remote set-url origin https://github.com/user/new-repo.git


# FETCH AND PULL

git fetch origin              # Download updates
git fetch --all              # From all remotes

git pull origin main         # Fetch + merge
git pull --rebase            # Fetch + rebase


# PUSH

git push origin main
git push -u origin main      # Set upstream
git push --force-with-lease  # Force push (safer)
git push --tags              # Push tags


# PRUNE STALE BRANCHES

git fetch --prune
git remote prune origin
```

### 3.2 Collaboration Workflow

```
PULL REQUEST WORKFLOW:

1. Fork repository (if external contributor)
2. Clone to local
3. Create feature branch
4. Make changes, commit
5. Push to your remote
6. Create Pull Request
7. Code review
8. Address feedback
9. Merge


KEEPING FORK UPDATED:

# Add upstream remote
git remote add upstream https://github.com/original/repo.git

# Fetch upstream changes
git fetch upstream

# Merge upstream changes
git checkout main
git merge upstream/main

# Push to your fork
git push origin main


RESOLVING CONFLICTS:

# During merge
git merge feature
# If conflicts:
git status                    # See conflicting files
# Edit files to resolve
git add resolved-file.py
git commit                    # Complete merge

# During rebase
git rebase main
# If conflicts:
# Edit files to resolve
git add resolved-file.py
git rebase --continue
# Or abort
git rebase --abort
```

---

## PHẦN 4: ADVANCED GIT

### 4.1 Stashing

```bash
# SAVE WORK IN PROGRESS

git stash                    # Stash changes
git stash save "WIP: feature" # With message
git stash -u                 # Include untracked files


# LIST STASHES

git stash list


# APPLY STASH

git stash pop                # Apply and remove
git stash apply              # Apply and keep
git stash apply stash@{2}    # Apply specific


# VIEW STASH

git stash show               # Summary
git stash show -p            # Full diff


# DELETE STASH

git stash drop stash@{0}
git stash clear              # Delete all
```

### 4.2 Rewriting History

```bash
# AMEND LAST COMMIT

git commit --amend -m "New message"
git commit --amend --no-edit  # Add staged changes


# INTERACTIVE REBASE

git rebase -i HEAD~5          # Last 5 commits

# Commands:
# pick   = keep commit
# squash = combine with previous
# fixup  = combine, discard message
# reword = change message
# drop   = remove commit
# edit   = stop for amendments


# RESET COMMITS

git reset --soft HEAD~1       # Undo commit, keep staged
git reset --mixed HEAD~1      # Undo commit, unstage (default)
git reset --hard HEAD~1       # Undo commit, discard changes


# REVERT (safe, creates new commit)

git revert abc123             # Revert specific commit
git revert HEAD               # Revert last commit
git revert abc123..def456     # Revert range


# CHERRY-PICK

git cherry-pick abc123        # Apply specific commit
git cherry-pick abc123 def456 # Multiple commits
```

### 4.3 Git Bisect (Finding Bugs)

```bash
# START BISECT

git bisect start

# Mark current as bad
git bisect bad

# Mark known good commit
git bisect good abc123

# Git checks out middle commit
# Test and mark:
git bisect good    # If working
git bisect bad     # If broken

# Repeat until found
# Git will identify the breaking commit

# End bisect
git bisect reset


# AUTOMATED BISECT

git bisect start HEAD abc123
git bisect run python test_script.py
```

### 4.4 Git Hooks

```bash
# HOOKS LOCATION

.git/hooks/

# Common hooks:
# pre-commit     - Before commit
# commit-msg     - Validate commit message
# pre-push       - Before push
# post-merge     - After merge


# EXAMPLE: pre-commit hook

#!/bin/bash
# .git/hooks/pre-commit

# Run linting
echo "Running linting..."
flake8 src/
if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix errors."
    exit 1
fi

# Run tests
echo "Running tests..."
pytest tests/unit/
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix."
    exit 1
fi

echo "Pre-commit checks passed!"
exit 0


# Make executable
chmod +x .git/hooks/pre-commit
```

---

## PHẦN 5: GIT FOR DATA ENGINEERING

### 5.1 .gitignore for Data Projects

```gitignore
# .gitignore for Data Engineering Projects

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
*.so
.eggs/
*.egg-info/
dist/
build/

# Virtual environments
venv/
.venv/
env/
.conda/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Jupyter Notebooks
.ipynb_checkpoints/
*.ipynb  # Optional: exclude notebooks

# Data files (IMPORTANT)
*.csv
*.parquet
*.json
!config/*.json  # Keep config files
*.xlsx
*.db
*.sqlite

# Large files
*.zip
*.tar.gz
*.pkl
*.pickle

# Secrets and credentials
.env
.env.*
*.pem
*.key
secrets.yaml
credentials.json

# Logs
logs/
*.log

# Temporary files
tmp/
temp/
.cache/

# dbt specific
target/
dbt_packages/
logs/

# Airflow
airflow.db
airflow.cfg
logs/

# Spark
spark-warehouse/
metastore_db/
derby.log
```

### 5.2 Git LFS for Large Files

```bash
# INSTALL GIT LFS

# macOS
brew install git-lfs

# Ubuntu
sudo apt install git-lfs

# Initialize
git lfs install


# TRACK LARGE FILES

# Track file types
git lfs track "*.parquet"
git lfs track "*.pkl"
git lfs track "data/raw/*"

# This creates/updates .gitattributes
# Commit the .gitattributes file
git add .gitattributes
git commit -m "Configure Git LFS"


# VIEW TRACKED FILES

git lfs track


# PULL LFS FILES

git lfs pull


# CHECK LFS STATUS

git lfs status
git lfs ls-files
```

### 5.3 Commit Message Conventions

```
CONVENTIONAL COMMITS:

Format:
<type>(<scope>): <subject>

<body>

<footer>


TYPES:
- feat:     New feature
- fix:      Bug fix
- docs:     Documentation
- style:    Formatting (no code change)
- refactor: Code restructuring
- test:     Adding tests
- chore:    Maintenance tasks


EXAMPLES:

feat(etl): add incremental load for orders table

- Implement delta detection using updated_at column
- Add state management for last sync timestamp
- Include retry logic for failed batches

Closes #123


fix(pipeline): resolve null handling in customer transform

The customer transform was failing when address was null.
Added null check and default value handling.

Fixes #456


refactor(dbt): reorganize staging models

- Move staging models to separate directory
- Update ref() calls in downstream models
- Add model configs for materialization


DATA ENGINEERING SPECIFIC:

pipeline(orders): add new orders ingestion pipeline
model(dim_customer): add SCD type 2 tracking
schema(raw): add new columns for v2 API
migration(warehouse): partition orders table by date
quality(customers): add data validation rules
```

### 5.4 Managing Secrets

```bash
# NEVER COMMIT SECRETS

# Use .env files (gitignored)
# .env
DATABASE_URL=postgresql://user:pass@host/db
API_KEY=secret_key_here

# In code, use environment variables
import os
db_url = os.environ.get('DATABASE_URL')


# GIT-CRYPT (Encrypted files)

# Install
brew install git-crypt

# Initialize
git-crypt init

# Add GPG keys for team
git-crypt add-gpg-user USER_ID

# Mark files for encryption
# .gitattributes
secrets.yaml filter=git-crypt diff=git-crypt


# SOPS (Secrets management)

# Encrypt file
sops -e secrets.yaml > secrets.enc.yaml

# Decrypt file
sops -d secrets.enc.yaml > secrets.yaml

# Edit encrypted file
sops secrets.enc.yaml
```

---

## PHẦN 6: CI/CD WITH GIT

### 6.1 GitHub Actions

```yaml
# .github/workflows/ci.yml

name: Data Pipeline CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Lint
        run: |
          flake8 src/
          black --check src/
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
        run: |
          pytest tests/ -v --cov=src/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  dbt-test:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dbt
        run: pip install dbt-postgres
      
      - name: Run dbt tests
        env:
          DBT_PROFILES_DIR: ./dbt
        run: |
          cd dbt
          dbt deps
          dbt compile
          dbt test
```

### 6.2 GitLab CI

```yaml
# .gitlab-ci.yml

stages:
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/

test:
  stage: test
  image: python:3.10
  services:
    - postgres:14
  variables:
    POSTGRES_PASSWORD: postgres
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/test
  script:
    - pip install -r requirements.txt -r requirements-dev.txt
    - flake8 src/
    - pytest tests/ -v
  rules:
    - if: $CI_MERGE_REQUEST_ID
    - if: $CI_COMMIT_BRANCH == "main"

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy:
  stage: deploy
  script:
    - echo "Deploying to production..."
    - kubectl set image deployment/pipeline pipeline=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main
  when: manual
```

### 6.3 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort

  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 2.3.5
    hooks:
      - id: sqlfluff-lint
        args: ['--dialect', 'postgres']

# Install: pip install pre-commit
# Setup: pre-commit install
# Run all: pre-commit run --all-files
```

---

## PHẦN 7: BEST PRACTICES

### 7.1 Git Workflow Checklist

```
DAILY WORKFLOW:

□ Start day: git pull --rebase origin main
□ Create feature branch: git checkout -b feature/xyz
□ Make small, focused commits
□ Write clear commit messages
□ Push regularly: git push origin feature/xyz
□ Create PR when ready
□ Address review feedback
□ Squash/rebase before merge
□ Delete branch after merge


CODE REVIEW CHECKLIST:

□ Code compiles/runs
□ Tests pass
□ No hardcoded credentials
□ No large data files
□ Follows team conventions
□ Clear commit history
□ Documentation updated
□ Breaking changes noted
```

### 7.2 Repository Structure

```
data-pipeline/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── deploy.yml
│   └── CODEOWNERS
├── .gitignore
├── .gitattributes
├── .pre-commit-config.yaml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── src/
│   └── pipelines/
├── tests/
├── dbt/
├── airflow/
│   └── dags/
├── docker/
├── config/
├── docs/
└── requirements.txt
```

### 7.3 Common Issues & Solutions

```
PROBLEM: Accidentally committed secrets

SOLUTION:
1. Remove from history (if not pushed)
   git reset --soft HEAD~1
   # Remove secret, commit again

2. If pushed, rotate credentials immediately
3. Use BFG Repo-Cleaner or git filter-branch
   bfg --delete-files secrets.yaml
   git push --force


PROBLEM: Large files in history

SOLUTION:
# Find large files
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print $3, $4}' | \
  sort -rn | head -20

# Remove with BFG
bfg --strip-blobs-bigger-than 100M


PROBLEM: Merge conflicts

SOLUTION:
1. Communicate with team
2. Pull latest changes frequently
3. Keep branches short-lived
4. Use feature flags for long work
5. Rebase regularly: git rebase main


PROBLEM: Broken main branch

SOLUTION:
1. git revert <bad-commit>
2. Push fix immediately
3. Investigate root cause
4. Add tests to prevent regression
```

---

## PHẦN 8: TOOLS & INTEGRATIONS

### 8.1 Git GUIs

```
POPULAR GIT GUIS:

1. GitKraken
   - Cross-platform
   - Visual branch management
   - Built-in merge tool

2. Sourcetree
   - Free from Atlassian
   - Good for beginners
   - Bitbucket integration

3. GitHub Desktop
   - Simple interface
   - GitHub integration
   - Good for beginners

4. VS Code Git
   - Built-in
   - GitLens extension
   - Source control panel

5. Fork
   - Fast, native
   - macOS and Windows
   - Good diff viewer
```

### 8.2 Useful Git Aliases

```bash
# Add to ~/.gitconfig

[alias]
    # Short commands
    co = checkout
    br = branch
    ci = commit
    st = status
    
    # Logging
    lg = log --oneline --graph --all
    last = log -1 HEAD
    
    # Undo
    undo = reset --soft HEAD~1
    unstage = reset HEAD --
    
    # Cleanup
    cleanup = "!git branch --merged | grep -v '\\*\\|main\\|develop' | xargs -n 1 git branch -d"
    
    # Work in progress
    wip = "!git add -A && git commit -m 'WIP'"
    unwip = reset HEAD~1
    
    # Shortcuts
    amend = commit --amend --no-edit
    aliases = config --get-regexp alias
```

### 8.3 Git Statistics

```bash
# REPOSITORY STATISTICS

# Commits by author
git shortlog -sn

# Lines changed by author
git log --author="username" --oneline --numstat | \
  awk '{adds += $1; dels += $2} END {print "Added:", adds, "Deleted:", dels}'

# Most changed files
git log --pretty=format: --name-only | \
  sort | uniq -c | sort -rn | head -20

# Repository size
git count-objects -vH
```

---

## PHẦN 9: MONOREPO vs POLYREPO

### 9.1 Monorepo Strategy

**Monorepo** = một repository chứa tất cả projects/services.

**Ưu điểm:**
- Atomic cross-project changes
- Shared tooling và configuration
- Easier dependency management
- Unified CI/CD pipeline
- Better code discoverability

**Nhược điểm:**
- Repository size grows large
- Slower git operations
- Complex CI/CD configuration
- Access control challenges
- Build time increases

```
monorepo/
├── packages/
│   ├── ingestion/
│   │   ├── src/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── transformation/
│   │   ├── dbt_project/
│   │   │   ├── models/
│   │   │   └── tests/
│   │   └── pyproject.toml
│   ├── orchestration/
│   │   ├── dags/
│   │   └── pyproject.toml
│   └── shared-lib/
│       ├── src/
│       └── pyproject.toml
├── infrastructure/
│   ├── terraform/
│   └── docker/
├── .github/
│   └── workflows/
├── pyproject.toml          # Root config
└── pants.toml              # Build system
```

### 9.2 Polyrepo Strategy

**Polyrepo** = mỗi project/service có repository riêng.

**Ưu điểm:**
- Clear ownership per team
- Independent deployment
- Faster git operations
- Simple access control
- Independent versioning

**Nhược điểm:**
- Cross-repo changes are hard
- Dependency version conflicts
- Code duplication
- Discovery challenges

```
# Polyrepo structure

org/data-ingestion-service     # Repo 1
org/data-transformation-dbt    # Repo 2
org/data-orchestration         # Repo 3
org/data-shared-lib            # Repo 4
org/data-infrastructure        # Repo 5
org/data-ml-pipeline           # Repo 6
```

### 9.3 Monorepo Tooling

**Pants (Python-focused):**

```toml
# pants.toml
[GLOBAL]
pants_version = "2.19.0"
backend_packages = [
    "pants.backend.python",
    "pants.backend.python.lint.black",
    "pants.backend.python.lint.ruff",
    "pants.backend.python.typecheck.mypy",
]

[python]
interpreter_constraints = [">=3.10,<3.13"]
enable_resolves = true

[python.resolves]
ingestion = "packages/ingestion/lock.txt"
transformation = "packages/transformation/lock.txt"
```

```bash
# Pants commands for monorepo
pants test packages/ingestion::        # Test one package
pants test ::                          # Test everything
pants lint packages/::                 # Lint all packages
pants package packages/ingestion       # Build package

# Only test changed code
pants --changed-since=HEAD~1 test

# Show dependency graph
pants dependencies packages/ingestion
pants dependents packages/shared-lib
```

**Nx (General-purpose):**

```json
// nx.json
{
  "targetDefaults": {
    "test": {
      "dependsOn": ["^build"],
      "cache": true
    },
    "build": {
      "dependsOn": ["^build"],
      "cache": true
    }
  },
  "affected": {
    "defaultBase": "main"
  }
}
```

```bash
# Nx commands
npx nx affected:test              # Test only affected projects
npx nx affected:build             # Build only affected
npx nx graph                      # Visualize dependencies
npx nx run ingestion:test         # Run specific target
```

**Turborepo:**

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    }
  }
}
```

### 9.4 Sparse Checkout for Large Monorepos

```bash
# Clone only specific directories from large monorepo
git clone --filter=blob:none --sparse https://github.com/org/monorepo.git
cd monorepo

# Enable sparse checkout
git sparse-checkout init --cone

# Add only needed directories
git sparse-checkout set packages/ingestion packages/shared-lib

# List current sparse checkout paths
git sparse-checkout list

# Add more paths later
git sparse-checkout add infrastructure/terraform

# Disable sparse checkout (get everything)
git sparse-checkout disable
```

### 9.5 Git Subtree and Submodules

**Git Submodules (Reference to another repo):**

```bash
# Add submodule
git submodule add https://github.com/org/shared-lib.git libs/shared

# Clone repo with submodules
git clone --recurse-submodules https://github.com/org/main-repo.git

# Update submodules
git submodule update --remote --merge

# Remove submodule
git submodule deinit libs/shared
git rm libs/shared
rm -rf .git/modules/libs/shared
```

**Git Subtree (Embed another repo):**

```bash
# Add subtree
git subtree add --prefix=libs/shared \
    https://github.com/org/shared-lib.git main --squash

# Pull updates from subtree remote
git subtree pull --prefix=libs/shared \
    https://github.com/org/shared-lib.git main --squash

# Push changes back to subtree remote
git subtree push --prefix=libs/shared \
    https://github.com/org/shared-lib.git feature/update
```

| Feature | Submodules | Subtree |
|---------|-----------|---------|
| Complexity | Higher | Lower |
| History | Separate | Merged |
| Dependency | External clone | Self-contained |
| Updates | Manual sync | Pull/push |
| Best for | Libraries | Embedded code |

---

## PHẦN 10: GIT INTERNALS

### 10.1 Git Objects

Git lưu trữ tất cả dưới dạng 4 loại objects:

```
GIT OBJECT TYPES:

1. BLOB (Binary Large Object)
   - Stores file content
   - No filename, just content hash
   - SHA-1 hash based on content

2. TREE
   - Directory listing
   - Points to blobs and other trees
   - Contains: mode, type, hash, name

3. COMMIT
   - Points to root tree
   - Author, committer, message
   - Parent commit(s)
   - Timestamp

4. TAG (Annotated)
   - Points to a commit
   - Tagger info, message
   - Used for releases
```

```bash
# Explore git objects
git cat-file -t HEAD              # Show object type (commit)
git cat-file -p HEAD              # Show commit content
git cat-file -p HEAD^{tree}       # Show root tree

# Show blob content
git ls-tree HEAD                  # List tree entries
git cat-file -p <blob-hash>       # Show file content

# Count objects
git count-objects -v

# Show all objects
git rev-list --objects --all | head -20
```

### 10.2 Git Packfiles

```bash
# Git packs loose objects into packfiles for efficiency
# .git/objects/pack/ contains packfiles

# Manually trigger packing
git gc                            # Garbage collection + pack
git repack -a -d                  # Repack all objects

# Inspect packfile
git verify-pack -v .git/objects/pack/*.idx | head -20

# Packfile format:
#   .pack  - Contains compressed objects
#   .idx   - Index for fast lookups

# Find large objects in packfile
git verify-pack -v .git/objects/pack/*.idx | \
    sort -k 3 -n | tail -10
```

### 10.3 Reflog — Safety Net

```bash
# Reflog tracks ALL ref changes (even deleted commits)
git reflog                        # Show recent actions
git reflog show main              # Show main branch history

# Recover deleted branch
git branch recovered-branch HEAD@{5}

# Recover after hard reset
git reflog
# Find the commit before reset
git reset --hard HEAD@{2}

# Recover amended commit
git reflog
git checkout HEAD@{1} -- .       # Restore files

# Reflog expires after 90 days (default)
git config gc.reflogExpire 180.days.ago
git config gc.reflogExpireUnreachable 90.days.ago
```

### 10.4 Git Garbage Collection

```bash
# Automatic GC runs periodically
git gc --auto                     # Run if needed
git gc --aggressive               # Full optimization (slow)
git gc --prune=now                # Remove unreachable objects

# Check what would be pruned
git fsck --unreachable            # List unreachable objects
git fsck --lost-found             # Recover lost objects

# Configure auto GC
git config gc.auto 256            # Pack after 256 loose objects
git config gc.autoPackLimit 50    # Repack after 50 packfiles

# Pruning schedule
git config gc.pruneExpire 2.weeks.ago
```

### 10.5 Git Merge Internals

```
THREE-WAY MERGE:

       Base (common ancestor)
       /         \
      v           v
   Ours         Theirs
   (HEAD)       (branch)
      \           /
       v         v
      Merge Result

Git finds common ancestor, then:
1. If both sides unchanged from base → keep as-is
2. If one side changed → use changed version
3. If both sides changed differently → CONFLICT
```

```bash
# Show merge base
git merge-base main feature-branch

# Show three-way diff
git diff ...feature-branch        # Changes in feature vs common ancestor
git diff main...feature-branch    # Same thing

# Merge strategies
git merge -s recursive feature    # Default (recursive)
git merge -s ort feature          # Newer, faster (default in Git 2.34+)
git merge -s ours feature         # Keep ours, ignore theirs
git merge -s subtree feature      # For subtree merges

# Conflict resolution helpers
git checkout --ours -- file.py    # Keep our version
git checkout --theirs -- file.py  # Keep their version
git merge --abort                 # Abort merge entirely
```

### 10.6 Transfer Protocols

```bash
# Git supports multiple transfer protocols

# SSH (recommended for private repos)
git remote add origin git@github.com:org/repo.git
# Uses SSH keys for authentication

# HTTPS (simpler setup)
git remote add origin https://github.com/org/repo.git
# Uses tokens or credential manager

# Git protocol (fast, read-only)
git clone git://github.com/org/repo.git

# Local protocol
git clone /path/to/repo.git

# Check remote protocol
git remote -v

# Optimize transfer
git config pack.windowMemory 256m
git config pack.threads 4
```

---

## PHẦN 11: DATA VERSIONING

### 11.1 The Problem

```
Code vs Data versioning challenges:

CODE:
- Small files (KB-MB)
- Text-based (diffable)
- Git handles well
- Version = commit hash

DATA:
- Large files (GB-TB)
- Binary formats (Parquet, Avro)
- Git can't handle efficiently
- Need specialized tools

ARTIFACTS:
- Models (ML models)
- Configurations (schemas)
- Environment (Docker images)
- Need reproducibility
```

### 11.2 DVC (Data Version Control)

```bash
# Install DVC
pip install dvc dvc-s3

# Initialize DVC in git repo
cd my-project
dvc init

# Track large data files
dvc add data/raw/sales_2024.parquet
# Creates: data/raw/sales_2024.parquet.dvc (tracked by git)
# Adds:   data/raw/sales_2024.parquet to .gitignore

# Configure remote storage
dvc remote add -d myremote s3://my-bucket/dvc-store
dvc remote modify myremote profile my-aws-profile

# Push data to remote
dvc push

# Pull data from remote
dvc pull

# Commit DVC tracking files to git
git add data/raw/sales_2024.parquet.dvc .gitignore
git commit -m "Add sales data v1"
```

**DVC Pipelines:**

```yaml
# dvc.yaml - Define reproducible pipelines
stages:
  extract:
    cmd: python src/extract.py
    deps:
      - src/extract.py
      - config/sources.yaml
    outs:
      - data/raw/
    params:
      - extract.start_date
      - extract.end_date

  transform:
    cmd: python src/transform.py
    deps:
      - src/transform.py
      - data/raw/
    outs:
      - data/processed/
    plots:
      - reports/quality_metrics.json:
          x: date
          y: completeness

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/
    outs:
      - models/model.pkl
    metrics:
      - metrics.json:
          cache: false
```

```bash
# DVC pipeline commands
dvc repro                         # Reproduce pipeline
dvc repro transform               # Reproduce specific stage
dvc dag                           # Show pipeline DAG

# Compare experiments
dvc metrics diff                  # Compare metrics
dvc params diff                   # Compare parameters
dvc plots diff                    # Compare plots

# Experiments
dvc exp run                       # Run experiment
dvc exp show                      # Show all experiments
dvc exp diff exp-abc exp-def      # Compare experiments
```

### 11.3 LakeFS

```bash
# LakeFS - Git-like operations for data lakes
# Provides branching, commits, merges for object storage

# Install lakectl CLI
pip install lakefs-client

# Create repository
lakectl repo create lakefs://my-data-lake s3://my-bucket/data

# Create branch
lakectl branch create lakefs://my-data-lake/feature-new-schema \
    --source lakefs://my-data-lake/main

# Upload data to branch
lakectl fs upload lakefs://my-data-lake/feature-new-schema/raw/data.parquet \
    --source local/data.parquet

# Diff between branches
lakectl diff lakefs://my-data-lake/main lakefs://my-data-lake/feature-new-schema

# Commit changes
lakectl commit lakefs://my-data-lake/feature-new-schema \
    -m "Update schema for new source"

# Merge branch
lakectl merge lakefs://my-data-lake/feature-new-schema \
    lakefs://my-data-lake/main

# Rollback (revert to previous commit)
lakectl branch revert lakefs://my-data-lake/main \
    --commit <commit-id>
```

**LakeFS with Spark:**

```python
# Read from LakeFS branch
df = spark.read.parquet(
    "s3a://my-data-lake/feature-branch/raw/sales/"
)

# Write to LakeFS branch
df.write.mode("overwrite").parquet(
    "s3a://my-data-lake/feature-branch/processed/sales/"
)

# Use LakeFS hooks for quality checks
# pre-commit hook validates data before commit
```

### 11.4 Delta Lake Time Travel

```sql
-- Delta Lake built-in versioning

-- Read specific version
SELECT * FROM sales VERSION AS OF 5;
SELECT * FROM sales TIMESTAMP AS OF '2026-01-15';

-- Show history
DESCRIBE HISTORY sales;

-- Restore to previous version
RESTORE TABLE sales TO VERSION AS OF 3;

-- Time travel in Spark
df = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("/data/sales")

-- Compare versions
df_v1 = spark.read.format("delta").option("versionAsOf", 1).load(path)
df_v2 = spark.read.format("delta").option("versionAsOf", 5).load(path)
diff = df_v2.exceptAll(df_v1)
```

### 11.5 Apache Iceberg Time Travel

```sql
-- Iceberg snapshots
SELECT * FROM sales FOR SYSTEM_TIME AS OF '2026-01-15 10:00:00';

-- Read specific snapshot
SELECT * FROM sales FOR SYSTEM_VERSION AS OF 123456789;

-- List snapshots
SELECT * FROM my_catalog.my_db.sales.snapshots;

-- Rollback to snapshot
CALL my_catalog.system.rollback_to_snapshot('my_db.sales', 123456789);

-- Cherry-pick snapshot
CALL my_catalog.system.cherrypick_snapshot('my_db.sales', 987654321);
```

### 11.6 Comparison of Data Versioning Tools

| Feature | DVC | LakeFS | Delta Lake | Iceberg |
|---------|-----|--------|------------|---------|
| Scope | Files + Pipelines | Object Storage | Table Format | Table Format |
| Branching | Git-based | Native | N/A | N/A |
| Time Travel | Via git tags | Commits | Versions | Snapshots |
| Merge | Git merge | Native merge | N/A | N/A |
| Granularity | File-level | Object-level | Row-level | Row-level |
| Storage | Any remote | S3/GCS/ADLS | Same as data | Same as data |
| Best for | ML pipelines | Data lakes | Lakehouse tables | Lakehouse tables |
| Integration | Python, CLI | Spark, Presto | Spark, Flink | Spark, Trino |

---

## PHẦN 12: REAL-WORLD SCENARIOS

### 12.1 Repository Migration

```bash
# Migrate from one Git host to another (e.g., GitLab → GitHub)

# 1. Mirror clone (all branches, tags)
git clone --mirror https://gitlab.com/org/old-repo.git
cd old-repo.git

# 2. Push to new remote
git remote set-url origin https://github.com/org/new-repo.git
git push --mirror

# 3. Update team remotes
# Each team member:
git remote set-url origin https://github.com/org/new-repo.git
git fetch origin
```

### 12.2 Disaster Recovery

```bash
# SCENARIO: Accidentally pushed sensitive data

# 1. Remove from history (BFG Repo Cleaner - faster)
brew install bfg
bfg --delete-files passwords.yaml
bfg --replace-text expressions.txt    # Redact patterns

git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force --all
git push --force --tags

# 2. Rotate compromised credentials immediately
# 3. Notify security team
# 4. Enable secret scanning

# SCENARIO: Corrupted repository
# 1. Check integrity
git fsck --full

# 2. Recover from remote
git clone --mirror https://github.com/org/repo.git backup
cd backup
git fsck --full

# 3. If local-only corruption
git stash                          # Save work
git fetch origin
git reset --hard origin/main       # Reset to remote state
git stash pop                      # Restore work
```

### 12.3 Large Repository Optimization

```bash
# PROBLEM: Git operations slow on large repos

# 1. Shallow clone
git clone --depth 1 https://github.com/org/large-repo.git
git fetch --deepen=10              # Get more history gradually

# 2. Partial clone (blobless)
git clone --filter=blob:none https://github.com/org/repo.git
# Blobs downloaded on demand

# 3. Treeless clone
git clone --filter=tree:0 https://github.com/org/repo.git
# Even more aggressive — trees fetched on demand

# 4. Git maintenance
git maintenance start              # Enable background optimization
git maintenance run --task=gc      # Run specific task
git maintenance run --task=commit-graph
git maintenance run --task=prefetch

# 5. Commit graph for faster log
git commit-graph write --reachable
git config fetch.writeCommitGraph true

# 6. File system monitor (faster status)
git config core.fsmonitor true
git config core.untrackedcache true
```

### 12.4 Compliance and Auditing

```bash
# Git for compliance requirements (SOX, HIPAA, GDPR)

# 1. Signed commits (GPG)
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git commit -S -m "Signed commit for compliance"

# Verify signatures
git log --show-signature
git verify-commit HEAD

# 2. Protected branches
# GitHub: Settings → Branches → Branch protection rules
# - Require pull request reviews
# - Require status checks
# - Require signed commits
# - Restrict force pushes
# - Require linear history

# 3. Audit log queries
# Who changed this file and when?
git log --follow --diff-filter=M -- path/to/critical/file.py

# What was the state at a specific date?
git log --before="2026-01-15" --oneline -- path/to/file

# All changes by a specific author
git log --author="developer@company.com" --since="2025-01-01"

# Changes to sensitive paths
git log --all --oneline -- \
    '*/secrets/*' '*/credentials/*' '*.env'
```

### 12.5 Multi-Environment Configuration

```bash
# Managing configs across environments with Git

# Strategy: Branch per environment (NOT recommended)
# Better: Config files with environment-specific values

# Project structure:
# config/
# ├── base.yaml          # Shared config
# ├── dev.yaml           # Dev overrides
# ├── staging.yaml       # Staging overrides
# └── prod.yaml          # Prod overrides

# Use git-crypt for sensitive configs
brew install git-crypt

# Initialize git-crypt
git-crypt init

# Configure which files to encrypt
# .gitattributes
# config/prod.yaml filter=git-crypt diff=git-crypt
# config/staging.yaml filter=git-crypt diff=git-crypt
# secrets/** filter=git-crypt diff=git-crypt

# Add GPG keys of authorized users
git-crypt add-gpg-user DEVELOPER_GPG_KEY_ID

# Files encrypted in remote, decrypted locally
git-crypt status                   # Show encryption status
git-crypt lock                     # Encrypt all files
git-crypt unlock                   # Decrypt all files
```

---

## PHẦN 13: RESOURCES

### 13.1 Essential Reading

| Resource | Type | Level |
|----------|------|-------|
| Pro Git (Scott Chacon) | Book (free) | All |
| Git Internals | Book chapter | Advanced |
| Atlassian Git Tutorials | Web docs | Beginner-Mid |
| GitHub Skills | Interactive | Beginner |
| Learn Git Branching | Interactive | All |
| Oh Shit, Git!? | Quick ref | All |

### 13.2 Tools Ecosystem

| Tool | Purpose | Link |
|------|---------|------|
| GitHub | Hosting + CI/CD | github.com |
| GitLab | Hosting + DevOps | gitlab.com |
| Bitbucket | Hosting (Atlassian) | bitbucket.org |
| Gitea | Self-hosted | gitea.io |
| DVC | Data versioning | dvc.org |
| LakeFS | Data lake versioning | lakefs.io |
| pre-commit | Git hooks framework | pre-commit.com |
| BFG Repo Cleaner | History cleanup | rtyley.github.io/bfg-repo-cleaner |
| git-crypt | File encryption | github.com/AGWA/git-crypt |
| Pants | Monorepo build | pantsbuild.org |

### 13.3 Cheat Sheet

```bash
# === DAILY WORKFLOW ===
git status                     # Check status
git add -p                     # Stage interactively
git commit -m "type: message"  # Commit
git push origin feature        # Push

# === BRANCHING ===
git switch -c feature          # Create + switch
git switch main                # Switch to main
git merge feature              # Merge
git branch -d feature          # Delete merged

# === UNDO ===
git reset --soft HEAD~1        # Undo commit, keep changes
git reset --hard HEAD~1        # Undo commit, discard changes
git revert HEAD                # Create undo commit
git checkout -- file.py        # Discard file changes
git restore --staged file.py   # Unstage file

# === INVESTIGATE ===
git log --oneline --graph      # Visual history
git blame file.py              # Who changed each line
git bisect start               # Find bug introduction
git diff main..feature         # Compare branches

# === CLEANUP ===
git fetch --prune              # Remove deleted remote refs
git branch --merged | xargs git branch -d  # Delete merged
git gc                         # Garbage collect
```

---

*Document Version: 2.0*
*Last Updated: February 2026*
*Coverage: Git fundamentals, branching, collaboration, CI/CD, monorepo, internals, data versioning, real-world scenarios*
