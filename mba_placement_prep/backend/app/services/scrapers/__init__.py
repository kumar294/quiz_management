"""Public-source ingestion. Each scraper must:
  - respect the site's robots.txt and terms of use,
  - identify itself with settings.scraper_user_agent,
  - throttle to settings.scraper_rate_limit_per_min,
  - cache results in PublicInterviewData rather than re-fetching.
The real HTML parsing lives in per-site modules; this package exposes only the
uniform `fetch(company, role) -> PublicInterviewData` interface.
"""
