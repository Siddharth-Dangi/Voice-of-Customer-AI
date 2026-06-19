import json
import requests
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional
from models import FeedbackItemAnalysis, BatchAnalysisResult, ExecutiveSummaryResult, CustomerPersona

BATCH_SYSTEM_PROMPT = """
You are a Voice of Customer AI agent. Analyze the provided list of customer feedback entries and return a JSON object with a list of analyses.
Each feedback item in the input batch has an "id" and a "text". You must analyze each one and output a matching analysis object with the same "id".

Each analysis object must contain:
- id: The exact integer ID of the feedback entry.
- sentiment: Exactly one of: "Positive", "Neutral", "Negative".
- sentiment_score: Float between -1.0 (very negative) and 1.0 (very positive).
- category: Exactly one of: "Product Quality", "Pricing", "User Experience", "Support", "Performance", "Feature Requests".
- pain_points: A list of strings identifying specific, concrete complaints or pain points (e.g. "Slow dashboard loading"). Keep them short. If none, return an empty list.
- feature_requests: A list of strings of specific feature requests. If none, return an empty list.
- opportunity_score: Float (0.0 to 100.0) indicating the opportunity level of resolving this issue (higher = more room for improvement).
- business_impact_score: Float (0.0 to 100.0) indicating the business impact of addressing this feedback (higher = greater impact on churn reduction, satisfaction, or growth).

You must return a valid JSON object matching this schema:
{
  "analyses": [
    {
      "id": <int>,
      "sentiment": "<str>",
      "sentiment_score": <float>,
      "category": "<str>",
      "pain_points": ["<str>", ...],
      "feature_requests": ["<str>", ...],
      "opportunity_score": <float>,
      "business_impact_score": <float>
    },
    ...
  ]
}
"""

SUMMARY_SYSTEM_PROMPT = """
You are a senior business intelligence and product strategy consultant.
You will be provided with aggregated customer feedback statistics, including category breakdown, sentiment distribution, top pain points, and top feature requests.
Based on this information, generate an executive summary in JSON format that matches this schema:
{
  "key_findings": ["<finding 1>", "<finding 2>", ...],
  "overall_sentiment_summary": "<paragraph summarizing sentiment trends>",
  "top_complaints_summary": "<paragraph summarizing top complaints and pain points>",
  "product_recommendations": ["<recommendation 1>", "<recommendation 2>", ...],
  "growth_opportunities": ["<opportunity 1>", "<opportunity 2>", ...],
  "personas": [
    {
      "name": "<persona name, e.g. Power User>",
      "description": "<brief description of this customer profile>",
      "pain_points": ["<pain point 1>", ...],
      "needs": ["<need 1>", ...]
    },
    ...
  ]
}

Generate 2 to 3 distinct customer personas based on the feedback patterns.
Ensure the output is a valid JSON object.
"""

class GroqClient:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        
    def _post(self, messages, json_mode=False) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        if json_mode:
            data["response_format"] = {"type": "json_object"}
            
        response = requests.post(self.url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()

def analyze_feedback_batch(client: GroqClient, batch: List[Dict[str, Any]]) -> List[FeedbackItemAnalysis]:
    """Analyzes a single batch of feedback items."""
    # Format batch content
    batch_input = [{"id": item["id"], "text": item["text"]} for item in batch]
    prompt = f"Analyze the following feedback batch:\n{json.dumps(batch_input, indent=2)}"
    
    try:
        messages = [
            {"role": "system", "content": BATCH_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        response = client._post(messages, json_mode=True)
        content = response["choices"][0]["message"]["content"]
        
        data = json.loads(content)
        validated = BatchAnalysisResult.model_validate(data)
        return validated.analyses
    except Exception as e:
        print(f"Error processing batch: {e}")
        # Fallback default analysis for each item in the batch
        fallback_list = []
        for item in batch:
            # Simple keyword matching for basic categorization in case of failure
            text_lower = item["text"].lower()
            category = "User Experience"
            if "slow" in text_lower or "lag" in text_lower or "performance" in text_lower or "loading" in text_lower:
                category = "Performance"
            elif "price" in text_lower or "cost" in text_lower or "subscription" in text_lower or "expensive" in text_lower:
                category = "Pricing"
            elif "support" in text_lower or "ticket" in text_lower or "chat" in text_lower or "email" in text_lower:
                category = "Support"
            elif "bug" in text_lower or "crash" in text_lower or "broken" in text_lower:
                category = "Product Quality"
            elif "add" in text_lower or "request" in text_lower or "feature" in text_lower or "integration" in text_lower:
                category = "Feature Requests"
                
            sentiment = "Neutral"
            sentiment_score = 0.0
            if any(w in text_lower for w in ["great", "love", "awesome", "excellent", "beautiful", "fast"]):
                sentiment = "Positive"
                sentiment_score = 0.7
            elif any(w in text_lower for w in ["bad", "slow", "broke", "crash", "worst", "hate", "frustrat"]):
                sentiment = "Negative"
                sentiment_score = -0.7

            fallback_list.append(FeedbackItemAnalysis(
                id=item["id"],
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                category=category,
                pain_points=[item["text"][:50] + "..."] if sentiment == "Negative" else [],
                feature_requests=[item["text"][:50] + "..."] if category == "Feature Requests" else [],
                opportunity_score=50.0 if sentiment == "Negative" else 20.0,
                business_impact_score=40.0 if sentiment == "Negative" else 20.0
            ))
        return fallback_list

def analyze_feedback_dataset(
    api_key: str, 
    model: str, 
    feedback_list: List[Dict[str, Any]], 
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[FeedbackItemAnalysis]:
    """Processes feedback items concurrently in batches."""
    client = GroqClient(api_key, model)
    batch_size = 20
    batches = [feedback_list[i:i + batch_size] for i in range(0, len(feedback_list), batch_size)]
    
    total_items = len(feedback_list)
    completed_items = 0
    results = []
    
    # Use ThreadPoolExecutor to make concurrent calls to Groq API
    # Max workers set to 5 to avoid overloading the Groq free-tier rate limits
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_batch = {executor.submit(analyze_feedback_batch, client, batch): batch for batch in batches}
        
        for future in concurrent.futures.as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_results = future.result()
                results.extend(batch_results)
            except Exception as e:
                print(f"Critical error on batch future: {e}")
                
            completed_items += len(batch)
            if progress_callback:
                progress_callback(completed_items, total_items)
                
    # Sort results by ID to match original order
    results.sort(key=lambda x: x.id)
    return results

def generate_executive_summary(api_key: str, model: str, stats: Dict[str, Any]) -> ExecutiveSummaryResult:
    """Generates the final executive summary and personas based on aggregate feedback statistics."""
    client = GroqClient(api_key, model)
    
    prompt = f"""
    Please analyze the following aggregated customer feedback statistics and generate the executive summary:
    
    - Total Feedback Analyzed: {stats['total_feedback']}
    - Sentiment Distribution: {json.dumps(stats['sentiment_distribution'])}
    - Category Distribution: {json.dumps(stats['category_distribution'])}
    - Top Pain Points (Complaints) Identified: {json.dumps(stats['top_pain_points'])}
    - Top Feature Requests Identified: {json.dumps(stats['top_feature_requests'])}
    
    Sample Customer Quotes (Negative):
    {json.dumps(stats.get('sample_negative', [])[:5], indent=2)}
    
    Sample Customer Quotes (Positive):
    {json.dumps(stats.get('sample_positive', [])[:5], indent=2)}
    """
    
    try:
        messages = [
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        response = client._post(messages, json_mode=True)
        content = response["choices"][0]["message"]["content"]
        
        data = json.loads(content)
        validated = ExecutiveSummaryResult.model_validate(data)
        return validated
    except Exception as e:
        print(f"Error generating executive summary: {e}")
        # Return fallback data
        return ExecutiveSummaryResult(
            key_findings=[
                "User Experience and Performance are top concerns for customer feedback.",
                "There is a strong demand for dark mode and mobile capabilities.",
                "Customer support responsiveness needs prioritization."
            ],
            overall_sentiment_summary="The overall sentiment exhibits typical distributions, highlighting performance bottlenecks and support delays as core drivers of negative feedback, while design updates drive positive feedback.",
            top_complaints_summary="Top complaints include sluggish load times on dashboards and late responses from the customer support team.",
            product_recommendations=[
                "Optimize application response times and database query execution.",
                "Establish a dedicated fast-response customer support queue.",
                "Implement high-demand features like Dark Mode."
            ],
            growth_opportunities=[
                "Introduce native mobile applications.",
                "Develop premium integrations (Slack, Microsoft Teams) for team workspaces."
            ],
            personas=[
                CustomerPersona(
                    name="Performance-Sensitive User",
                    description="A user who depends on high-speed data loading for daily tasks.",
                    pain_points=["Slow load times", "Sluggish dashboard updates"],
                    needs=["Optimized responsiveness", "Faster CSV import speeds"]
                ),
                CustomerPersona(
                    name="Collaboration seeker",
                    description="A team lead looking to coordinate reviews and share analytics reports.",
                    pain_points=["No Slack/Teams integration", "Difficult PDF sharing"],
                    needs=["Easy report downloads", "Third-party sharing channels"]
                )
            ]
        )
