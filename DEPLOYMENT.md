# Deployment Instructions

## Creating GitHub Repository

The repository needs to be created on GitHub before pushing. Follow these steps:

### Option 1: Using GitHub CLI (if installed)

```bash
# Check if gh is installed
which gh

# If installed, create the repository
cd /Users/barca/Dev/some_ideas/word_recite
gh repo create VocabMaster --public --source=. --remote=origin --push
```

### Option 2: Manual Creation via GitHub Website

1. Visit https://github.com/new
2. Set repository name: `VocabMaster`
3. Set description: `AI-powered vocabulary learning application with spaced repetition`
4. Choose visibility: `Public`
5. Do NOT initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

Then push from command line:

```bash
cd /Users/barca/Dev/some_ideas/word_recite
git remote set-url origin https://github.com/Barca0412/VocabMaster.git
git push -u origin main
```

### Option 3: Using Personal Access Token

If you encounter authentication issues:

1. Generate a Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control)
   - Copy the generated token

2. Push using token:

```bash
cd /Users/barca/Dev/some_ideas/word_recite
git remote set-url origin https://YOUR_TOKEN@github.com/Barca0412/VocabMaster.git
git push -u origin main
```

Replace `YOUR_TOKEN` with the actual token.

## Post-Deployment Checklist

After successfully pushing to GitHub:

1. Verify all files are present in the repository
2. Check .gitignore is working (no .env file should be visible)
3. Add repository description and topics on GitHub:
   - Description: "AI-powered vocabulary learning application with spaced repetition"
   - Topics: `vocabulary`, `learning`, `spaced-repetition`, `ai`, `python`, `pyqt6`, `education`

4. Enable GitHub Pages for documentation (optional):
   - Settings > Pages
   - Source: Deploy from branch
   - Branch: main, /docs folder

5. Configure repository settings:
   - Enable Issues
   - Enable Wiki (optional)
   - Add README badges (optional)

## Repository Structure Summary

```
VocabMaster/
├── .env.example              # API configuration template
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
├── README.md                # Main documentation
├── requirements.txt         # Python dependencies
├── main.py                  # Application entry point
├── run.sh                   # Startup script
├── data/
│   ├── .gitkeep            # Preserve directory structure
│   ├── builtin_cet4.txt    # CET-4 vocabulary
│   └── builtin_cet6.txt    # CET-6 vocabulary
├── docs/
│   ├── FEATURES_v3.md      # Feature documentation
│   ├── LLM_INTEGRATION.md  # AI integration guide
│   └── SPACED_REPETITION_DESIGN.md
├── src/
│   ├── core/               # Business logic
│   │   ├── config.py
│   │   ├── word_manager.py
│   │   ├── dictionary.py
│   │   ├── spaced_repetition.py
│   │   ├── learning_tracker.py
│   │   └── llm_generator.py
│   └── ui/                 # User interface
│       ├── main_window.py
│       ├── settings_window_new.py
│       ├── quiz_window.py
│       ├── report_window.py
│       └── themes.py
└── DEPLOYMENT.md           # This file
```

## Verification Commands

After pushing, verify the repository:

```bash
# Check remote configuration
git remote -v

# View commit history
git log --oneline

# Check current status
git status

# Verify all branches
git branch -a
```

## Troubleshooting

### Authentication Failed

If you see "Authentication failed":

1. Use Personal Access Token instead of password
2. Or configure SSH keys (see GitHub documentation)

### Permission Denied

If you see "Permission denied":

1. Verify you're logged into the correct GitHub account
2. Check repository ownership
3. Ensure you have write access to the repository

### Repository Not Found

If you see "Repository not found":

1. Create the repository on GitHub first
2. Verify the repository name is correct
3. Check the URL in git remote configuration

## Next Steps

After successful deployment:

1. Share the repository URL: https://github.com/Barca0412/VocabMaster
2. Add a screenshot to README (capture main window)
3. Create releases/tags for version management
4. Set up GitHub Actions for CI/CD (optional)
5. Add contribution guidelines (optional)
