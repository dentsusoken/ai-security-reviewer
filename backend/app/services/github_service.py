"""GitHub repository fetch service."""

import base64
import re
from dataclasses import dataclass

import httpx


@dataclass
class CodeFile:
    """Represents a code file from repository."""

    path: str
    content: str
    size: int
    language: str


@dataclass
class RepoInfo:
    """Repository metadata."""

    owner: str
    repo: str
    branch: str
    default_branch: str
    description: str | None
    file_count: int


# Supported file extensions for security review
SUPPORTED_EXTENSIONS = {
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".py": "python",
    ".java": "java",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".rs": "rust",
}

# Files to skip (too large or not useful for security review)
SKIP_PATTERNS = [
    r"node_modules/",
    r"vendor/",
    r"\.min\.js$",
    r"\.bundle\.js$",
    r"dist/",
    r"build/",
    r"__pycache__/",
    r"\.pyc$",
    r"test/",
    r"tests/",
    r"spec/",
    r"\.test\.",
    r"\.spec\.",
]

# Size limits
MAX_FILE_SIZE = 50 * 1024  # 50KB per file
MAX_FILES = 10  # Maximum files to analyze


class GitHubService:
    """Service for fetching code from GitHub repositories."""

    def __init__(self, token: str | None = None):
        """Initialize with optional GitHub token for higher rate limits."""
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Security-Reviewer/1.0",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def parse_github_url(self, url: str) -> tuple[str, str, str | None]:
        """Parse GitHub URL to extract owner, repo, and optional branch.

        Supports:
        - https://github.com/owner/repo
        - https://github.com/owner/repo/tree/branch
        - github.com/owner/repo
        """
        # Remove trailing slashes and .git suffix
        url = url.rstrip("/").removesuffix(".git")

        # Extract owner/repo from URL
        patterns = [
            r"github\.com[:/]([^/]+)/([^/]+)(?:/tree/([^/]+))?",
            r"^([^/]+)/([^/]+)$",  # Simple owner/repo format
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2)
                branch = match.group(3) if len(match.groups()) > 2 else None
                return owner, repo, branch

        raise ValueError(f"Invalid GitHub URL format: {url}")

    async def get_repo_info(self, owner: str, repo: str) -> dict:
        """Get repository metadata."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_file_tree(self, owner: str, repo: str, branch: str) -> list[dict]:
        """Get recursive file tree for a branch."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}",
                params={"recursive": "1"},
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("tree", [])

    async def get_file_content(self, owner: str, repo: str, path: str, branch: str) -> str:
        """Get decoded content of a single file."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": branch},
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8")
            else:
                content = data.get("content", "")

            return content

    def _should_skip_file(self, path: str) -> bool:
        """Check if file should be skipped based on patterns."""
        for pattern in SKIP_PATTERNS:
            if re.search(pattern, path):
                return True
        return False

    def _get_file_extension(self, path: str) -> str | None:
        """Get file extension if supported."""
        for ext in SUPPORTED_EXTENSIONS:
            if path.endswith(ext):
                return ext
        return None

    async def fetch_repository_files(  # noqa: C901
        self,
        url: str,
        progress_callback=None,
    ) -> tuple[RepoInfo, list[CodeFile]]:
        """Fetch code files from a GitHub repository.

        Args:
            url: GitHub repository URL
            progress_callback: Optional async callback for progress updates

        Returns:
            Tuple of (RepoInfo, list of CodeFile)
        """
        # Parse URL
        owner, repo, branch = self.parse_github_url(url)

        if progress_callback:
            await progress_callback(
                "fetching_repo", {"message": f"リポジトリ情報を取得中: {owner}/{repo}"}
            )

        # Get repo info
        repo_data = await self.get_repo_info(owner, repo)
        default_branch = repo_data.get("default_branch", "main")
        branch = branch or default_branch

        if progress_callback:
            await progress_callback(
                "fetching_tree", {"message": f"ファイルツリーを取得中 (branch: {branch})"}
            )

        # Get file tree
        tree = await self.get_file_tree(owner, repo, branch)

        # Filter to supported code files
        code_files_info = []
        for item in tree:
            if item["type"] != "blob":
                continue

            path = item["path"]
            size = item.get("size", 0)

            # Skip if matches skip patterns
            if self._should_skip_file(path):
                continue

            # Check extension
            ext = self._get_file_extension(path)
            if not ext:
                continue

            # Check size
            if size > MAX_FILE_SIZE:
                continue

            code_files_info.append(
                {
                    "path": path,
                    "size": size,
                    "language": SUPPORTED_EXTENSIONS[ext],
                }
            )

        # Sort by size (smaller first) and limit
        code_files_info.sort(key=lambda x: x["size"])
        code_files_info = code_files_info[:MAX_FILES]

        if progress_callback:
            await progress_callback(
                "files_found",
                {
                    "message": f"{len(code_files_info)} 件のコードファイルを検出",
                    "file_count": len(code_files_info),
                },
            )

        # Fetch file contents
        code_files = []
        for i, file_info in enumerate(code_files_info):
            if progress_callback:
                await progress_callback(
                    "fetching_file",
                    {
                        "message": f"ファイル取得中: {file_info['path']} ({i + 1}/{len(code_files_info)})",
                        "current": i + 1,
                        "total": len(code_files_info),
                    },
                )

            try:
                content = await self.get_file_content(owner, repo, file_info["path"], branch)
                code_files.append(
                    CodeFile(
                        path=file_info["path"],
                        content=content,
                        size=file_info["size"],
                        language=file_info["language"],
                    )
                )
            except Exception as e:
                # Skip files that can't be fetched
                print(f"Warning: Could not fetch {file_info['path']}: {e}")
                continue

        repo_info = RepoInfo(
            owner=owner,
            repo=repo,
            branch=branch,
            default_branch=default_branch,
            description=repo_data.get("description"),
            file_count=len(code_files),
        )

        if progress_callback:
            await progress_callback(
                "files_fetched",
                {
                    "message": f"コード取得完了: {len(code_files)} ファイル",
                    "file_count": len(code_files),
                },
            )

        return repo_info, code_files
