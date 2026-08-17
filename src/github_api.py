import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env")


def get_repository(owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:

        data = response.json()

        return {
            "name": data["full_name"],
            "url": data["html_url"],
            "stars": data["stargazers_count"]
        }

    print(
        f"GitHub API error: "
        f"{response.status_code}"
    )

    return None


if __name__ == "__main__":

    result = get_repository(
        "huggingface",
        "transformers"
    )

    if result:

        print("\nGitHub Repository")
        print("------------------")
        print("Name:", result["name"])
        print("URL:", result["url"])
        print("Stars:", result["stars"])