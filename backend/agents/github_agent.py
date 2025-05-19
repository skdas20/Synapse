from github import Github, UnknownObjectException
from typing import List, Dict

class GitHubAgent:
    def __init__(self, access_token: str = None):
        if not access_token:
            raise ValueError("GitHub token is required but was not provided. Please check your .env file.")
        self.github = Github(access_token)

    async def create_repository(self, repo_name: str, description: str = "") -> str:
        """Creates a new repository or returns the URL if it already exists"""
        user = self.github.get_user()
        try:
            # Try to get the repository first
            repo = user.get_repo(repo_name)
            print(f"Repository '{repo_name}' already exists. Using existing repository.")
            return repo.html_url
        except UnknownObjectException:
            # Repository does not exist, so create it
            print(f"Repository '{repo_name}' not found. Creating new repository.")
            try:
                repo = user.create_repo(
                    name=repo_name,
                    description=description,
                    private=False,  # Default to public, can be parameterized
                    auto_init=True  # Initialize with a README
                )
                return repo.html_url
            except Exception as e_create:
                # Catch specific exceptions from create_repo if necessary
                raise Exception(f"Failed to create repository '{repo_name}': {str(e_create)}")
        except Exception as e_get:
            # Catch other potential errors during get_repo
            raise Exception(f"Failed to check or create repository '{repo_name}': {str(e_get)}")

    async def push_files(self, repo_name: str, files: Dict[str, str]) -> None:
        """Pushes files to the repository"""
        try:
            user = self.github.get_user()
            repo = user.get_repo(repo_name)
            
            for file_path, content in files.items():
                try:
                    # Try to get existing file to update it
                    file = repo.get_contents(file_path)
                    repo.update_file(
                        path=file_path,
                        message=f"Update {file_path}",
                        content=content,
                        sha=file.sha
                    )
                except:
                    # File doesn't exist, create it
                    repo.create_file(
                        path=file_path,
                        message=f"Add {file_path}",
                        content=content
                    )
        except Exception as e:
            raise Exception(f"Failed to push files: {str(e)}")

    async def create_issues(self, repo_name: str, tasks: List[str]) -> None:
        """Creates GitHub issues from tasks"""
        try:
            user = self.github.get_user()
            repo = user.get_repo(repo_name)
            
            for task in tasks:
                repo.create_issue(
                    title=task,
                    body=f"Task from Synapse:\n{task}",
                    labels=['synapse-generated']
                )
        except Exception as e:
            raise Exception(f"Failed to create issues: {str(e)}")
