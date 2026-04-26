# agents/job_discovery_agent.py
#
# Fetches live jobs from RemoteOK and scores each one against the candidate's
# own skill/keyword set extracted directly from the resume. No hard-coded role
# names are used anywhere in the search pipeline.

import requests
import json
import os
import re


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower())


class JobDiscoveryAgent:

    @staticmethod
    def fetch_jobs(resume_keywords: list[str] | str, limit: int = 30) -> list[dict]:
        """
        Parameters
        ----------
        resume_keywords : list[str] | str
            Either a list of keyword strings extracted from the resume, OR the
            legacy comma-separated string produced by RoleDetectionAgent.
        limit : int
            Maximum number of jobs to return.

        Returns
        -------
        list[dict]  – each dict has: title, company, location, description, url, score
        """

        # ── Normalise input ───────────────────────────────────────────────
        if isinstance(resume_keywords, str):
            keywords = [k.strip() for k in resume_keywords.split(",") if k.strip()]
        else:
            keywords = [k.strip() for k in resume_keywords if k.strip()]

        kw_normalised = [_normalise(kw) for kw in keywords]

        # ── Fetch raw job feed ────────────────────────────────────────────
        url = "https://remoteok.com/api"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            jobs_data = response.json()
        except Exception:
            return []

        # ── Score every job against all resume keywords ───────────────────
        scored = []
        seen = set()

        for job in jobs_data[1:]:   # first element is metadata
            job_id = f"{job.get('position', '')}-{job.get('company', '')}"
            if job_id in seen:
                continue

            # Build a single searchable blob from all job text fields
            job_blob = _normalise(" ".join([
                str(job.get("position", "")),
                str(job.get("company", "")),
                str(job.get("description", "")),
                " ".join(job.get("tags", [])),
            ]))

            # Count how many of the candidate's keywords appear in this job
            matched = sum(1 for kw in kw_normalised if kw and kw in job_blob)

            if matched == 0:
                continue    # skip completely irrelevant jobs

            score = round((matched / max(len(kw_normalised), 1)) * 100)

            seen.add(job_id)
            scored.append({
                "title":       job.get("position", ""),
                "company":     job.get("company", ""),
                "location":    job.get("location", "Remote"),
                "description": job.get("description", ""),
                "url":         job.get("url", ""),
                "score":       score,
            })

        # ── Sort by relevance, return top N ──────────────────────────────
        scored.sort(key=lambda j: j["score"], reverse=True)
        result = scored[:limit]

        # Persist for inspection / caching
        os.makedirs("data", exist_ok=True)
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

        return result