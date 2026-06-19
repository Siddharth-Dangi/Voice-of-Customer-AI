import pandas as pd
import re
from typing import Dict, Any, List

def clean_text(text: str) -> str:
    """Cleans raw feedback text by removing excessive whitespace and unprintable characters."""
    if not isinstance(text, str):
        return ""
    # Remove control characters and clean whitespaces
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_uploaded_file(file, filename: str) -> pd.DataFrame:
    """Parses Streamlit uploaded file (CSV, XLSX, TXT) into a Pandas DataFrame."""
    if filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    elif filename.endswith(".txt"):
        # Streamlit files are file-like, need to read bytes and decode
        bytes_data = file.read()
        content = bytes_data.decode("utf-8", errors="ignore")
        # Split by double newline first (paragraphs) to group cohesive feedback block, 
        # otherwise split by single newline.
        if "\n\n" in content:
            items = [item.strip() for item in content.split("\n\n") if item.strip()]
        else:
            items = [item.strip() for item in content.split("\n") if item.strip()]
        df = pd.DataFrame({"feedback_text": items})
    else:
        raise ValueError("Unsupported file format. Please upload CSV, XLSX, or TXT.")
    
    return df

def calculate_aggregate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Aggregates feedback and analysis results to generate dashboard metrics."""
    if df.empty:
        return {
            "total_feedback": 0,
            "sentiment_distribution": {"Positive": 0, "Neutral": 0, "Negative": 0},
            "category_distribution": {},
            "top_pain_points": [],
            "top_feature_requests": [],
            "sample_positive": [],
            "sample_negative": [],
            "sample_neutral": []
        }
        
    # Sentiment distribution
    sentiment_dist = df["sentiment"].value_counts().to_dict()
    # Backfill missing keys
    for sent in ["Positive", "Neutral", "Negative"]:
        if sent not in sentiment_dist:
            sentiment_dist[sent] = 0
            
    # Category distribution
    category_dist = df["category"].value_counts().to_dict()
    
    # Aggregate specific pain points
    all_pain_points = []
    for p_list in df["pain_points"]:
        all_pain_points.extend([clean_text(p) for p in p_list if p])
    
    # Frequency count
    pain_counts = pd.Series(all_pain_points).value_counts().to_dict()
    top_pain_points = sorted(pain_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Aggregate specific feature requests
    all_feature_requests = []
    for f_list in df["feature_requests"]:
        all_feature_requests.extend([clean_text(f) for f in f_list if f])
        
    feat_counts = pd.Series(all_feature_requests).value_counts().to_dict()
    top_feature_requests = sorted(feat_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Representative samples
    sample_pos = df[df["sentiment"] == "Positive"]["feedback_text"].head(5).tolist()
    sample_neg = df[df["sentiment"] == "Negative"]["feedback_text"].head(5).tolist()
    sample_neu = df[df["sentiment"] == "Neutral"]["feedback_text"].head(5).tolist()
    
    return {
        "total_feedback": len(df),
        "sentiment_distribution": sentiment_dist,
        "category_distribution": category_dist,
        "top_pain_points": top_pain_points,
        "top_feature_requests": top_feature_requests,
        "sample_positive": sample_pos,
        "sample_negative": sample_neg,
        "sample_neutral": sample_neu
    }
