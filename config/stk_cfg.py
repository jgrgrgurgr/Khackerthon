import os
from typing import List

class StkCfg:
    UPD_INT: int = int(os.getenv("UPD_INT", "10"))
    
    KR_STKS: List[dict] = [
        {"sym": "005930.KS", "name": "삼성전자", "desc": "반도체, 전자제품 제조업체"},
        {"sym": "000660.KS", "name": "SK하이닉스", "desc": "메모리 반도체 전문기업"},
        {"sym": "035420.KS", "name": "NAVER", "desc": "인터넷 포털 및 IT 서비스"},
        {"sym": "005380.KS", "name": "현대차", "desc": "자동차 제조업체"},
        {"sym": "006400.KS", "name": "삼성SDI", "desc": "배터리 및 전자소재"},
        {"sym": "035720.KS", "name": "카카오", "desc": "모바일 플랫폼 및 콘텐츠 서비스"},
        {"sym": "051910.KS", "name": "LG화학", "desc": "화학 및 배터리 소재"},
        {"sym": "068270.KS", "name": "셀트리온", "desc": "바이오의약품 개발"},
        {"sym": "207940.KS", "name": "삼성바이오로직스", "desc": "바이오의약품 위탁생산"},
        {"sym": "373220.KS", "name": "LG에너지솔루션", "desc": "배터리 전문기업"},
        {"sym": "005490.KS", "name": "POSCO홀딩스", "desc": "철강 제조업체"},
        {"sym": "000270.KS", "name": "기아", "desc": "자동차 제조업체"},
        {"sym": "055550.KS", "name": "신한지주", "desc": "금융지주회사"},
        {"sym": "105560.KS", "name": "KB금융", "desc": "금융지주회사"},
        {"sym": "032830.KS", "name": "삼성생명", "desc": "생명보험회사"}
    ]