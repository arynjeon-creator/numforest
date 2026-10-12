# 숫자숲 탐험대

초등 연산 탐험 게임 (가족용 웹앱)

- 앱 주소: https://arynjeon-creator.github.io/numforest/
- 태블릿·폰 크롬에서 열고 "홈 화면에 추가"하면 앱처럼 쓸 수 있어요 (인터넷 없이도 열림)
- 엄마 설정: "엄마 설정 (꾹)"을 1초 누르기 → 비밀번호 (처음 0000)
- 태블릿 기록 맞추기: 엄마 설정 → 태블릿 기록 맞추기 → 가족 코드 (모든 기기 같은 코드)

## 파일
- index.html, sw.js, manifest.webmanifest, icon-*.png: 앱 (GitHub Pages가 보여 주는 파일)
- supabase-setup.sql: 기록 저장소 만들기 (Supabase SQL Editor에서 한 번 실행)
- tools/: 앱을 만드는 원본(source.html)과 빌드 도구(build.py)

개인정보: 아이 이름 등은 저장하지 않으며, 기록 맞추기 서버에는 게임 기록과 가족 코드의 해시만 저장됩니다.
