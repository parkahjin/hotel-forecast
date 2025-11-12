# AWS Lightsail을 활용한 Streamlit 웹 배포 완벽 가이드

> **프로젝트**: 호텔 객실 수요 예측 시스템  
> **작성일**: 2025년 10월  
> **목적**: AWS Lightsail에서 Streamlit 앱을 배포하고 안정적으로 운영하기

---

## 📋 목차
1. [개요](#개요)
2. [AWS Lightsail 인스턴스 생성](#1-aws-lightsail-인스턴스-생성)
3. [서버 초기 설정](#2-서버-초기-설정)
4. [프로젝트 배포](#3-프로젝트-배포)
5. [Nginx 리버스 프록시 설정](#4-nginx-리버스-프록시-설정)
6. [도메인 및 SSL 설정](#5-도메인-및-ssl-설정)
7. [자동 재시작 설정 (핵심!)](#6-자동-재시작-설정-핵심)
8. [문제 해결 가이드](#7-문제-해결-가이드)
9. [유지보수 명령어](#8-유지보수-명령어)

---

## 개요

### 배포 아키텍처
```
사용자 브라우저
    ↓ HTTPS (443)
DuckDNS 도메인 (hotel-demand-forecast.duckdns.org)
    ↓
AWS Lightsail 인스턴스 (Ubuntu 24.04)
    ↓
Nginx (리버스 프록시)
    ↓ HTTP (8501)
Streamlit 앱 (Python)
```

### 기술 스택
- **클라우드**: AWS Lightsail
- **OS**: Ubuntu 24.04 LTS
- **웹서버**: Nginx
- **앱**: Streamlit + Python
- **도메인**: DuckDNS (무료 DDNS)
- **SSL**: Let's Encrypt (무료)
- **프로세스 관리**: systemd

---

## 1. AWS Lightsail 인스턴스 생성

### 1.1 인스턴스 설정
```
플랫폼: Linux/Unix
운영체제: Ubuntu 24.04 LTS
플랜: $5/월 (1GB RAM, 1 vCPU, 40GB SSD)
위치: 서울 (ap-northeast-2)
```

### 1.2 방화벽 설정
```
SSH: 22 포트
HTTP: 80 포트 
HTTPS: 443 포트
Custom: 8501 포트 (Streamlit, 선택사항)
```

### 1.3 고정 IP 할당
- Lightsail 콘솔 → 네트워킹 탭
- 고정 IP 생성 및 인스턴스에 연결
- 예시: `3.37.159.57`

---

## 2. 서버 초기 설정

### 2.1 SSH 접속
```bash
# Lightsail 콘솔에서 "SSH를 사용하여 연결" 클릭
# 또는 로컬에서
ssh ubuntu@3.37.159.57
```

### 2.2 시스템 업데이트
```bash
sudo apt update
sudo apt upgrade -y
```

### 2.3 필수 패키지 설치
```bash
# Python 및 pip
sudo apt install python3 python3-pip python3-venv -y

# Nginx (웹서버)
sudo apt install nginx -y

# Git
sudo apt install git -y

# 기타 유틸리티
sudo apt install curl wget unzip -y
```

---

## 3. 프로젝트 배포

### 3.1 프로젝트 클론
```bash
cd ~
git clone https://github.com/your-username/hotel-forecast.git streamlit_app
cd streamlit_app
```

### 3.2 Python 가상환경 생성
```bash
python3 -m venv ~/streamlit_env
source ~/streamlit_env/bin/activate
```

### 3.3 의존성 설치
```bash
pip install --upgrade pip
pip install streamlit pandas plotly prophet
# 또는
pip install -r requirements.txt
```

### 3.4 로컬 테스트
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

브라우저에서 `http://[서버IP]:8501` 접속하여 확인

---

## 4. Nginx 리버스 프록시 설정

### 4.1 Nginx 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/streamlit
```

**설정 내용:**
```nginx
server {
    listen 80;
    server_name hotel-demand-forecast.duckdns.org;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### 4.2 설정 활성화
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/

# 기본 사이트 비활성화 (선택사항)
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

### 4.3 Apache2 충돌 해결 (발생 시)
```bash
# Apache2가 80 포트 사용 중이면
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo systemctl start nginx
```

---

## 5. 도메인 및 SSL 설정

### 5.1 DuckDNS 설정
1. https://www.duckdns.org/ 접속
2. 계정 생성 (GitHub 로그인 가능)
3. 도메인 생성: `hotel-demand-forecast`
4. 서버 IP 입력: `3.37.159.57`

### 5.2 SSL 인증서 설치 (Let's Encrypt)
```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# SSL 인증서 발급 및 자동 설정
sudo certbot --nginx -d hotel-demand-forecast.duckdns.org

# 이메일 입력 및 약관 동의
# Nginx 설정 자동 변경 선택
```

### 5.3 자동 갱신 설정
```bash
# 인증서는 90일마다 갱신 필요
# Certbot이 자동으로 cron job 설정함
sudo certbot renew --dry-run  # 테스트
```

---

## 6. 자동 재시작 설정 (핵심!)

### 🚨 문제 상황
- Streamlit 앱이 자주 종료됨
- 502 Bad Gateway 에러 발생
- 수동으로 재시작해야 하는 불편함

### ✅ 해결 방법: systemd 서비스 등록

### 6.1 systemd 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/streamlit.service
```

**파일 내용:**
```ini
[Unit]
Description=Streamlit Hotel Forecast App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/streamlit_app
Environment="PATH=/home/ubuntu/streamlit_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ubuntu/streamlit_env/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**핵심 설정 설명:**
- `Restart=always`: 프로세스가 죽으면 자동 재시작
- `RestartSec=3`: 3초 후 재시작 시도
- `After=network.target`: 네트워크 활성화 후 시작
- `WantedBy=multi-user.target`: 서버 부팅 시 자동 시작

### 6.2 서비스 등록 및 시작
```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start streamlit

# 부팅 시 자동 시작 설정
sudo systemctl enable streamlit

# 상태 확인
sudo systemctl status streamlit
```

**정상 출력 예시:**
```
● streamlit.service - Streamlit Hotel Forecast App
   Loaded: loaded (/etc/systemd/system/streamlit.service; enabled)
   Active: active (running) since ...
```

### 6.3 기존 수동 실행 프로세스 정리
```bash
# 기존 Streamlit 프로세스 종료
pkill -f streamlit

# 또는
ps aux | grep streamlit
kill [PID]
```

---

## 7. 문제 해결 가이드

### 7.1 502 Bad Gateway 에러

**원인 1: Streamlit 프로세스 종료**
```bash
# 확인
sudo systemctl status streamlit

# 해결
sudo systemctl restart streamlit
```

**원인 2: Nginx 중지**
```bash
# 확인
sudo systemctl status nginx

# 해결
sudo systemctl restart nginx
```

**원인 3: 포트 충돌 (Apache2)**
```bash
# 확인
sudo lsof -i :80

# 해결
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo systemctl restart nginx
```

### 7.2 DNS_PROBE_FINISHED_NXDOMAIN

**원인: 도메인 DNS 문제**
```bash
# 로컬 PC에서 확인
nslookup hotel-demand-forecast.duckdns.org

# DuckDNS 설정 확인
# https://www.duckdns.org/ 에서 IP 재설정
```

### 7.3 SSH 접속 불가 (UPSTREAM_ERROR)

**원인: 인스턴스 문제**
```bash
# AWS Lightsail 콘솔에서 인스턴스 재부팅
# 인스턴스 → 점 3개 메뉴 → 재부팅

# systemd 서비스 설정했으면 자동으로 Streamlit 시작됨
```

### 7.4 Streamlit이 계속 죽는 경우

**원인: 메모리 부족**
```bash
# 메모리 확인
free -h

# 스왑 메모리 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 적용
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**원인: 앱 에러**
```bash
# 로그 확인
sudo journalctl -u streamlit -n 50
sudo journalctl -u streamlit -f  # 실시간
```

### 7.5 Nginx 설정 오류

```bash
# 설정 테스트
sudo nginx -t

# 에러 로그 확인
sudo tail -50 /var/log/nginx/error.log

# 재시작
sudo systemctl restart nginx
```

---

## 8. 유지보수 명령어

### 8.1 서비스 관리
```bash
# Streamlit 서비스
sudo systemctl status streamlit    # 상태 확인
sudo systemctl start streamlit     # 시작
sudo systemctl stop streamlit      # 중지
sudo systemctl restart streamlit   # 재시작
sudo systemctl enable streamlit    # 자동 시작 활성화
sudo systemctl disable streamlit   # 자동 시작 비활성화

# Nginx 서비스
sudo systemctl status nginx
sudo systemctl restart nginx
```

### 8.2 로그 확인
```bash
# Streamlit 로그 (실시간)
sudo journalctl -u streamlit -f

# Streamlit 로그 (최근 100줄)
sudo journalctl -u streamlit -n 100

# Nginx 에러 로그
sudo tail -50 /var/log/nginx/error.log

# Nginx 접속 로그
sudo tail -50 /var/log/nginx/access.log
```

### 8.3 프로세스 확인
```bash
# Streamlit 프로세스
ps aux | grep streamlit

# 포트 사용 확인
sudo netstat -tulpn | grep 8501
sudo lsof -i :8501

# 80, 443 포트
sudo netstat -tulpn | grep -E '80|443'
```

### 8.4 코드 업데이트
```bash
cd ~/streamlit_app

# Git에서 최신 코드 받기
git pull origin main

# 서비스 재시작
sudo systemctl restart streamlit

# 로그로 확인
sudo journalctl -u streamlit -f
```

### 8.5 시스템 리소스 모니터링
```bash
# 메모리 사용량
free -h

# CPU 사용량
top
# 또는
htop  # 설치 필요: sudo apt install htop

# 디스크 사용량
df -h

# 프로세스별 메모리
ps aux --sort=-%mem | head -10
```

---

## 9. 배포 체크리스트

### ✅ 초기 배포 시
- [ ] Lightsail 인스턴스 생성
- [ ] 고정 IP 할당
- [ ] 방화벽 설정 (22, 80, 443)
- [ ] SSH 접속 확인
- [ ] 시스템 업데이트
- [ ] Python, Nginx, Git 설치
- [ ] 프로젝트 클론
- [ ] 가상환경 생성 및 패키지 설치
- [ ] Nginx 리버스 프록시 설정
- [ ] DuckDNS 도메인 연결
- [ ] SSL 인증서 설치
- [ ] **systemd 서비스 등록** (가장 중요!)
- [ ] 브라우저 테스트

### ✅ 정기 점검 (주 1회)
- [ ] 서비스 상태 확인
- [ ] 로그 확인
- [ ] 디스크 용량 확인
- [ ] SSL 인증서 만료일 확인 (90일)
- [ ] 백업 확인

### ✅ 문제 발생 시
1. 브라우저에서 사이트 접속 안 됨
   - [ ] `sudo systemctl status streamlit`
   - [ ] `sudo systemctl status nginx`
   - [ ] `sudo systemctl restart streamlit`
   - [ ] `sudo systemctl restart nginx`

2. DNS 문제
   - [ ] `nslookup hotel-demand-forecast.duckdns.org`
   - [ ] DuckDNS 설정 확인

3. SSH 접속 안 됨
   - [ ] AWS 콘솔에서 인스턴스 상태 확인
   - [ ] 인스턴스 재부팅

---

## 10. 핵심 요약

### 🎯 성공적인 배포의 3대 핵심

#### 1️⃣ Nginx 리버스 프록시
```
사용자 → Nginx (80/443) → Streamlit (8501)
```
- HTTPS 암호화
- 도메인 연결
- 포트 변환

#### 2️⃣ systemd 서비스 (자동 재시작)
```ini
[Service]
Restart=always
RestartSec=3
```
- **Streamlit 죽어도 3초 후 자동 부활**
- **서버 재부팅 시 자동 시작**
- **더 이상 502 에러 걱정 없음**

#### 3️⃣ 모니터링 및 로그
```bash
sudo journalctl -u streamlit -f
```
- 실시간 문제 파악
- 빠른 대응

---

## 11. 자주 묻는 질문 (FAQ)

### Q1: 서버 재부팅하면 다시 설정해야 하나요?
**A:** 아니요! systemd 서비스로 등록했기 때문에 자동으로 시작됩니다.

### Q2: Streamlit이 자꾸 죽는데 어떻게 하나요?
**A:** 이 가이드의 **6. 자동 재시작 설정**을 따라 systemd 서비스를 등록하세요.

### Q3: 502 Bad Gateway 에러가 자주 나요.
**A:** 
1. `sudo systemctl status streamlit` 확인
2. `sudo systemctl restart streamlit`
3. systemd 서비스 등록 확인

### Q4: 코드를 수정하면 어떻게 반영하나요?
**A:**
```bash
cd ~/streamlit_app
git pull origin main
sudo systemctl restart streamlit
```

### Q5: 여러 Streamlit 앱을 동시에 운영하려면?
**A:** 포트를 다르게 설정하고 서비스 파일도 각각 만들어야 합니다.
```bash
# 앱1: streamlit-app1.service (포트 8501)
# 앱2: streamlit-app2.service (포트 8502)
# Nginx에서 각각 다른 도메인/경로로 라우팅
```

### Q6: 비용은 얼마나 드나요?
**A:**
- Lightsail: $5/월 (1GB 플랜)
- DuckDNS: 무료
- Let's Encrypt SSL: 무료
- **총 $5/월**

---

## 12. 참고 자료

### 공식 문서
- [AWS Lightsail](https://lightsail.aws.amazon.com/)
- [Streamlit](https://docs.streamlit.io/)
- [Nginx](https://nginx.org/en/docs/)
- [systemd](https://www.freedesktop.org/wiki/Software/systemd/)
- [DuckDNS](https://www.duckdns.org/)
- [Let's Encrypt](https://letsencrypt.org/)

### 유용한 링크
- Streamlit 커뮤니티: https://discuss.streamlit.io/
- Nginx 설정 생성기: https://nginxconfig.io/
- SSL 테스트: https://www.ssllabs.com/ssltest/

---

## 13. 버전 히스토리

| 날짜 | 버전 | 변경사항 |
|------|------|----------|
| 2025-10-19 | 1.0 | 초기 배포 완료 |
| 2025-10-22 | 1.1 | systemd 자동 재시작 설정 추가 |
| 2025-10-22 | 1.2 | Apache2 충돌 문제 해결 추가 |

---

## 📞 문제 해결이 안 되면?

1. **로그 확인**: `sudo journalctl -u streamlit -n 100`
2. **서비스 상태**: `sudo systemctl status streamlit nginx`
3. **프로세스 확인**: `ps aux | grep streamlit`
4. **포트 확인**: `sudo netstat -tulpn | grep -E '80|443|8501'`

그래도 안 되면 이 문서를 보고 처음부터 다시 확인하세요! 💪

---

**작성자**: 박아진  
**프로젝트**: 호텔 객실 수요 예측 시스템  
**최종 수정**: 2025년 10월 22일  
**라이선스**: MIT

---

이 가이드가 도움이 되셨다면 ⭐ 스타 부탁드립니다!