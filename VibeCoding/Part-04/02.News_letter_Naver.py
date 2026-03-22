"""
Naver News Search CLI

Usage examples:
   python Part-04/02.News_letter_Naver.py --query "파이썬" --display 10
   python Part-04/02.News_letter_Naver.py  # interactive prompt
 
 Notes:
 - Client ID and Secret default to values you provided but can be overridden with
  environment variables NAVER_CLIENT_ID and NAVER_CLIENT_SECRET or CLI options.
"""

import os
import sys
import argparse
import requests
import json
import re
import html
from typing import Dict
from dotenv import load_dotenv
import os

load_dotenv()

# Defaults (from user-provided values)
DEFAULT_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID"")
DEFAULT_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET"")

ENDPOINT = "https://openapi.naver.com/v1/search/news.json"


def strip_html_tags(text: str) -> str:
	if not text:
		return ""
	text = re.sub(r"<[^>]+>", "", text)
	return html.unescape(text)


def search_news(query: str, client_id: str, client_secret: str, display: int = 10, start: int = 1, sort: str = None) -> Dict:
	headers = {
		"X-Naver-Client-Id": client_id,
		"X-Naver-Client-Secret": client_secret,
	}
	params = {"query": query, "display": display, "start": start}
	if sort:
		params["sort"] = sort

	resp = requests.get(ENDPOINT, headers=headers, params=params, timeout=10)
	resp.raise_for_status()
	return resp.json()


def print_results(data: Dict, to_console: bool = True):
	items = data.get("items", [])
	if not items:
		print("검색 결과가 없습니다.")
		return

	for idx, it in enumerate(items, start=1):
		title = strip_html_tags(it.get("title", ""))
		description = strip_html_tags(it.get("description", ""))
		originallink = it.get("originallink") or it.get("link") or ""
		pubdate = it.get("pubDate") or it.get("pubdate") or ""

		print(f"{idx}. {title}")
		if pubdate:
			print(f"   날짜: {pubdate}")
		if description:
			print(f"   요약: {description}")
		if originallink:
			print(f"   링크: {originallink}")
		print("-")


def save_results_json(data: Dict, filename: str):
	try:
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, ensure_ascii=False, indent=2)
		print(f"결과를 {filename}에 저장했습니다.")
	except Exception as e:
		print(f"파일 저장 오류: {e}")


def main(argv=None):
	parser = argparse.ArgumentParser(description="Naver News Search CLI")
	parser.add_argument("--query", "-q", help="검색어 (예: '파이썬')")
	parser.add_argument("--display", "-d", type=int, default=10, help="표시 개수 (최대 100)")
	parser.add_argument("--start", "-s", type=int, default=1, help="시작 인덱스")
	parser.add_argument("--sort", help="정렬 (sim 또는 date)")
	parser.add_argument("--client-id", help="Naver Client ID")
	parser.add_argument("--client-secret", help="Naver Client Secret")
	parser.add_argument("--save", help="검색 결과 JSON으로 저장할 파일명")

	args = parser.parse_args(argv)

	client_id = args.client_id or DEFAULT_CLIENT_ID
	client_secret = args.client_secret or DEFAULT_CLIENT_SECRET

	if not args.query:
		try:
			q = input("검색어를 입력하세요: ").strip()
		except (KeyboardInterrupt, EOFError):
			print("입력 취소")
			sys.exit(0)
	else:
		q = args.query.strip()

	if not q:
		print("검색어를 입력해야 합니다.")
		sys.exit(1)

	# Validate display value
	if args.display < 1 or args.display > 100:
		print("display 값은 1~100 사이여야 합니다.")
		sys.exit(1)

	try:
		data = search_news(q, client_id, client_secret, display=args.display, start=args.start, sort=args.sort)
		print_results(data)

		if args.save:
			save_results_json(data, args.save)

	except requests.HTTPError as he:
		if he.response is not None and he.response.status_code == 401:
			print("인증 실패: Client ID/Client Secret을 확인하세요.")
		else:
			print(f"HTTP 오류: {he}")
		sys.exit(1)
	except Exception as e:
		print(f"오류 발생: {e}")
		sys.exit(1)


if __name__ == "__main__":
	main()
