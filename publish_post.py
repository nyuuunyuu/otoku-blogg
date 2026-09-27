"""
GitHub Pages(Jekyll)ブログに、新しい記事を自動で追加するスクリプト。
GitHubの公式API(審査不要、Personal Access Tokenだけで使える)を使うので、
PinterestのAPIのような審査待ちは一切ありません。

事前準備:
1. GitHubの「Settings」→「Developer settings」→「Personal access tokens」→
   「Tokens (classic)」で新しいトークンを発行し、「repo」権限にチェックを入れる
2. .env に GITHUB_TOKEN と GITHUB_REPO(例: nyuuunyuu/otoku-blog)を追加

使い方:
    python publish_post.py --title "記事タイトル" --body-file post_body.md
"""

import argparse
import base64
import os
from datetime import date

import requests
from dotenv import load_dotenv

API_BASE = "https://api.github.com"


def slugify(text: str) -> str:
    """タイトルからファイル名に使える簡易スラッグを作る(日本語はそのまま使う)"""
    keep = "".join(c if c.isalnum() else "-" for c in text)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")[:50] or "post"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="記事タイトル")
    parser.add_argument("--body-file", required=True, help="記事本文が書かれたMarkdownファイルのパス")
    parser.add_argument("--categories", default="楽天 まとめ", help="カテゴリ(スペース区切り)")
    args = parser.parse_args()

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")  # 例: "nyuuunyuu/otoku-blog"
    if not token or not repo:
        print("GITHUB_TOKEN と GITHUB_REPO を .env に設定してください。")
        return

    with open(args.body_file, encoding="utf-8") as f:
        body = f.read()

    today = date.today().isoformat()
    front_matter = (
        "---\n"
        f'layout: post\n'
        f'title: "{args.title}"\n'
        f"date: {today} 12:00:00 +0900\n"
        f"categories: {args.categories}\n"
        "---\n\n"
    )
    full_content = front_matter + body

    filename = f"_posts/{today}-{slugify(args.title)}.md"
    url = f"{API_BASE}/repos/{repo}/contents/{filename}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {
        "message": f"新しい記事を追加: {args.title}",
        "content": base64.b64encode(full_content.encode("utf-8")).decode("utf-8"),
    }

    resp = requests.put(url, json=payload, headers=headers, timeout=20)
    if resp.status_code >= 400:
        print(f"投稿に失敗しました: {resp.status_code}\n{resp.text}")
        return

    print(f"投稿できました: {filename}")
    print("1〜2分待つとブログに反映されます。")


if __name__ == "__main__":
    main()
