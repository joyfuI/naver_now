# NAVER NOW_sjva
[SJVA](https://sjva.me/) 용 NAVER NOW 플러그인  
SJVA에서 NAVER NOW를 다운로드할 수 있습니다.

## 설치
SJVA에서 "시스템 → 플러그인 → 플러그인 수동 설치" 칸에 저장소 주소를 넣고 설치 버튼을 누르면 됩니다.  
`https://github.com/joyfuI/naver_now`

## 잡담
네이버 나우는 다시보기가 없어서 실시간 방송을 다운받기 위해 만들었습니다.  
스케줄별로 Cron 설정을 할 수 있고 지정한 시간이 되면 약 10분 동안 10초 간격 다운로드 시도를 합니다.  
따라서 방송 스케줄 5분 전으로 Cron을 설정해두기를 추천합니다.

Cron에서 week를 나타내는 부분이 통상적인 `0:일요일 ~ 6:토요일`이 아니라 `0:월요일 ~ 6:일요일`이므로 유의하시길 바랍니다.  
헛갈린다 싶으면 영어 약자로 지정하셔도 됩니다.

## Changelog
v0.1.2
* 스케줄 Cron 설정을 좀 더 편리하게 지정할 수 있도록 수정

v0.1.1
* 다운로드 실패 시 한 번 더 재시도하도록 수정
* 켜져 있는 스케줄을 변경하면 스케줄러에도 바로 적용이 되게 수정

v0.1.0
* 최초 공개
