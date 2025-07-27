# YouTube Transcript MCP Server

YouTube 영상의 트랜스크립트를 가져오는 MCP (Model Context Protocol) 서버입니다. Claude와 같은 AI 모델에서 YouTube 영상의 자막 데이터를 쉽게 활용할 수 있도록 해줍니다.

## 기능

- YouTube 영상 URL에서 트랜스크립트 추출
- 다국어 트랜스크립트 지원 (한국어, 영어 등)
- 자동 생성 및 수동 생성 자막 모두 지원
- 사용 가능한 트랜스크립트 목록 조회

## 설치

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd youtube_transcript_mcp
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는 Windows의 경우: venv\Scripts\activate
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

## Claude Desktop 설정

Claude Desktop에서 이 MCP 서버를 사용하려면 Claude 설정 파일을 수정해야 합니다.

### macOS
Claude Desktop 설정 파일 위치: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Claude Desktop 설정 파일 위치: `%APPDATA%\Claude\claude_desktop_config.json`

설정 파일에 다음 내용을 추가하세요:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "/path/to/your/youtube_transcript_mcp/venv/bin/python",
      "args": ["/path/to/your/youtube_transcript_mcp/youtube_transcript_mcp_server.py"],
      "env": {}
    }
  }
}
```

**중요**: `/path/to/your/youtube_transcript_mcp`를 실제 프로젝트 경로로 변경해주세요.

## 사용 방법

Claude Desktop에서 설정이 완료되면 다음과 같이 사용할 수 있습니다:

### 트랜스크립트 가져오기
```
이 YouTube 영상의 트랜스크립트를 가져와줘: https://www.youtube.com/watch?v=VIDEO_ID
```

### 특정 언어로 트랜스크립트 가져오기
```
이 영상의 영어 트랜스크립트를 가져와줘: https://www.youtube.com/watch?v=VIDEO_ID
```

### 사용 가능한 트랜스크립트 목록 조회
```
이 영상에서 사용 가능한 트랜스크립트 목록을 보여줘: https://www.youtube.com/watch?v=VIDEO_ID
```

## 지원되는 URL 형식

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `VIDEO_ID` (11자리 비디오 ID만)

## 지원되는 언어

- 한국어 (ko) - 기본값
- 영어 (en)
- 기타 YouTube에서 지원하는 모든 언어

서버는 요청된 언어가 없을 경우 자동으로 한국어 → 영어 → 자동 생성 자막 순으로 시도합니다.

## API 도구

이 MCP 서버는 다음 두 가지 도구를 제공합니다:

### 1. get_youtube_transcript
- **설명**: YouTube 영상의 트랜스크립트를 가져옵니다
- **매개변수**:
  - `url` (필수): YouTube 영상 URL
  - `language` (선택, 기본값: "ko"): 언어 코드

### 2. list_available_transcripts
- **설명**: 사용 가능한 트랜스크립트 목록을 가져옵니다
- **매개변수**:
  - `url` (필수): YouTube 영상 URL

## 문제 해결

### 설정이 적용되지 않는 경우
1. Claude Desktop을 완전히 종료하고 다시 시작
2. 설정 파일의 경로가 올바른지 확인
3. 가상환경이 활성화되어 있는지 확인

### 트랜스크립트를 찾을 수 없는 경우
- 해당 영상에 자막이 없을 수 있습니다
- 비공개 영상이거나 접근이 제한된 영상일 수 있습니다
- `list_available_transcripts` 도구를 사용해 사용 가능한 언어를 확인해보세요

## 의존성

- `mcp>=0.8.0`: Model Context Protocol 라이브러리
- `youtube-transcript-api>=0.6.0`: YouTube 트랜스크립트 API
- `asyncio`: 비동기 처리

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
