#!/bin/bash

# VocabMaster - Push to GitHub Script
# This script helps you push the project to GitHub

echo "========================================="
echo "VocabMaster - GitHub Deployment"
echo "========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Error: Git repository not initialized"
    exit 1
fi

echo "Step 1: Create GitHub repository"
echo "---------------------------------"
echo "Please create a new repository on GitHub:"
echo "  1. Visit: https://github.com/new"
echo "  2. Repository name: VocabMaster"
echo "  3. Description: AI-powered vocabulary learning application with spaced repetition"
echo "  4. Visibility: Public"
echo "  5. Do NOT initialize with README, .gitignore, or license"
echo "  6. Click 'Create repository'"
echo ""
read -p "Press Enter after creating the repository on GitHub..."

echo ""
echo "Step 2: Verify remote configuration"
echo "------------------------------------"
git remote -v

echo ""
echo "Step 3: Push to GitHub"
echo "----------------------"
echo "Pushing to: https://github.com/Barca0412/VocabMaster.git"
echo ""

# Attempt to push
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "SUCCESS! Repository pushed to GitHub"
    echo "========================================="
    echo ""
    echo "Your repository is now available at:"
    echo "https://github.com/Barca0412/VocabMaster"
    echo ""
    echo "Next steps:"
    echo "  1. Visit your repository on GitHub"
    echo "  2. Add repository description and topics"
    echo "  3. Verify all files are present"
    echo "  4. Check .env file is NOT visible (should be ignored)"
    echo ""
else
    echo ""
    echo "========================================="
    echo "PUSH FAILED"
    echo "========================================="
    echo ""
    echo "Possible solutions:"
    echo ""
    echo "1. Repository not created yet:"
    echo "   - Create the repository on GitHub first"
    echo "   - Make sure it's named 'VocabMaster'"
    echo ""
    echo "2. Authentication failed:"
    echo "   - Generate a Personal Access Token: https://github.com/settings/tokens"
    echo "   - Then run: git remote set-url origin https://YOUR_TOKEN@github.com/Barca0412/VocabMaster.git"
    echo "   - Try pushing again"
    echo ""
    echo "3. Using SSH instead:"
    echo "   - Run: git remote set-url origin git@github.com:Barca0412/VocabMaster.git"
    echo "   - Make sure SSH keys are configured"
    echo ""
    echo "For detailed instructions, see DEPLOYMENT.md"
fi
