import requests
from config import Config


class GitHubService:
    def __init__(self):
        self.base_url = Config.GITHUB_API_URL
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }

        # Add authentication if available
        if Config.GITHUB_CLIENT_ID and Config.GITHUB_CLIENT_SECRET:
            self.headers['Authorization'] = f'token {Config.GITHUB_CLIENT_SECRET}'

    def get_user_repositories(self, username, per_page=30):
        """
        Fetch public repositories for a given GitHub username
        """
        try:
            url = f'{self.base_url}/users/{username}/repos'
            params = {
                'sort': 'updated',
                'per_page': per_page,
                'type': 'owner'
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            repos = response.json()

            # Extract relevant information
            return [
                {
                    'name': repo.get('name'),
                    'description': repo.get('description'),
                    'html_url': repo.get('html_url'),
                    'language': repo.get('language'),
                    'stars': repo.get('stargazers_count'),
                    'forks': repo.get('forks_count'),
                    'updated_at': repo.get('updated_at'),
                    'topics': repo.get('topics', [])
                }
                for repo in repos if not repo.get('fork', False)
            ]

        except requests.exceptions.RequestException:
            return []

    def get_repository_details(self, owner, repo):
        """
        Get detailed information about a specific repository
        """
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()

            return {
                'name': data.get('name'),
                'description': data.get('description'),
                'html_url': data.get('html_url'),
                'language': data.get('language'),
                'stars': data.get('stargazers_count'),
                'forks': data.get('forks_count'),
                'open_issues': data.get('open_issues_count'),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'topics': data.get('topics', []),
                'license': data.get('license', {}).get('name') if data.get('license') else None
            }

        except requests.exceptions.RequestException:
            return None

    def get_user_profile(self, username):
        """
        Get GitHub user profile information
        """
        try:
            url = f'{self.base_url}/users/{username}'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()

            return {
                'username': data.get('login'),
                'name': data.get('name'),
                'bio': data.get('bio'),
                'avatar_url': data.get('avatar_url'),
                'public_repos': data.get('public_repos'),
                'followers': data.get('followers'),
                'following': data.get('following'),
                'company': data.get('company'),
                'location': data.get('location'),
                'blog': data.get('blog'),
                'html_url': data.get('html_url')
            }

        except requests.exceptions.RequestException:
            return None

    def get_repository_languages(self, owner, repo):
        """
        Get programming languages used in a repository
        """
        try:
            url = f'{self.base_url}/repos/{owner}/{repo}/languages'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException:
            return {}
