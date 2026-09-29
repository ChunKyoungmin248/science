# LEVER 통합과학 WEEK 2 — 평형과 안정성

- `LEVER_통합과학_WEEK2_평형과안정성.hwpx` : 한글 교재 파일 (한글 2014 이상에서 열림, `.hwp`로 다시 저장 가능)
- `LEVER_통합과학_WEEK2_미리보기.pdf` : rhwp 렌더링 미리보기 (실제 한글 화면과 줄 나눔이 조금 다를 수 있음)

## 사용 글꼴
- Pretendard (Regular / Medium / SemiBold / Bold / Black) — 없으면 맑은 고딕으로 대체
- Times New Roman (변수 기울임), 한글 수식(HYhwpEQ)

## 다시 빌드
```
python3 tools/draw_figs.py fig                     # 손필기 도식 재작도
EQSIZE_BIN=<rhwp eqsize> python3 tools/build_lever.py fig out.hwpx
```
`tools/eqsize.rs`는 rhwp(https://github.com/edwardkim/rhwp) 예제로 넣어 빌드하면 수식 크기를 계산합니다.
