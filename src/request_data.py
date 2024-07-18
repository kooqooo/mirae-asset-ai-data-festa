from typing import List


class RequestData:
    """
    ChatCompletions API 요청을 위한 데이터 클래스입니다.

    Args:
        messages: 프롬프트나 이전 대화 내용
        temperature (float): 생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성), 0.00 < temperature <= 1 (기본값: 0.50)
        topP (float): 생성 토큰 후보군을 누적 확률을 기반으로 샘플링, 0 < topP <= 1 (기본값: 0.8)
        topK (int): 생성 토큰 후보군에서 확률이 높은 k개를 후보로 지정하여 샘플링, 0 <= topK <= 128 (기본값: 0)
        repeatPenalty (float): 같은 토큰을 생성하는 것에 대한 패널티 정도(설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소), 0 < repeatPenalty <= 10 (기본값: 5.0)
        maxTokens (int): 최대 생성 토큰 수, 0 <= maxTokens <= 4096 (기본값: 100)
        stopBefore (list[str]): 토큰 생성 중단 문자, (기본값: [])
        includeAiFilters (bool): 생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱 /음란 등 카테고리별로 해당하는 정도, (기본값: True)
        seed (int): 0일 때 일관성 수준이 랜덤 적용 (기본값: 0), 사용자 지정 seed 범위: 1 <= seed <= 4294967295
    """

    def __init__(
        self,
        messages: List[dict[str, str]],
        temperature: float = 0.1,
        topP: float = 0.8,
        topK: int = 0,
        maxTokens: int = 256,
        repeatPenalty: float = 5.0,
        stopBefore: List[str] = [],
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


class SegmentationRequestData:
    """
    Segmentation API 요청을 위한 데이터 클래스입니다.
    
    Args:
        text (str): 문단 나누기를 수행할 문서, 1~120,000자(한글 기준, 공백 포함)
        segCnt (int): 원하는 문단 나누기 수, 1 <= segCount, -1 == segCount (-1로 설정 시 모델이 최적 문단 수로 분리) (기본값: -1)
        alpha (float): 문단 나누기를 위한 thresholds 값, 클수록 나눠지는 문단 수 증가, -1.5 <= alpha <=1.5, -100 == alpha(모델의 최적값으로 자동 수행) (기본값: 0.0)
        postProcess (bool): 문단 나누기 수행 후 원하는 길이로 문단을 합치거나 나누는 후처리 수행 여부 (기본값: False)
        postProcessMaxSize (int): post process module 적용 시 문단에 포함되는 문자열의 최대 글자 수, 1 <= postProcessMaxSize (기본값: 1000)
        postProcessMinSize (int): post process module 적용 시 문단에 포함되는 문자열의 최소 글자 수, 0 <= postProcessMinSize <= postProcessMaxSize (기본값: 300)
    """
    
    def __init__(
        self,
        text: List[str],
        segCnt: int = -1,
        alpha: float = 0.0,
        postProcess: bool = False,
        postProcessMaxSize: int = 1000,
        postProcessMinSize: int = 300,
    ) -> None:
        self.text = text
        self.segCnt = segCnt
        self.alpha = alpha
        self.postProcess = postProcess
        self.postProcessMaxSize = postProcessMaxSize
        self.postProcessMinSize = postProcessMinSize
        
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "segCnt": self.segCnt,
            "alpha": self.alpha,
            "postProcess": self.postProcess,
            "postProcessMaxSize": self.postProcessMaxSize,
            "postProcessMinSize": self.postProcessMinSize,
        }
        
class SlidingWindowRequestData:
    def __init__(self, messages: List[dict], max_tokens: int=200) -> None:
        self.messages = messages
        self.max_tokens = max_tokens
        
    def to_dict(self) -> dict:
        return {
            "maxTokens": self.max_tokens,
            "messages": self.messages,
        }
        
class SummaryRequestData:
    def __init__(
        self,
        texts: List[str],
        autoSentenceSplitter: bool=True,
        segCount: int=-1,
        segMinSize: int=300,
        segMaxSize: int=1000,
        includeAiFilters: bool=True,
    ) -> None:
        self.texts = texts
        self.autoSentenceSplitter = autoSentenceSplitter
        self.segCount = segCount
        self.segMinSize = segMinSize
        self.segMaxSize = segMaxSize
        self.includeAiFilters = includeAiFilters
        
    def to_dict(self) -> dict:
        return {
            "texts": self.texts,
            "autoSentenceSplitter": self.autoSentenceSplitter,
            "segCount": self.segCount,
            "segMinSize": self.segMinSize,
            "segMaxSize": self.segMaxSize,
            "includeAiFilters": self.includeAiFilters
        }
