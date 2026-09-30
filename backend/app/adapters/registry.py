"""구체 어댑터 생성과 등록은 이 파일에만 둔다."""

from app.adapters.ai.base import ImageGenerator, TextGenerator
from app.adapters.ai.image import OpenAIImage
from app.adapters.ai.mock import MockImage, MockText
from app.adapters.ai.text import OpenAIText
from app.adapters.http import SourceHTTP
from app.adapters.sources.base import SourceAdapter
from app.adapters.sources.domeggook import DomeggookAdapter
from app.adapters.sources.mock import MockSource
from app.core.config import Config


class Registry:
    def __init__(self, config: Config) -> None:
        self.http = SourceHTTP(config)
        self.sources: list[SourceAdapter] = (
            [MockSource()]
            if config.source_mode == "mock"
            else [DomeggookAdapter(config, self.http)]
        )
        self.text: TextGenerator = MockText() if config.ai_mode == "mock" else OpenAIText(config)
        self.image: ImageGenerator = (
            MockImage(config) if config.ai_mode == "mock" else OpenAIImage(config)
        )

    def source_for(self, url: str) -> SourceAdapter | None:
        return next((adapter for adapter in self.sources if adapter.matches(url)), None)
