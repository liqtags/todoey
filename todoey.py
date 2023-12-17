import requests
import re
import base64
import os
import json


def update_pr_description(owner, repo, pr_number, new_description, github_token):
    """
    Updates the description of a PR
    :param owner: The owner of the repo
    :param repo: The repo name
    :param pr_number: The PR number
    :param new_description: The new description
    :param github_token: The github token
    :return: The status code of the request
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"token {github_token}"}
    data = {"body": new_description}
    response = requests.patch(url, headers=headers, json=data)
    return response.status_code


def add_comment_to_pr(owner, repo, pr_number, comment, github_token):
    """
    Adds a comment to a PR
    :param owner: The owner of the repo
    :param repo: The repo name
    :param pr_number: The PR number
    :param comment: The comment
    :param github_token: The github token
    :return: The status code of the request
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"token {github_token}"}
    data = {"body": comment}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code


def get_pr_changes(owner, repo, pr_number, github_token):
    """
    Gets the changes of a PR (files changed) not including removed files
    :param owner: The owner of the repo
    :param repo: The repo name
    :param pr_number: The PR number
    :param github_token: The github token
    :return: The changes of the PR
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(url, headers=headers)
    files = response.json()
    # to me the below oneliner is magic and is beautiful
    files_with_removed = [
        file["filename"] for file in files if file["status"] != "removed"
    ]
    return files_with_removed


def extract_todos(file_path, github_token, owner, repo, pr_number, branch):
    """
    Extracts the todos from a file
    :param file_path: The file path
    :param github_token: The github token
    :param owner: The owner of the repo
    :param repo: The repo name
    :param pr_number: The PR number
    :param branch: The branch name
    :return: The todos in a array
    """
    fileData = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}",
        headers={"Authorization": f"token {github_token}"},
    )
    response = fileData.json()
    content = base64.b64decode(response["content"]).decode("utf-8")
    todo_pattern = re.compile(r"# TODO!: (.+?)(?:$|\n)", re.MULTILINE)
    todos = []

    for match in todo_pattern.finditer(content):
        todo = {
            "content": match.group(1).strip(),
            "line_number": content.count("\n", 0, match.start()) + 1,
        }
        todo[
            "link"
        ] = f'https://github.com/{owner}/{repo}/blob/{branch}/{file_path.replace("/", "-")}#L{todo["line_number"]}'
        todos.append(todo)

    return todos

def init_todey(github_user, pr_number, repo, token, branch):
    """
    The init_todey handles the main logic of the script
    :param github_user: The github user
    :param pr_number: The PR number
    :param repo: The repo name
    :param token: The github token
    :param branch: The branch name
    :return: None
    """
    owner = github_user
    github_token = token
    changes = get_pr_changes(owner, repo, pr_number, github_token)

    # if changes is empty array, then return
    if not changes:
        print("No changes in the PR")
        return

    new_description = "Here are the extracted TODO from the changed files:\n\n"
    for file_path in changes:
        todos = extract_todos(file_path, github_token, owner, repo, pr_number, branch)
        if todos:
            new_description += f"\n#### {file_path}:\n"
            for todo in todos:
                todoContent = todo["content"]
                todoLink = todo["link"]
                line_number = todo["line_number"]
                markdownLink = f"[Line: {line_number}]({todoLink})"
                new_description += f"- {todoContent} - {markdownLink}\n"

    update_comment = add_comment_to_pr(owner, repo, pr_number, new_description, github_token)

    if update_comment == 201:
        print(f"PR comment added successfully.")
    else:
        print(f"Failed to add PR comment. Status code: {update_comment}")

if __name__ == "__main__":
    """
    This is the main function that is called when the script is run
    """
    pr_number = os.environ.get("PR_NUMBER", 2)
    github_user = os.environ.get("GITHUB_USER", "0xlino")
    repo = os.environ.get("REPO", "todo_idea_py")
    repo = repo.split("/")[1]
    token = os.environ.get("TOKEN", "")
    branch = os.environ.get("BRANCH", "main")

    init_todey(github_user, pr_number, repo, token, branch)
