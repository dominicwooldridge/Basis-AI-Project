from pydantic import BaseModel, Field

class ProjectIntake(BaseModel):
    # ... other fields ...
    prevailing_wage_compliant: bool = Field(
        description="Developer confirms Davis-Bacon wage rates will be paid "
                    "to all construction and maintenance workers"
    )
    apprenticeship_compliant: bool = Field(
        description="Developer confirms 10-15% of labor hours will be "
                    "performed by registered apprentices"
    )