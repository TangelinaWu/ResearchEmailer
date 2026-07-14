"""Classify a contact's email domain as NYC tristate (NY/NJ/CT) or not.

No institution/location field is scraped from arXiv PDFs, so this is a best-effort
heuristic based on email domain. Add/remove domains below as needed.
"""

NYC_TRISTATE_DOMAINS = {
    # NYC
    "nyu.edu", "nyulangone.org", "columbia.edu", "cuny.edu", "gc.cuny.edu",
    "hunter.cuny.edu", "baruch.cuny.edu", "ccny.cuny.edu", "citytech.cuny.edu",
    "yu.edu", "fordham.edu", "cooper.edu", "pratt.edu", "nyit.edu",
    "mssm.edu", "rockefeller.edu", "hofstra.edu", "pace.edu", "newschool.edu",
    "adelphi.edu",
    # NY (broader state)
    "cornell.edu", "stonybrook.edu", "sunysb.edu", "albany.edu", "buffalo.edu",
    "rochester.edu", "rpi.edu", "syr.edu", "vassar.edu", "colgate.edu",
    # NJ
    "rutgers.edu", "princeton.edu", "stevens.edu", "njit.edu", "shu.edu",
    "montclair.edu", "rider.edu", "tcnj.edu",
    # CT
    "yale.edu", "uconn.edu", "wesleyan.edu", "quinnipiac.edu", "fairfield.edu",
}


def classify_region(email):
    """Return 'nyc_tristate', 'remote', or 'unknown' based on the email domain."""
    if not email or "@" not in email:
        return "unknown"
    domain = email.strip().lower().split("@")[-1]
    return "nyc_tristate" if domain in NYC_TRISTATE_DOMAINS else "remote"
