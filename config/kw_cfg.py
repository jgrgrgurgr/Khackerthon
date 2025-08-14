import os
from typing import Optional

class KwCfg:
    KIS_KEY: Optional[str] = os.getenv("KIS_KEY")
    KIS_SEC: Optional[str] = os.getenv("KIS_SEC") 
    KIS_URL: str = "https://openapi.koreainvestment.com:9443"
    
    KW_ACC: Optional[str] = os.getenv("KW_ACC")
    
    UPD_INT: int = int(os.getenv("UPD_INT", "5"))