import re


GITHUB_PATTERN = re.compile(
    r"https?://github\.com/"
    r"[A-Za-z0-9_.-]+/"
    r"[A-Za-z0-9_.-]+"
)


def find_github_url(text):
    """
    Find an explicit GitHub repository URL
    inside supplied text.

    Returns None if no GitHub URL is found.
    """

    if not text:
        return None

    match = GITHUB_PATTERN.search(text)

    if match:
        return match.group(0).rstrip(".,);]")

    return None