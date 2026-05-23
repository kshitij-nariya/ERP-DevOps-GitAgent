from __future__ import annotations

import os
import tempfile
from pathlib import Path

import httpx
import git


def _read_changed_files(repo_dir: Path, changed_files: list[str]) -> dict[str, str]:
    contents = {}
    for filepath in changed_files:
        path = repo_dir / filepath
        if path.exists() and path.is_file() and path.stat().st_size < 500_000:
            contents[filepath] = path.read_text(encoding="utf-8", errors="ignore")
    return contents


def clone_and_diff(repo_url: str, head_sha: str = "HEAD", base_sha: str = "HEAD~1") -> dict:
    with tempfile.TemporaryDirectory(prefix="erp-devops-review-") as tmpdir:
        repo = git.Repo.clone_from(repo_url, tmpdir, depth=80)
        repo_dir = Path(tmpdir)

        try:
            changed_output = repo.git.diff(base_sha, head_sha, name_only=True)
            diff_content = repo.git.diff(base_sha, head_sha)
        except Exception:
            changed_output = repo.git.diff("HEAD~1", "HEAD", name_only=True)
            diff_content = repo.git.diff("HEAD~1", "HEAD")

        changed_files = [line.strip() for line in changed_output.splitlines() if line.strip()]
        file_contents = _read_changed_files(repo_dir, changed_files)
        return {
            "changed_files": changed_files,
            "diff_content": diff_content[:50_000],
            "file_contents": file_contents,
            "python_files": [path for path in changed_files if path.endswith(".py")],
            "xml_files": [path for path in changed_files if path.endswith(".xml")],
        }


def fetch_pull_request_files(repo_full_name: str, pr_number: int) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    changed_files: list[str] = []
    file_contents: dict[str, str] = {}
    diff_parts: list[str] = []

    with httpx.Client(timeout=30.0, headers=headers) as client:
        page = 1
        while True:
            response = client.get(
                f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files",
                params={"per_page": 100, "page": page},
            )
            response.raise_for_status()
            items = response.json()
            if not items:
                break

            for item in items:
                filename = item["filename"]
                changed_files.append(filename)
                patch = item.get("patch")
                if patch:
                    diff_parts.append(f"diff --git a/{filename} b/{filename}\n{patch}")

                raw_url = item.get("raw_url")
                if raw_url:
                    raw_response = client.get(raw_url)
                    if raw_response.status_code == 200 and len(raw_response.text) < 500_000:
                        file_contents[filename] = raw_response.text

            if len(items) < 100:
                break
            page += 1

    return {
        "changed_files": changed_files,
        "diff_content": "\n".join(diff_parts)[:50_000],
        "file_contents": file_contents,
        "python_files": [path for path in changed_files if path.endswith(".py")],
        "xml_files": [path for path in changed_files if path.endswith(".xml")],
    }


def get_pull_request_files_or_none(repo_full_name: str, pr_number: int) -> dict | None:
    try:
        return fetch_pull_request_files(repo_full_name, pr_number)
    except httpx.HTTPStatusError:
        return None
    except httpx.RequestError:
        return None


def analyze_local_path(path: str) -> dict:
    root = Path(path).expanduser()
    if not root.exists() and path.startswith("../demo"):
        docker_demo = Path("/app/demo") / path.removeprefix("../demo").lstrip("/")
        if docker_demo.exists():
            root = docker_demo
    root = root.resolve()
    if root.is_file():
        files = [root]
        base = root.parent
    else:
        files = [
            file
            for file in root.rglob("*")
            if file.is_file()
            and ".git" not in file.parts
            and file.suffix in {".py", ".xml", ".csv"}
            and file.stat().st_size < 500_000
        ]
        base = root

    changed_files = [str(file.relative_to(base)) for file in files]
    file_contents = {
        str(file.relative_to(base)): file.read_text(encoding="utf-8", errors="ignore")
        for file in files
    }
    diff_content = "\n".join(f"diff --git a/{name} b/{name}\n" + content for name, content in file_contents.items())
    return {
        "changed_files": changed_files,
        "diff_content": diff_content[:50_000],
        "file_contents": file_contents,
        "python_files": [path for path in changed_files if path.endswith(".py")],
        "xml_files": [path for path in changed_files if path.endswith(".xml")],
    }


def get_repo_data(
    repo_url: str,
    head_sha: str = "HEAD",
    base_sha: str = "HEAD~1",
    repo_full_name: str | None = None,
    pr_number: int = 0,
) -> dict:
    if pr_number > 0 and repo_full_name:
        pr_data = get_pull_request_files_or_none(repo_full_name, pr_number)
        if pr_data is not None and pr_data["changed_files"]:
            return pr_data
        return clone_and_diff(repo_url, head_sha, base_sha)
    if repo_url.startswith(("http://", "https://", "git@")):
        return clone_and_diff(repo_url, head_sha, base_sha)
    return analyze_local_path(repo_url)
