"""Hashnode 자동 게시 봇 — GraphQL API 기반.

Hashnode API:
- https://hashnode.com/settings/developer → Personal Access Token 발급 (즉시, 무료)
- POST https://gql.hashnode.com/  (GraphQL)
- Mutation: publishPost

환경변수:
- HASHNODE_TOKEN
- HASHNODE_PUBLICATION_ID (사용자 첫 블로그의 publication ID)
- SITE_URL
"""
from __future__ import annotations
import os
import json
import random
from datetime import date
from pathlib import Path
from urllib import request

TOKEN = os.environ.get("HASHNODE_TOKEN", "")
PUB_ID = os.environ.get("HASHNODE_PUBLICATION_ID", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")

STATE_FILE = Path(os.environ.get(
    "HASHNODE_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".hashnode_state.json"),
))

ENDPOINT = "https://gql.hashnode.com/"


# Dev.to와 동일한 콘텐츠 풀 재사용 (영문 콘텐츠는 공유)
try:
    from devto_bot import POSTS as DEVTO_POSTS
except ImportError:
    DEVTO_POSTS = []


def gql(query: str, variables: dict) -> dict:
    if not TOKEN:
        return {"error": "HASHNODE_TOKEN missing"}
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": TOKEN,
                 "Content-Type": "application/json",
                 "User-Agent": "tarofortune-bot/0.1"},
    )
    try:
        with request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode()
            except Exception:
                pass
        return {"error": f"{e}: {b}"}


def discover_publication() -> str | None:
    """사용자 첫 publication ID 자동 발견 (사용자가 별도 입력 안 해도 됨)."""
    query = """
    query Me {
      me {
        publications(first: 5) {
          edges { node { id title } }
        }
      }
    }
    """
    r = gql(query, {})
    try:
        edges = r["data"]["me"]["publications"]["edges"]
        if edges:
            return edges[0]["node"]["id"]
    except Exception:
        pass
    return None


def publish_post(title: str, body_md: str, tags: list[str], canonical: str = None) -> dict:
    pub_id = PUB_ID or discover_publication()
    if not pub_id:
        return {"ok": False, "error": "No publication ID (set HASHNODE_PUBLICATION_ID)"}

    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post { id slug url title }
      }
    }
    """
    # Hashnode는 tag 객체 형태로 받음
    tag_input = [{"slug": t.lower().replace(" ", "-"), "name": t} for t in tags]
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": body_md,
            "publicationId": pub_id,
            "tags": tag_input,
        }
    }
    if canonical:
        variables["input"]["originalArticleURL"] = canonical
    r = gql(mutation, variables)
    if "errors" in r:
        return {"ok": False, "error": r["errors"]}
    post = r.get("data", {}).get("publishPost", {}).get("post")
    if post:
        return {"ok": True, "url": post.get("url"), "id": post.get("id")}
    return {"ok": False, "error": json.dumps(r)[:300]}


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted_indices": [], "last_date": None}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def run_daily():
    if not DEVTO_POSTS:
        print("No content pool available.")
        return
    state = load_state()
    today = date.today().isoformat()
    if state.get("last_date") == today:
        print("Already posted today.")
        return
    posted = set(state.get("posted_indices", []))
    available = [i for i in range(len(DEVTO_POSTS)) if i not in posted]
    if not available:
        state["posted_indices"] = []
        available = list(range(len(DEVTO_POSTS)))
    idx = random.choice(available)
    post = DEVTO_POSTS[idx]
    result = publish_post(post["title"], post["body_markdown"],
                          post["tags"], post.get("canonical_url"))
    print(f"[hashnode] idx={idx} {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("posted_indices", []).append(idx)
        state["last_date"] = today
        save_state(state)


if __name__ == "__main__":
    run_daily()
