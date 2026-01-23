# generation/query_processor.py

class QueryProcessor:
    """
    Fast dictionary-based query expansion for power grid domain
    Falls back to LLM only for complex queries
    """
    
    # Comprehensive bilingual expansions
    KEYWORD_MAP = {
        # English technical terms
        "transformer": "변압기 substation voltage equipment insulating oil",
        "renewable energy": "재생에너지 신재생 solar wind VRE variable",
        "HVDC": "직류송전 high voltage direct current transmission VSC LCC BTB",
        "grid": "전력망 송전망 배전망 power system network transmission distribution",
        "stability": "안정도 frequency voltage control dynamic",
        "ESS": "에너지저장 energy storage battery BESS",
        "inverter": "인버터 converter grid-forming grid-following",
        "transmission": "송전 송전선로 765kV 345kV line tower conductor",
        "distribution": "배전 DC AC system network",
        "generator": "발전 발전기 synchronous turbine power plant",
        "market": "시장 전력시장 SMP CBP electricity trading",
        "smart grid": "스마트그리드 지능형전력망 automation SCADA",
        "nuclear": "원자력 nuclear power plant reactor",
        "coal": "석탄 coal plant thermal",
        "curtailment": "출력제한 제약 curtailment limitation",
        
        # Korean technical terms
        "재생에너지": "renewable solar wind VRE 태양광 풍력",
        "전력망": "grid power system 송전망 배전망 transmission",
        "변압기": "transformer substation 변전소 voltage",
        "송전": "transmission line 송전선로 765kV 345kV HVDC",
        "안정도": "stability frequency voltage control 주파수 전압",
        "에너지저장": "ESS energy storage battery BESS 배터리",
        "전력시장": "electricity market SMP CBP trading 거래",
        "한전": "KEPCO KPX 전력거래소 utility",
        "스마트그리드": "smart grid automation 자동화 SCADA DAS",
        "제주": "Jeju island 해남 HVDC interconnection",
        "동기조상기": "synchronous condenser compensator reactive",
        "출력제한": "curtailment limitation VRE constraint",
        "전력수급": "electricity supply demand BPLE planning",
        
        # Specific entities
        "KPX": "전력거래소 Korea Power Exchange market operator KEPCO",
        "KEPCO": "한전 Korea Electric Power utility transmission",
        "insulating oil": "절연유 transformer oil dielectric",
        "PyPSA": "power system analysis toolbox optimization",
        "765kV": "transmission line 송전선로 ultra high voltage",
        "CBP": "cost-based pool 비용기반풀 market pricing SMP",
        "SMP": "system marginal price 계통한계가격 market",
        "EMSC": "전력시장감시위원회 market monitoring surveillance",
        "SCADA": "supervisory control 감시제어 automation DAS",
        "VRE": "variable renewable energy 변동성재생에너지 solar wind",
        "BPLE": "전력수급기본계획 basic plan electricity supply demand",
    }
    
    def __init__(self):
        pass  # No LLM needed for fast dictionary expansion
    
    def expand_query(self, original_query: str) -> str:
        """
        Fast dictionary-based expansion with bilingual support
        """
        expanded_terms = set()
        query_lower = original_query.lower()
        
        # Check each keyword in our dictionary
        for keyword, expansion in self.KEYWORD_MAP.items():
            # Match both case-insensitive and exact (for Korean)
            if keyword.lower() in query_lower or keyword in original_query:
                # Add expansion terms (max 3 to avoid query bloat)
                expansion_terms = expansion.split()[:3]
                for term in expansion_terms:
                    # Don't add if already in query
                    if term.lower() not in query_lower and term not in original_query:
                        expanded_terms.add(term)
        
        # Combine original + expansions
        if expanded_terms:
            expanded_query = f"{original_query} {' '.join(list(expanded_terms)[:5])}"  # Limit to 5 new terms
            return expanded_query
        
        return original_query