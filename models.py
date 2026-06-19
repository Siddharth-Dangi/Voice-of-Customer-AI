from pydantic import BaseModel, Field
from typing import List, Optional

class FeedbackItemAnalysis(BaseModel):
    id: int = Field(description="The unique identifier matching the feedback item")
    sentiment: str = Field(description="Sentiment classification: Positive, Neutral, or Negative")
    sentiment_score: float = Field(description="Sentiment score between -1.0 (very negative) and 1.0 (very positive)")
    category: str = Field(description="Category classification: Product Quality, Pricing, User Experience, Support, Performance, Feature Requests")
    pain_points: List[str] = Field(default=[], description="List of specific complaints or pain points identified in this feedback")
    feature_requests: List[str] = Field(default=[], description="List of specific feature requests identified in this feedback")
    opportunity_score: float = Field(default=0.0, description="Score from 0 to 100 on how much of an opportunity this feedback represents (higher means more potential for improvement)")
    business_impact_score: float = Field(default=0.0, description="Score from 0 to 100 on the business impact of addressing this feedback (higher means more impact)")

class BatchAnalysisResult(BaseModel):
    analyses: List[FeedbackItemAnalysis]

class CustomerPersona(BaseModel):
    name: str = Field(description="The name of the persona, e.g., 'Power User', 'Frustrated Customer'")
    description: str = Field(description="A brief description of this customer profile")
    pain_points: List[str] = Field(description="Top pain points for this persona")
    needs: List[str] = Field(description="Key needs and requirements for this persona")

class ExecutiveSummaryResult(BaseModel):
    key_findings: List[str] = Field(description="Top key findings summarized from the customer feedback")
    overall_sentiment_summary: str = Field(description="A summary paragraph of the customer sentiment trends")
    top_complaints_summary: str = Field(description="A summary paragraph of the top complaints and pain points")
    product_recommendations: List[str] = Field(description="Ranked product recommendations based on customer needs")
    growth_opportunities: List[str] = Field(description="Growth opportunities identified from underserved needs")
    personas: List[CustomerPersona] = Field(description="List of customer personas generated from feedback patterns")
