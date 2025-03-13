from langchain_core.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import sys
import os
import time
import random
sys.path.append("../..")  # Add the project root to the path
from src.config import get_groq_llm, PROJECT_CONFIG

def get_monitoring_prompt():
    return PromptTemplate(
        input_variables=["project_name", "deployment_status"],
        template="""
        You are a system reliability engineer. Create a monitoring and feedback plan for the deployed project named "{project_name}".
        
        Deployment Status:
        {deployment_status}
        
        Please provide:
        
        1. Monitoring Strategy
           - Key metrics to track
           - Performance indicators
           - Error tracking approach
           - User feedback collection methods
        
        2. Alerting Configuration
           - Alert thresholds
           - Escalation procedures
           - On-call rotation recommendations
        
        3. Feedback Analysis
           - How to process and prioritize user feedback
           - A/B testing recommendations
           - Feature usage tracking
        
        4. Continuous Improvement
           - Feedback loop implementation
           - Regular review schedule
           - Technical debt management
        
        Provide a comprehensive monitoring and feedback plan that ensures the application remains reliable and improves over time.
        """
    )

def simulate_monitoring_data():
    """
    Simulate monitoring data for demonstration purposes
    """
    # Simulate some basic metrics
    metrics = {
        "response_time_ms": random.randint(50, 500),
        "error_rate": random.uniform(0, 0.05),
        "cpu_usage": random.uniform(10, 90),
        "memory_usage": random.uniform(20, 80),
        "active_users": random.randint(10, 1000),
        "requests_per_minute": random.randint(10, 1000)
    }
    
    # Simulate some user feedback
    feedback_options = [
        "The application is very responsive and easy to use.",
        "I found the login process confusing.",
        "Great features, but the UI could be more intuitive.",
        "The search functionality is not working correctly.",
        "Love the new dashboard design!",
        "The application crashed when I tried to upload a large file."
    ]
    
    user_feedback = random.sample(feedback_options, 3)
    
    return {
        "timestamp": time.time(),
        "metrics": metrics,
        "user_feedback": user_feedback
    }

def monitor_application(state):
    """
    Set up monitoring and collect feedback
    """
    monitoring_chain = LLMChain(llm=get_groq_llm(), prompt=get_monitoring_prompt())
    monitoring_plan = monitoring_chain.run(
        project_name=state["project_name"],
        deployment_status=state["deployment_status"]
    )
    
    state["monitoring_plan"] = monitoring_plan
    
    # Save monitoring plan to file
    os.makedirs(PROJECT_CONFIG["output_dir"], exist_ok=True)
    with open(f"{PROJECT_CONFIG['output_dir']}/monitoring_plan.md", "w") as f:
        f.write(monitoring_plan)
    
    # Simulate monitoring data
    print("\nSimulating monitoring data collection...")
    monitoring_data = simulate_monitoring_data()
    state["monitoring_data"] = monitoring_data
    
    # Save monitoring data to file
    with open(f"{PROJECT_CONFIG['output_dir']}/monitoring_data.json", "w") as f:
        import json
        json.dump(monitoring_data, f, indent=2)
    
    print("Monitoring setup complete.")
    print(f"Current metrics:")
    for metric, value in monitoring_data["metrics"].items():
        print(f"  - {metric}: {value}")
    
    print("\nUser feedback samples:")
    for feedback in monitoring_data["user_feedback"]:
        print(f"  - \"{feedback}\"")
    
    return state 