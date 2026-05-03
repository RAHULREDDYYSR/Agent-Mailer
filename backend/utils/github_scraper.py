"""
GitHub README scraper utility.

Uses the GitHub REST API (no browser/HTML scraping needed) to:
  1. List all public, non-forked repos for a given GitHub profile URL.
  2. Fetch the raw README.md content for each repo (base64-decoded).
  3. Return structured data ready for LLM summarisation.

Rate limits:
  - Unauthenticated: 60 requests / hour
  - Authenticated (GITHUB_TOKEN): 5,000 requests / hour
Set GITHUB_TOKEN in .env to avoid hitting the unauthenticated limit.
"""

import asyncio
import base64
import os
import logging
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
README_MAX_CHARS = 6000  # Trim README before sending to LLM to keep context lean


def _build_headers() -> dict:
    """Build GitHub API request headers, injecting token if available."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _extract_username(github_url: str) -> str:
    """Extract GitHub username from a profile URL or bare username string."""
    cleaned = github_url.strip().rstrip("/")
    # Handles: https://github.com/username  OR  github.com/username  OR  username
    parts = cleaned.split("/")
    return parts[-1]


async def fetch_repo_readmes(github_url: str) -> list[dict]:
    """
    Fetch README content for all public, non-forked repos of a GitHub user.

    Args:
        github_url: GitHub profile URL (e.g. https://github.com/username)
                    or bare username string.

    Returns:
        List of dicts, each containing:
          - repo_name   (str)
          - description (str, may be empty)
          - readme_text (str, raw Markdown, trimmed to README_MAX_CHARS)
          - stars       (int)
          - language    (str or None)
          - repo_url    (str)
    """
    username = _extract_username(github_url)
    if not username:
        logger.warning("Could not extract username from: %s", github_url)
        return []

    headers = _build_headers()
    results: list[dict] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        # ------------------------------------------------------------------ #
        # 1. List all repos (paginate to handle users with >100 repos)        #
        # ------------------------------------------------------------------ #
        page = 1
        all_repos: list[dict] = []
        while True:
            resp = await client.get(
                f"{GITHUB_API}/users/{username}/repos",
                params={"per_page": 100, "sort": "updated", "page": page},
                headers=headers,
            )
            if resp.status_code == 404:
                logger.error("GitHub user not found: %s", username)
                return []
            resp.raise_for_status()
            page_repos = resp.json()
            if not page_repos:
                break
            all_repos.extend(page_repos)
            if len(page_repos) < 100:
                break
            page += 1

        logger.info("Found %d repos for user '%s'", len(all_repos), username)

        # ------------------------------------------------------------------ #
        # 2. Filter to non-fork repos only, then fetch all READMEs concurrently
        # ------------------------------------------------------------------ #
        own_repos = [r for r in all_repos if not r.get("fork")]

        async def _fetch_one(repo: dict) -> dict | None:
            readme_resp = await client.get(
                f"{GITHUB_API}/repos/{username}/{repo['name']}/readme",
                headers=headers,
            )
            if readme_resp.status_code != 200:
                logger.debug("No README for repo: %s/%s", username, repo["name"])
                return None

            content_b64 = readme_resp.json().get("content", "")
            try:
                readme_text = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
            except Exception as exc:
                logger.warning("Could not decode README for %s: %s", repo["name"], exc)
                return None

            if len(readme_text) > README_MAX_CHARS:
                readme_text = readme_text[:README_MAX_CHARS] + "\n\n[...README truncated for brevity...]"

            return {
                "repo_name": repo["name"],
                "description": repo.get("description") or "",
                "readme_text": readme_text,
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language"),
                "repo_url": repo.get("html_url", f"https://github.com/{username}/{repo['name']}"),
            }

        # Fire all README requests simultaneously
        fetched = await asyncio.gather(*[_fetch_one(r) for r in own_repos])
        results = [r for r in fetched if r is not None]

    logger.info("Fetched READMEs for %d repos", len(results))
    return results
