# 한국어(SM64DS 공식 번역) 이식 — 진행 문서

Super Mario 64 DS **(Korea)** 롬에서 **공식 한글 메시지**(BMG 712엔트리)와
**한글 8x16 글리프 폰트**(`ARCHIVE/c2d.narc[14]`)를 추출해
Ultimate 포트에 한국어 로컬라이제이션으로 이식하는 작업 산출물.

## 추출 산출물
| 파일 | 내용 |
|---|---|
| `data/kr_font_atlas_256.png` | 코드 0x00–0xFF 16x16 셀 한글 글리프 아틀라스 |
| `data/sheets/kr_sheet_p00…15.png` | 712개 메시지 렌더 시트(엔트리 인덱스 라벨 포함) |
| `data/kr_messages_meta.tsv` | 엔트리 인덱스 / 길이 / 코드 시퀀스 |
| `tools/*.py` | 추출·렌더 스크립트 |

## 확정된 구조 정보
- 메시지: `id26/msg_data_hn.bin` (BMG, INF1 카운트 712(0x2C8), DAT1 오프셋 0x30), u16 없는 1바이트 코드 문자열.
  - 0xFC=공백, 0xFD=줄바꿈, 0xFF=종료.
- 폰트: `ARCHIVE/c2d.narc` 내부 `[14] d_2d_mario_SPfont…ncl` 계열 16,384B.
  - AddChar 배치: `idx = ((c & 0x1f) + ((c & 0xe0) << 1))`,
    상반 타일 `base+idx*0x20`, 하반 타일 `base+idx*0x20+0x400`. (2-플레인, 총 256코드/512슬롯)
  - 팔레트: FAT id 137 (`d_2d_mario_3Dfont_ncl.bin`, BGR555 256엔트리).
- 사용 코드: 238개(0x00–0xFE). 코딩은 가나다순이 아니며 **글리프 시각 판독으로만 매핑 가능**.

## 다음 단계 (외부 행동 필요)
1. **코드→유니코드 매핑**: `data/kr_workbook_atlas.png`(238개 라벨 글리프, 3x 확대)와
   `data/sheets/*.png`(712 메시지 렌더)를 판독해 `data/kr_workbook_fill.tsv`의
   `unicode` 칸을 채운 뒤 커밋·푸시. (Malgun 템플릿 자동 매칭은 8px 폰트 특성상 실패했음)
2. **DS↔포트 대사 매핑**: N64 포트 `text/dialogs.h` 구조와 DS 메시지를 문장 단위 대응.
3. **통합**: `text/kr/dialogs.h` + KR 문자셋(charmap) + 포트 폰트 LUT에 한글 글리프 확장.
4. **빌드**: devkitPro 설치(관리자 권한 필요, 현재 환경 미보유로 미설치) + 원본 SM64 baserom 필요
   → `.cia`/QR 생성 후 이 포크 Release 업로드.