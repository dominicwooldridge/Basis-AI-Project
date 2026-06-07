from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    AWS_PROFILE: str = os.getenv("AWS_PROFILE")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")
    NREL_API_KEY: str = os.getenv("NREL_API_KEY")
    EIA_API_KEY: str = os.getenv("EIA_API_KEY")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.NREL_API_KEY:
            missing.append("NREL_API_KEY")
        if not cls.EIA_API_KEY:
            missing.append("EIA_API_KEY")
        if not cls.AWS_PROFILE:
            missing.append("AWS_PROFILE")
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


config = Config()
