import os
import json
from typing import Optional
from github import Github
from agno.tools import Toolkit, tool

class GithubTools(Toolkit):
    """
    Agno Toolkit for GitHub contributor and repository analysis using PyGithub.
    """
    def __init__(self):
        """
        Initialize with authentication from environment variable.
        Args:
            token_env_var: Name of the environment variable containing the GitHub token.
        """
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError(f"GitHub token not found in environment variable: {token}")
        self.github = Github(token)
        super().__init__(name="github_tools")
        self.register(self.get_repository)
        self.register(self.get_contributors_info)
        self.register(self.get_issues_info)
        self.register(self.get_issue_info)
        self.register(self.get_pull_requests_info)
        self.register(self.comment_on_pull_request)
        self.register(self.comment_on_issue)
        self.register(self.search_code)
        self.register(self.get_pull_request_info)
        self.register(self.get_pull_request_files)
        self.register(self.summarize_pull_request)
        self.register(self.add_label_to_issue)

    def get_repository(self, repo_path: str) -> str:
        """
        Fetch repository details for a given <owner>/<repo_name>.
        Args:
            repo_path: Repository path in format 'owner/repo'
        Returns:
            JSON-formatted string containing repository details
        """
        try:
            repo = self.github.get_repo(repo_path)
            repo_info = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "open_issues": repo.open_issues_count,
                "default_branch": repo.default_branch,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "license": repo.license.name if repo.license else None,
                "private": repo.private,
                "archived": repo.archived,
            }
            return json.dumps(repo_info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching repository {repo_path}: {str(e)}"
            }, indent=2)

    def get_contributors_info(self, repo_path: str) -> str:
        """
        Fetch detailed contributor information for a given <owner>/<repo_name>.
        Args:
            repo_path: Repository path in format 'owner/repo'
        Returns:
            JSON-formatted string containing a list of contributors and their details
        """
        try:
            repo = self.github.get_repo(repo_path)
            contributors = repo.get_contributors()
            contributors_info = []
            for contributor in contributors:
                info = {
                    "login": contributor.login,
                    "name": getattr(contributor, "name", None),
                    "email": getattr(contributor, "email", None),
                    "avatar_url": contributor.avatar_url,
                    "html_url": contributor.html_url,
                    "contributions": contributor.contributions,
                    "site_admin": getattr(contributor, "site_admin", False),
                }
                contributors_info.append(info)
            return json.dumps(contributors_info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching contributors for {repo_path}: {str(e)}"
            }, indent=2)

    def get_issues_info(self, repo_path: str, state: str = "open") -> str:
        """
        Fetch detailed issue information for a given <owner>/<repo_name>.
        Args:
            repo_path: Repository path in format 'owner/repo'
            state: Issue state - 'open', 'closed', or 'all' (default: 'open')
        Returns:
            JSON-formatted string containing a list of issues and their details
        """
        try:
            repo = self.github.get_repo(repo_path)
            issues = repo.get_issues(state=state)
            issues_info = []
            for issue in issues:
                if issue.pull_request is not None:
                    continue  # Skip pull requests
                info = {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "user": issue.user.login if issue.user else None,
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "labels": [label.name for label in issue.labels],
                    "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                    "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                    "html_url": issue.html_url,
                    "body": issue.body,
                }
                issues_info.append(info)
            return json.dumps(issues_info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching issues for {repo_path}: {str(e)}"
            }, indent=2)

    def get_issue_info(self, repo_path: str, issue_number: int) -> str:
        """
        Fetch detailed information for a specific issue by its number.
        Args:
            repo_path: Repository path in format 'owner/repo'
            issue_number: The number of the issue
        Returns:
            JSON-formatted string containing the issue's details
        """
        try:
            repo = self.github.get_repo(repo_path)
            issue = repo.get_issue(number=issue_number)
            if issue.pull_request is not None:
                return json.dumps({
                    "error": True,
                    "message": f"Issue #{issue_number} is a pull request, not an issue."
                }, indent=2)
            info = {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "user": issue.user.login if issue.user else None,
                "assignees": [assignee.login for assignee in issue.assignees],
                "labels": [label.name for label in issue.labels],
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                "html_url": issue.html_url,
                "body": issue.body,
            }
            return json.dumps(info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching issue #{issue_number} for {repo_path}: {str(e)}"
            }, indent=2)

    def get_pull_requests_info(self, repo_path: str, state: str = "open") -> str:
        """
        Fetch detailed pull request information for a given <owner>/<repo_name>.
        Args:
            repo_path: Repository path in format 'owner/repo'
            state: PR state - 'open', 'closed', or 'all' (default: 'open')
        Returns:
            JSON-formatted string containing a list of pull requests and their details
        """
        try:
            repo = self.github.get_repo(repo_path)
            pulls = repo.get_pulls(state=state)
            pulls_info = []
            for pr in pulls:
                info = {
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "user": pr.user.login if pr.user else None,
                    "assignees": [assignee.login for assignee in pr.assignees],
                    "labels": [label.name for label in pr.labels],
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                    "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                    "mergeable": pr.mergeable,
                    "merged": pr.merged,
                    "html_url": pr.html_url,
                    "body": pr.body,
                }
                pulls_info.append(info)
            return json.dumps(pulls_info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching pull requests for {repo_path}: {str(e)}"
            }, indent=2)

    def comment_on_pull_request(self, repo_path: str, pr_number: int, comment: str) -> str:
        """
        Add a comment to a pull request by its number.
        Args:
            repo_path: Repository path in format 'owner/repo'
            pr_number: The number of the pull request
            comment: The comment text to add
        Returns:
            JSON-formatted string with the comment URL or error message
        """
        try:
            repo = self.github.get_repo(repo_path)
            pr = repo.get_pull(pr_number)
            comment_obj = pr.create_issue_comment(comment)
            return json.dumps({
                "success": True,
                "comment_url": comment_obj.html_url
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error commenting on PR #{pr_number} for {repo_path}: {str(e)}"
            }, indent=2)

    def comment_on_issue(self, repo_path: str, issue_number: int, comment: str) -> str:
        """
        Add a comment to an issue by its number.
        Args:
            repo_path: Repository path in format 'owner/repo'
            issue_number: The number of the issue
            comment: The comment text to add
        Returns:
            JSON-formatted string with the comment URL or error message
        """
        try:
            repo = self.github.get_repo(repo_path)
            issue = repo.get_issue(number=issue_number)
            comment_obj = issue.create_comment(comment)
            return json.dumps({
                "success": True,
                "comment_url": comment_obj.html_url
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error commenting on issue #{issue_number} for {repo_path}: {str(e)}"
            }, indent=2)

    def search_code(self, repo_path: str, query: str) -> str:
        """
        Search the code in the specified repository using a query string.
        Args:
            repo_path: Repository path in format 'owner/repo'
            query: The search query string
        Returns:
            JSON-formatted string containing a list of matching code results
        """
        try:
            repo = self.github.get_repo(repo_path)
            results = self.github.search_code(f'{query} repo:{repo_path}')
            code_results = []
            for file in results:
                code_results.append({
                    "name": file.name,
                    "path": file.path,
                    "html_url": file.html_url,
                    "repository": file.repository.full_name,
                })
            return json.dumps(code_results, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error searching code in {repo_path}: {str(e)}"
            }, indent=2)

    def get_pull_request_info(self, repo_path: str, pr_number: int) -> str:
        """
        Get detailed information for a specific pull request by its number.
        Args:
            repo_path: Repository path in format 'owner/repo'
            pr_number: The number of the pull request
        Returns:
            JSON-formatted string containing the pull request's details
        """
        try:
            repo = self.github.get_repo(repo_path)
            pr = repo.get_pull(pr_number)
            info = {
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "user": pr.user.login if pr.user else None,
                "assignees": [assignee.login for assignee in pr.assignees],
                "labels": [label.name for label in pr.labels],
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
                "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                "mergeable": pr.mergeable,
                "merged": pr.merged,
                "html_url": pr.html_url,
                "body": pr.body,
            }
            return json.dumps(info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching pull request #{pr_number} for {repo_path}: {str(e)}"
            }, indent=2)

    def get_pull_request_files(self, repo_path: str, pr_number: int) -> str:
        """
        Get the list of files changed in a pull request by its number.
        Args:
            repo_path: Repository path in format 'owner/repo'
            pr_number: The number of the pull request
        Returns:
            JSON-formatted string containing a list of files changed in the pull request
        """
        try:
            repo = self.github.get_repo(repo_path)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()
            files_info = []
            for file in files:
                files_info.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "raw_url": file.raw_url,
                    "blob_url": file.blob_url,
                })
            return json.dumps(files_info, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error fetching files for pull request #{pr_number} in {repo_path}: {str(e)}"
            }, indent=2)

    def summarize_pull_request(self, repo_path: str, pr_number: int) -> str:
        """
        Summarize a pull request by its number (title, body, changed files, additions, deletions, etc.).
        Args:
            repo_path: Repository path in format 'owner/repo'
            pr_number: The number of the pull request
        Returns:
            JSON-formatted string containing a summary of the pull request
        """
        try:
            repo = self.github.get_repo(repo_path)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()
            files_summary = []
            total_additions = 0
            total_deletions = 0
            for file in files:
                files_summary.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                })
                total_additions += file.additions
                total_deletions += file.deletions
            summary = {
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "user": pr.user.login if pr.user else None,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
                "merged": pr.merged,
                "additions": total_additions,
                "deletions": total_deletions,
                "files_changed": len(files_summary),
                "files": files_summary,
                "body": pr.body,
                "html_url": pr.html_url,
            }
            return json.dumps(summary, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error summarizing pull request #{pr_number} for {repo_path}: {str(e)}"
            }, indent=2)

    def add_label_to_issue(self, repo_path: str, issue_number: int, label: str) -> str:
        """
        Add a label to an issue by its number.
        Args:
            repo_path: Repository path in format 'owner/repo'
            issue_number: The number of the issue
            label: The label to add
        Returns:
            JSON-formatted string with the updated labels or error message
        """
        try:
            repo = self.github.get_repo(repo_path)
            issue = repo.get_issue(number=issue_number)
            issue.add_to_labels(label)
            labels = [l.name for l in issue.labels]
            return json.dumps({
                "success": True,
                "labels": labels
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error adding label to issue #{issue_number} for {repo_path}: {str(e)}"
            }, indent=2) 