#!/usr/bin/env python3
"""
알림 처리 수정된 YouTube Transcript MCP Server
notifications/initialized 메시지를 올바르게 처리합니다.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """URL에서 YouTube 비디오 ID를 추출합니다."""
    if len(url) == 11 and not ("/" in url or "." in url):
        return url

    parsed_url = urlparse(url)

    if "youtube.com" in parsed_url.netloc:
        if "/watch" in parsed_url.path:
            query_params = parse_qs(parsed_url.query)
            if "v" in query_params:
                return query_params["v"][0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path[1:].split("?")[0]

    raise ValueError("유효하지 않은 YouTube URL입니다.")


def extract_text_from_transcript(fetched_transcript) -> str:
    """FetchedTranscript 객체에서 텍스트를 추출합니다."""
    try:
        if hasattr(fetched_transcript, "snippets"):
            text_parts = []
            for snippet in fetched_transcript.snippets:
                if hasattr(snippet, "text"):
                    text_parts.append(snippet.text)
            return " ".join(text_parts)
        elif isinstance(fetched_transcript, list):
            text_parts = []
            for item in fetched_transcript:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                elif hasattr(item, "text"):
                    text_parts.append(item.text)
            return " ".join(text_parts)
        elif isinstance(fetched_transcript, str):
            return fetched_transcript
        else:
            return str(fetched_transcript)
    except Exception as e:
        return str(fetched_transcript)


def get_transcript(url: str, language: str = "ko") -> str:
    """트랜스크립트를 가져옵니다."""
    try:
        video_id = extract_video_id(url)
        print(f"비디오 ID: {video_id}, 요청 언어: {language}", file=sys.stderr)

        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        languages_to_try = [language, "ko", "en"]

        for lang in languages_to_try:
            try:
                transcript = transcript_list.find_transcript([lang])
                fetched_data = transcript.fetch()
                text = extract_text_from_transcript(fetched_data)

                lang_info = getattr(transcript, "language", lang)
                is_generated = getattr(transcript, "is_generated", False)
                status = " (자동 생성)" if is_generated else " (수동 생성)"

                return f"YouTube 영상 트랜스크립트\n비디오 ID: {video_id}\n언어: {lang_info}{status}\n글자 수: {len(text)}\n\n{text}"

            except Exception:
                continue

        try:
            transcript = transcript_list.find_generated_transcript(["ko", "en"])
            fetched_data = transcript.fetch()
            text = extract_text_from_transcript(fetched_data)
            lang_info = getattr(transcript, "language", "auto")
            return f"YouTube 영상 트랜스크립트\n비디오 ID: {video_id}\n언어: {lang_info} (자동 생성)\n글자 수: {len(text)}\n\n{text}"
        except Exception:
            pass

        return f"오류: 비디오 ID {video_id}에서 사용 가능한 트랜스크립트를 찾을 수 없습니다."

    except Exception as e:
        return f"트랜스크립트 가져오기 실패: {str(e)}"


def list_transcripts(url: str) -> str:
    """사용 가능한 트랜스크립트 목록을 가져옵니다."""
    try:
        video_id = extract_video_id(url)
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        return f"YouTube 영상 (ID: {video_id}) 트랜스크립트 목록:\n\n{str(transcript_list)}"
    except Exception as e:
        return f"트랜스크립트 목록 가져오기 실패: {str(e)}"


async def handle_request(request):
    """요청을 처리합니다."""
    try:
        method = request.get("method")
        request_id = request.get("id")  # id가 없을 수도 있음 (알림의 경우)

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "youtube-transcript-server",
                        "version": "1.0.0",
                    },
                },
            }

        elif method == "notifications/initialized":
            # 알림 메시지는 응답하지 않음
            print("초기화 알림 받음", file=sys.stderr)
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_youtube_transcript",
                            "description": "YouTube 영상의 트랜스크립트를 가져옵니다",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "url": {
                                        "type": "string",
                                        "description": "YouTube 영상 URL",
                                    },
                                    "language": {
                                        "type": "string",
                                        "description": "언어 코드",
                                        "default": "ko",
                                    },
                                },
                                "required": ["url"],
                            },
                        },
                        {
                            "name": "list_available_transcripts",
                            "description": "사용 가능한 트랜스크립트 목록을 가져옵니다",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "url": {
                                        "type": "string",
                                        "description": "YouTube 영상 URL",
                                    }
                                },
                                "required": ["url"],
                            },
                        },
                    ]
                },
            }

        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            print(f"도구 호출: {tool_name}, 인수: {arguments}", file=sys.stderr)

            if tool_name == "get_youtube_transcript":
                url = arguments.get("url")
                language = arguments.get("language", "ko")
                result = get_transcript(url, language)

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result}],
                        "isError": False,
                    },
                }

            elif tool_name == "list_available_transcripts":
                url = arguments.get("url")
                result = list_transcripts(url)

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result}],
                        "isError": False,
                    },
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                }

        # 지원하지 않는 메서드 (resources, prompts 등)
        elif method in ["resources/list", "prompts/list"]:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": "Method not found"},
            }

        else:
            print(f"알 수 없는 메서드: {method}", file=sys.stderr)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": "Method not found"},
            }

    except Exception as e:
        print(f"요청 처리 오류: {e}", file=sys.stderr)
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32603, "message": str(e)},
        }


async def main():
    """메인 함수"""
    print("YouTube Transcript MCP Server 시작...", file=sys.stderr)

    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            if not line:
                break

            try:
                request = json.loads(line.strip())
                response = await handle_request(request)

                # 알림 메시지의 경우 응답하지 않음
                if response is not None:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"처리 오류: {e}", file=sys.stderr)

    except Exception as e:
        print(f"서버 오류: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
