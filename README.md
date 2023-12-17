# GitHub TODOs Extractor aka Todoey

This script is designed to extract TODO comments from the changed files in a GitHub pull request (PR) and add a summary as a comment on the PR itself. It utilizes GitHub Actions to automatically trigger the workflow when a pull request is opened, synchronized, or reopened.

## Prerequisites

Before using the script, ensure you have the following:

-   GitHub account
-   Personal access token with the necessary permissions (generate one [here](https://github.com/settings/tokens))
-   Python installed on your machine

## GitHub Actions Workflow

The script is integrated with GitHub Actions using the following workflow:

```yaml
name: Todoey

on:
  pull_request: 
    types: [opened, synchronize, reopened]
  workflow_dispatch:

jobs:
  cinco:
    name: Analyze PR
    runs-on: ubuntu-latest
    steps:
      - name: check it out
        uses: actions/checkout@v2
        
      - name: Set up Python 3.8
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
          cache: pip
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Run Scraper
        env: 
          GITHUB_TOKEN: ${{ secrets.TOKEN }}
          PR_NUMBER: ${{ github.event.number }}
          GITHUB_USER: ${{ github.actor }}
          REPO: ${{ github.repository }}
          BRANCH: ${{ github.event.pull_request.head.ref }}
        run: |
          python todoey.py
```

This workflow is triggered on pull request events (opened, synchronized, reopened) and can also be manually triggered using the GitHub Actions web interface (`workflow_dispatch`). It sets up the necessary environment, installs dependencies, and runs the `todoey.py` script.

## Environment Variables

Before running the script, make sure to set the following environment variables:

-   `PR_NUMBER`: The number of the pull request.
-   `GITHUB_USER`: Your GitHub username.
-   `REPO`: The repository in the format `owner/repo`.
-   `TOKEN`: Your GitHub personal access token.
-   `BRANCH`: The name of the branch associated with the pull request.

## Usage

### Run the Script Locally

Execute the script with:
```bash
python todoey.py
```

### Run the GitHub Actions Workflow
Create or update a pull request to trigger the workflow automatically.