"""
GitHub README scraper — background task utilities.

run_github_scrape_background() is the entry point called by FastAPI's
BackgroundTasks immediately after user registration.

It:
  1. Fetches all public non-fork repos via GitHub REST API (concurrent).
  2. Filters out repos whose README has fewer than 50 words.
  3. Sends all qualifying READMEs concurrently to the LLM for summarisation.
  4. Appends the structured summaries to the user's user_context in the DB.
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.user import User
from backend.utils.github_scraper import fetch_repo_readmes
from backend.core.database import async_session_maker

logger = logging.getLogger(__name__)

MIN_README_WORDS = 50  # Repos with fewer words are skipped


def _word_count(text: str) -> int:
    return len(text.split())


async def _summarise_repo(repo: dict, llm) -> str | None:
    """
    Summarise a single repo's README with the LLM.
    Returns the summary string, or None if it should be skipped.
    """
    from langchain_core.messages import SystemMessage, HumanMessage
    from backend.graph.nodes import GITHUB_README_SUMMARIZER_PROMPT

    prompt = GITHUB_README_SUMMARIZER_PROMPT.format(repo_name=repo["repo_name"])
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(
            content=(
                f"Repository: {repo['repo_name']}\n"
                f"Description: {repo['description']}\n"
                f"Stars: {repo['stars']} | Language: {repo.get('language', 'N/A')}\n"
                f"URL: {repo['repo_url']}\n\n"
                f"README:\n{repo['readme_text']}"
            )
        ),
    ]
    try:
        response = await asyncio.to_thread(llm.invoke, messages)
        text = response.content.strip()
        if text.upper() == "SKIP":
            logger.debug("LLM chose to skip repo: %s", repo["repo_name"])
            return None
        return text
    except Exception as exc:
        logger.warning("LLM summarisation failed for %s: %s", repo["repo_name"], exc)
        return None


async def run_github_scrape_background(user_id: str, github_url: str) -> None:
    """
    Full pipeline — meant to be called as a FastAPI BackgroundTask.

    Creates its own DB session (independent of the request session which
    will have closed by the time this runs).
    """
    logger.info("[GitHub BG] Starting scrape for user %s → %s", user_id, github_url)

    # ── 1. Fetch all READMEs concurrently ────────────────────────────────────
    try:
        repos = await fetch_repo_readmes(github_url)
    except Exception as exc:
        logger.error("[GitHub BG] Failed to fetch READMEs: %s", exc)
        return

    if not repos:
        logger.info("[GitHub BG] No repos found for %s", github_url)
        return

    # ── 2. Filter: skip repos with fewer than MIN_README_WORDS words ──────────
    qualifying = [r for r in repos if _word_count(r["readme_text"]) >= MIN_README_WORDS]
    skipped = len(repos) - len(qualifying)
    logger.info(
        "[GitHub BG] %d repos total | %d qualify (≥%d words) | %d skipped",
        len(repos), len(qualifying), MIN_README_WORDS, skipped,
    )

    if not qualifying:
        logger.info("[GitHub BG] No qualifying repos after word-count filter.")
        return

    # ── 3. Summarise all qualifying repos concurrently ────────────────────────
    from backend.graph.chains import llm  # import here to avoid circular import at module load

    tasks = [_summarise_repo(repo, llm) for repo in qualifying]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    summaries: list[str] = []
    for repo, result in zip(qualifying, results):
        if isinstance(result, Exception):
            logger.warning("[GitHub BG] Exception summarising %s: %s", repo["repo_name"], result)
        elif result is not None:
            summaries.append(result)

    if not summaries:
        logger.info("[GitHub BG] No usable summaries generated.")
        return

    github_section = (
        "## GitHub Projects (auto-summarised)\n\n"
        + "\n\n---\n\n".join(summaries)
    )

    # ── 4. Persist to DB ─────────────────────────────────────────────────────
    async with async_session_maker() as db:
        try:
            result_db = await db.execute(select(User).where(User.id == user_id))
            db_user = result_db.scalars().first()
            if not db_user:
                logger.error("[GitHub BG] User %s not found in DB.", user_id)
                return

            existing = (db_user.user_context or "").strip()
            # Replace any old GitHub section to avoid duplication on re-runs
            if "## GitHub Projects (auto-summarised)" in existing:
                existing = existing.split("## GitHub Projects (auto-summarised)")[0].strip()

            db_user.user_context = (existing + "\n\n" + github_section).strip()
            await db.commit()
            logger.info(
                "[GitHub BG] ✅ Persisted %d project summaries for user %s",
                len(summaries), user_id,
            )
        except Exception as exc:
            logger.error("[GitHub BG] DB write failed: %s", exc)
            await db.rollback()
