# dev-helper_sjva
개인적으로 만든 SJVA 플러그인 개발 도우미  
혼자 쓸려고 만들기 시작한 건데 만들고 보니까 공개해도 괜찮을 것 같아서 공개합니다.  
대부분의 사람에겐 쓸모없는 플러그인입니다.

## 설치
SJVA에서 "시스템 → 플러그인 → 플러그인 수동 설치" 칸에 저장소 주소를 넣고 설치 버튼을 누르면 됩니다.  
`https://github.com/joyfuI/dev-helper`

## 만들게 된 과정
> SJVA에 내장된 FFmpeg가 구버전인 게 찝찝하니까 업데이트해야지!  
> 도커 환경을 잘 몰라서 무작정 아무 명령어나 쳐봤는데 apt, yum 모두 없는 명령어넹..  
> 아 그럼 바이너리를 직접 바꿔줘야 하나?라고 생각해서 FFmpeg 바이너리 파일 직접 교체  
> 파일 받고 압축 풀고 옮기고 귀찮.. 플러그인 테스트하다 보면 가끔 SJVA 초기화를 하는데 FFmpeg도 원래대로 돌아옴  
> 아 매번 업데이트하기 귀찮은데 걍 플러그인으로 하나 만들까?하고 제작 돌입  
> 플러그인 만들 때 특정 패키지가 필요하면 Command 메뉴에서 pip 실행하던 기억이 남  
> 어떤 패키지가 설치되어 있는지도 모르고 플러그인 테스트할 때 새로 설치한 패키지 지우는 것도 귀찮은데 아예 기능으로 만들어야겠다.  
> *파이썬 메뉴 추가*  
> 이참에 아예 플러그인 개발 도우미로 이름을 바꿔야겠다. 어떤 기능이 있으면 좋을까?  
> 전체적인 로그 보려고 맨날 터미널 띄웠는데 로그를 한군데에서 볼 수 있으면 좋겠다  
> *로그 메뉴 추가*  
> 로그 기능 만들려고 log 템플릿 파일 살펴보는데 처음 보는 매크로들이 많네?  
> 템플릿 매크로들이 어떻게 생겼는지 보여주는 페이지 하나 있으면 html 만들 때 편하겠다  
> *템플릿 매크로 메뉴 추가*  
> 몇몇 플러그인들을 보면 app.config['config'] 정보를 활용하던데 저기엔 어떤 값들이 있을까?  
> *데이터베이스 메뉴 추가*  
> 그러고 보니 도커 환경을 잘 모르잖아? platform 패키지에선 어떤 정보를 보여주지?  
> *정보 메뉴 추가*  
> 이제 대충 불편/궁금했던 건 다 추가된 것 같네.. 원래 목적(?)이었던 FFmpeg 업데이트 기능이나 추가하자..  
> *FFmpeg 업데이트 기능 추가*  
> 혼자 쓰려고 만든 건데 뭐 공개해도 괜찮을듯;;  

뭐 대충 이런 의식의 흐름으로 만들게 되었습니다. 원래 제작 동기였던 FFmpeg 업데이트 기능이 맨 마지막에 추가된 게 함정...  
암튼 개인적인 목적으로 의식의 흐름대로 만들어진 만큼 기능 추가도 의식의 흐름대로 할 예정입니다ㅎㅎ

## 메뉴 소개
* **정보**  
  platform, sys 패키지의 주요 값을 보여줍니다.
* **파이썬**  
  파이썬 패키지 설치/업데이트/삭제를 할 수 있습니다.
* **데이터베이스**  
  app.config 값을 보여줍니다.  
  원래 db 파일의 내용을 보여주는 기능을 생각했는데 잘 안돼서 일단 보류...
* **로그**  
  모든 로그 파일을 보여줍니다.
* **라이브러리**  
  FFmpeg 업데이트가 가능합니다. (나이틀리와 릴리즈 선택 가능)  
  다운로드부터 진행하다 보니 오래 걸립니다. 그냥 5분 정도 뒤에 버전확인 버튼 눌러서 잘 진행됐는지 확인해보세요.
* **템플릿 매크로**  
  SJVA에 내장된 템플릿 매크로를 보여줍니다.
