class RequestData:
    """
    API 요청을 위한 데이터 클래스입니다.

    Args:
        messages: 프롬프트나 이전 대화 내용
        temperature (float): 생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성), 0.00 < temperature <= 1 (기본값: 0.50)
        topP (float): 생성 토큰 후보군을 누적 확률을 기반으로 샘플링, 0 < topP <= 1 (기본값: 0.8)
        topK (int): 생성 토큰 후보군에서 확률이 높은 k개를 후보로 지정하여 샘플링, 0 <= topK <= 128 (기본값: 0)
        repeatPenalty (float): 같은 토큰을 생성하는 것에 대한 패널티 정도(설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소), 0 < repeatPenalty <= 10 (기본값: 5.0)
        maxTokens (int): 생성 토큰 후보군에서 확률이 높은 k개를 후보로 지정하여 샘플링
        stopBefore (list[str]): 토큰 생성 중단 문자, (기본값: [])
        includeAiFilters (bool): 생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱 /음란 등 카테고리별로 해당하는 정도, (기본값: True)
        seed (int): 0일 때 일관성 수준이 랜덤 적용 (기본값: 0), 사용자 지정 seed 범위: 1 <= seed <= 4294967295
    """

    def __init__(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        topP: float = 0.8,
        topK: int = 0,
        maxTokens: int = 256,
        repeatPenalty: float = 5.0,
        stopBefore: list[str] = [],
        includeAiFilters: bool = True,
        seed: int = 0,
    ) -> None:
        self.messages = messages
        self.topP = topP
        self.topK = topK
        self.maxTokens = maxTokens
        self.temperature = temperature
        self.repeatPenalty = repeatPenalty
        self.stopBefore = stopBefore
        self.includeAiFilters = includeAiFilters
        self.seed = seed

    def to_dict(self) -> dict:
        return {
            "messages": self.messages,
            "topP": self.topP,
            "topK": self.topK,
            "maxTokens": self.maxTokens,
            "temperature": self.temperature,
            "repeatPenalty": self.repeatPenalty,
            "stopBefore": self.stopBefore,
            "includeAiFilters": self.includeAiFilters,
            "seed": self.seed,
        }
