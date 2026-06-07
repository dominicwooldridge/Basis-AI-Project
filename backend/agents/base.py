from abc import ABC, abstractmethod
from langchain_aws import ChatBedrock
import boto3


class BaseAgent(ABC):
    def __init__(self):
        session = boto3.Session(profile_name="GSB570-BedrockOnly-490332585640")
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-5-haiku-20241022-v1:0",
            client=session.client("bedrock-runtime", region_name="us-west-2"),
            model_kwargs={"temperature": 0}
        )

    @abstractmethod
    async def run(self, **kwargs):
        pass
