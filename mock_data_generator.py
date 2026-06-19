import csv
import random
import argparse
from datetime import datetime, timedelta

# Sample customer feedback templates
FEEDBACK_TEMPLATES = [
    # Performance
    ("Performance", "Negative", "The loading time for the main analytics dashboard is extremely slow. It takes over 10 seconds to load."),
    ("Performance", "Negative", "I keep getting timeout errors when running reports for large date ranges. The app feels sluggish."),
    ("Performance", "Negative", "CPU usage spikes to 100% every time I open the editor. It lags my entire computer."),
    ("Performance", "Positive", "The new update made the page transition so smooth and fast. Loads instantly now!"),
    ("Performance", "Neutral", "The application response time is average, but it sometimes lags when exporting data."),
    ("Performance", "Negative", "Why does the app lag so much when switching between workspaces? Please optimize performance."),
    
    # User Experience
    ("User Experience", "Negative", "The navigation menu is really confusing. It takes me 4 clicks just to find the settings page."),
    ("User Experience", "Negative", "It is hard to read the text in light mode. Contrast is very poor, my eyes hurt."),
    ("User Experience", "Positive", "The layout is extremely clean and intuitive. I was able to figure out the workflows in 2 minutes."),
    ("User Experience", "Positive", "Beautiful interface! Very clean, uncluttered, and easy to use. Kudos to the design team."),
    ("User Experience", "Neutral", "The interface looks fine but the button placement for saving projects is a bit weird."),
    ("User Experience", "Negative", "The mobile web version is completely broken. Buttons overlap and I can't click the menu."),
    
    # Pricing
    ("Pricing", "Negative", "The subscription price is too high for small startups. $59/month is steep for basic features."),
    ("Pricing", "Negative", "Suddenly locking features that were previously free behind the Pro plan is a bad move."),
    ("Pricing", "Positive", "The pricing is very reasonable considering the amount of time and manual effort this tool saves us."),
    ("Pricing", "Positive", "Great value for money. The ROI we get from the team plan is well worth the cost."),
    ("Pricing", "Neutral", "Pricing is average for this category, but I wish there was a pay-as-you-go option."),
    ("Pricing", "Negative", "I'd love to use this but the pricing packages are not flexible enough for individual developers."),

    # Support
    ("Support", "Negative", "I submitted a support ticket 3 days ago about a billing issue and still haven't heard back."),
    ("Support", "Negative", "The support agent didn't read my query properly and just pasted a generic article link. Unhelpful."),
    ("Support", "Positive", "The live chat support was incredible! Solved my issue in less than 5 minutes."),
    ("Support", "Positive", "Excellent customer service. They helped me set up my custom integrations step-by-step."),
    ("Support", "Neutral", "The support docs are okay, but I prefer speaking to a human. Hard to find the contact form."),
    ("Support", "Negative", "No live chat option? Email support takes way too long to respond. Very frustrating."),

    # Product Quality
    ("Product Quality", "Negative", "The app crashed twice today while I was trying to import a CSV file. Lost my work."),
    ("Product Quality", "Negative", "There are so many bugs in the latest release. The export PDF button is completely broken."),
    ("Product Quality", "Positive", "I've been using this tool for 6 months and it hasn't crashed once. Extremely stable software."),
    ("Product Quality", "Positive", "Robust product quality. The features work exactly as described without any hiccups."),
    ("Product Quality", "Neutral", "The app is mostly stable but there are some minor visual bugs in the chart displays."),
    ("Product Quality", "Negative", "Data synchronization fails frequently between my web app and the desktop client."),

    # Feature Requests
    ("Feature Requests", "Neutral", "Please add a native dark mode. Working at night is blinding with this white screen."),
    ("Feature Requests", "Neutral", "We really need a Slack integration so our team can get notifications directly in our channels."),
    ("Feature Requests", "Neutral", "It would be great if we could export reports in PowerPoint format for executive presentations."),
    ("Feature Requests", "Neutral", "Is there a mobile app in the roadmap? I need to check the status dashboard on the go."),
    ("Feature Requests", "Neutral", "I highly recommend adding multi-user collaboration and permission roles for team workspaces."),
    ("Feature Requests", "Neutral", "Can you add an API endpoint to let us programmatically fetch analysis results?")
]

def generate_mock_data(size, output_file):
    # Base date for generating random timestamps
    base_date = datetime.now() - timedelta(days=90)
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["customer_id", "created_at", "feedback_text"])
        
        for i in range(1, size + 1):
            cust_id = f"CUST-{random.randint(1000, 9999)}"
            # Generate random timestamp in the last 90 days
            random_days = random.randint(0, 90)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            feedback_date = base_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
            date_str = feedback_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Select a random template
            category, sentiment, text_template = random.choice(FEEDBACK_TEMPLATES)
            
            # Add some variations to make the data more diverse
            variations = [
                lambda t: t,
                lambda t: f"{t} Hope this gets fixed soon.",
                lambda t: f"Just wanted to say: {t}",
                lambda t: f"{t} (using version 2.4.1)",
                lambda t: f"Disappointed. {t}" if sentiment == "Negative" else f"Awesome! {t}" if sentiment == "Positive" else t,
                lambda t: f"{t} Highly recommend." if sentiment == "Positive" else t
            ]
            feedback_text = random.choice(variations)(text_template)
            
            writer.writerow([cust_id, date_str, feedback_text])
            
    print(f"Successfully generated {size} mock feedback records in '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate mock feedback dataset CSV.")
    parser.add_argument("--size", type=int, default=100, help="Number of records to generate.")
    parser.add_argument("--output", type=str, default="mock_feedback.csv", help="Output CSV filename.")
    
    args = parser.parse_args()
    generate_mock_data(args.size, args.output)
