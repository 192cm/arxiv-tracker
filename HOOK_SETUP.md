# Hook 설정 가이드

Hook은 Claude Code 안에서 `/update-config` 자연어 명령으로 설정하는 게 가장 편하다.
이 프로젝트에서 권장하는 훅은 다음 2개.

## 1. PreCompact 훅 — 자동 백업

context가 자동 압축되기 전에 지금까지의 진행상황을 CLAUDE.md에 기록.

Claude Code 세션에서 그대로 입력:

```
/update-config PreCompact가 진행되기 전에 우리가 진행했던 프로젝트의 중요한 내용들과 필수적인 디테일들을 CLAUDE.md에 작성해줘. 그리고 작성된 날짜도 년, 월, 일, 시간으로 표시해주고. 이 프로젝트에만 적용되게 해줘.
```

## 2. Stop 훅 — 응답 완료 알림 (선택)

긴 작업 끝났을 때 beep 음으로 알림.

```
/update-config 클로드 코드가 응답을 완료할 때마다 beep 음이 나와서 알려주도록 해줘. 이 프로젝트에만 적용되게 해줘.
```

## 적용 확인

```bash
cat .claude/settings.json
```

`hooks` 키 아래에 PreCompact와 Stop 항목이 들어가 있으면 성공.

## 보고서에 쓸 때

훅이 적용된 `.claude/settings.json` 파일을 보고서에 캡처해서 첨부하면 "Hook을 실제로 설정했다"는 근거가 된다.
