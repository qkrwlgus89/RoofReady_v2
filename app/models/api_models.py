from typing import Optional
from pydantic import BaseModel, Field


class AptAnnouncementRaw(BaseModel):
    """
    한국부동산원 청약홈 분양정보 조회 서비스 응답 필드.
    (data.go.kr 15098547 / api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail)
    필드명은 모두 대문자 스네이크 케이스.
    """

    # 공고 식별
    PBLANC_NO: Optional[str] = Field(None, description="공고번호")
    HOUSE_MANAGE_NO: Optional[str] = Field(None, description="주택관리번호")
    PBLANC_URL: Optional[str] = Field(None, description="청약홈 공고 상세 URL (PDF 진입점)")

    # 단지명 / 사업 주체
    HOUSE_NM: Optional[str] = Field(None, description="주택명(단지명)")
    BSNS_MBY_NM: Optional[str] = Field(None, description="사업주체명")
    CNSTRCT_ENTRPS_NM: Optional[str] = Field(None, description="건설업체명")
    MDHS_TELNO: Optional[str] = Field(None, description="문의처 전화번호")
    HMPG_ADRES: Optional[str] = Field(None, description="홈페이지주소")
    NSPRC_NM: Optional[str] = Field(None, description="신문사명")

    # 주택 구분
    HOUSE_SECD: Optional[str] = Field(None, description="주택구분코드")
    HOUSE_SECD_NM: Optional[str] = Field(None, description="주택구분명 (APT 등)")
    HOUSE_DTL_SECD: Optional[str] = Field(None, description="주택상세구분코드")
    HOUSE_DTL_SECD_NM: Optional[str] = Field(None, description="주택상세구분명 (민영/공공 등)")
    RENT_SECD: Optional[str] = Field(None, description="분양/임대 구분코드")
    RENT_SECD_NM: Optional[str] = Field(None, description="분양/임대 구분명")

    # 공급 위치
    HSSPLY_ADRES: Optional[str] = Field(None, description="공급위치(주소)")
    HSSPLY_ZIP: Optional[str] = Field(None, description="공급위치 우편번호")
    SUBSCRPT_AREA_CODE: Optional[str] = Field(None, description="공급지역코드")
    SUBSCRPT_AREA_CODE_NM: Optional[str] = Field(None, description="공급지역명")

    # 공급 세대 (API가 int로 반환)
    TOT_SUPLY_HSHLDCO: Optional[int] = Field(None, description="총공급세대수")

    # 주요 일정 (YYYY-MM-DD)
    RCRIT_PBLANC_DE: Optional[str] = Field(None, description="모집공고일")
    PRZWNER_PRESNATN_DE: Optional[str] = Field(None, description="당첨자발표일")
    CNTRCT_CNCLS_BGNDE: Optional[str] = Field(None, description="계약시작일")
    CNTRCT_CNCLS_ENDDE: Optional[str] = Field(None, description="계약종료일")
    MVN_PREARNGE_YM: Optional[str] = Field(None, description="입주예정월 (YYYYMM)")

    # 청약 접수 기간
    RCEPT_BGNDE: Optional[str] = Field(None, description="청약접수시작일")
    RCEPT_ENDDE: Optional[str] = Field(None, description="청약접수종료일")

    # 특별공급 접수 기간
    SPSPLY_RCEPT_BGNDE: Optional[str] = Field(None, description="특별공급 접수시작일")
    SPSPLY_RCEPT_ENDDE: Optional[str] = Field(None, description="특별공급 접수종료일")

    # 일반공급 순위별 접수 일정
    GNRL_RNK1_CRSPAREA_RCPTDE: Optional[str] = Field(None, description="일반 1순위 해당지역 접수일")
    GNRL_RNK1_CRSPAREA_ENDDE: Optional[str] = Field(None, description="일반 1순위 해당지역 접수종료일")
    GNRL_RNK1_ETC_AREA_RCPTDE: Optional[str] = Field(None, description="일반 1순위 기타지역 접수일")
    GNRL_RNK1_ETC_AREA_ENDDE: Optional[str] = Field(None, description="일반 1순위 기타지역 접수종료일")
    GNRL_RNK2_CRSPAREA_RCPTDE: Optional[str] = Field(None, description="일반 2순위 해당지역 접수일")
    GNRL_RNK2_CRSPAREA_ENDDE: Optional[str] = Field(None, description="일반 2순위 해당지역 접수종료일")
    GNRL_RNK2_ETC_AREA_RCPTDE: Optional[str] = Field(None, description="일반 2순위 기타지역 접수일")
    GNRL_RNK2_ETC_AREA_ENDDE: Optional[str] = Field(None, description="일반 2순위 기타지역 접수종료일")

    # 기타 속성
    LRSCL_BLDLND_AT: Optional[str] = Field(None, description="대규모 택지개발지구 여부")
    NPLN_PRVOPR_PUBLIC_HOUSE_AT: Optional[str] = Field(None, description="수도권 내 민영주택 여부")
    PARCPRC_ULS_AT: Optional[str] = Field(None, description="분양가상한제 적용 여부")
    IMPRMN_BSNS_AT: Optional[str] = Field(None, description="정비사업 여부")
    PUBLIC_HOUSE_EARTH_AT: Optional[str] = Field(None, description="공공주택지구 여부")
    MDAT_TRGET_AREA_SECD: Optional[str] = Field(None, description="투기과열지구/조정대상지역 여부")
    SPECLT_RDN_EARTH_AT: Optional[str] = Field(None, description="투기과열지구 여부")
    PUBLIC_HOUSE_SPCLW_APPLC_AT: Optional[str] = Field(None, description="공공주택특별법 적용 여부")
