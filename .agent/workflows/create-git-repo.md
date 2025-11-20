---
description: Steps to create a new Git repository
---

# Create New Git Repository

## Method 1: Create Local Repository First

### Step 1: Create and Navigate to Your Project Directory
```bash
mkdir my-project
cd my-project
```

### Step 2: Initialize Git Repository
```bash
git init
```

### Step 3: Create Initial Files
```bash
# Create a README file
echo "# My Project" > README.md

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store

# Logs
*.log
EOF
```

### Step 4: Make Initial Commit
```bash
git add .
git commit -m "Initial commit"
```

### Step 5: Create GitHub Repository and Push
```bash
# Set main as default branch
git branch -M main

# Create GitHub repo and push (using GitHub CLI)
gh repo create my-project --public --source=. --remote=origin --push
```

**OR** manually create on GitHub and push:
```bash
# Create repo on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/my-project.git
git push -u origin main
```

---

## Method 2: Create GitHub Repository First

### Step 1: Create Repository on GitHub
```bash
# Using GitHub CLI
gh repo create my-project --public --clone

# This creates the repo on GitHub and clones it locally
cd my-project
```

### Step 2: Add Your Files
```bash
# Add your project files
# Then commit and push
git add .
git commit -m "Initial commit"
git push
```

---

## Method 3: Clone Existing Repository
```bash
# Clone a repository
git clone https://github.com/USERNAME/REPO_NAME.git

# Navigate into it
cd REPO_NAME
```

---

## Prerequisites

### Install Git (if not installed)
```bash
# Check if Git is installed
git --version

# Install Git using Homebrew
brew install git
```

### Install GitHub CLI (optional but recommended)
```bash
# Install GitHub CLI
brew install gh

# Authenticate with GitHub
gh auth login
```

### Configure Git (first time only)
```bash
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

---

## Common Git Commands

### Check Status
```bash
git status
```

### Add Files
```bash
# Add specific file
git add filename.txt

# Add all files
git add .
```

### Commit Changes
```bash
git commit -m "Your commit message"
```

### Push Changes
```bash
git push
```

### Pull Latest Changes
```bash
git pull
```

### View Commit History
```bash
git log
```

### Create New Branch
```bash
git checkout -b feature-branch-name
```

### Switch Branches
```bash
git checkout main
```

---

## Quick Reference: Complete Workflow

```bash
# 1. Create directory
mkdir my-new-project && cd my-new-project

# 2. Initialize Git
git init

# 3. Create files
echo "# My New Project" > README.md

# 4. Add and commit
git add .
git commit -m "Initial commit"

# 5. Create GitHub repo and push
git branch -M main
gh repo create my-new-project --public --source=. --remote=origin --push
```

---

## Troubleshooting

### "gh: command not found"
```bash
brew install gh
gh auth login
```

### "Permission denied (publickey)"
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key and add to GitHub
cat ~/.ssh/id_ed25519.pub
# Go to GitHub.com → Settings → SSH Keys → Add new
```

### "remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/USERNAME/REPO.git
```
