import os
import sys

# Add backend to path to import ai_agents
sys.path.append(os.getcwd())

from ai_agents.system import IssueReasoningAgent

def test_tamil_categorization():
    agent = IssueReasoningAgent()
    
    test_cases = [
        "எங்க வீட்ல தெரு விளக்கு எரியல",
        "தெரு விளக்கு",
        "குப்பை அதிகமா இருக்கு",
        "ரோடு ரொம்ப மோசமா இருக்கு"
    ]
    
    print("--- Tamil Categorization Test ---")
    for text in test_cases:
        result = agent.analyze(text)
        print(f"Input: {text}")
        print(f"Category: {result.get('Issue_Type')}")
        print(f"Locked: {result.get('category_locked')}")
        print("-" * 20)

if __name__ == "__main__":
    test_tamil_categorization()
