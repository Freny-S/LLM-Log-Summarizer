import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

SAMPLE_LOGS = """
2024-03-01 02:13:44 ERROR [kafka-consumer] Failed to consume from topic tv.events.playback - broker timeout after 30s
2024-03-01 02:13:45 WARN  [kafka-consumer] Retrying connection attempt 1/3
2024-03-01 02:13:47 WARN  [kafka-consumer] Retrying connection attempt 2/3
2024-03-01 02:13:50 ERROR [kafka-consumer] Max retries exceeded. Dropping event batch. batch_id=b8f3a1
2024-03-01 02:13:51 ERROR [metrics-service] NullPointerException at MetricsAggregator.java:142
2024-03-01 02:13:52 INFO  [health-check] Service status: degraded
2024-03-01 02:14:10 INFO  [kafka-consumer] Connection re-established. Resuming consumption.
"""

def summarize_logs(logs: str) -> dict:
    prompt = f"""You are an on-call engineer assistant. Analyze these application logs and return a JSON response with exactly these fields:
- severity: one of [CRITICAL, HIGH, MEDIUM, LOW]
- summary: 1-2 sentence plain English summary of what happened
- root_cause: your best guess at the root cause
- affected_services: list of affected services
- resolved: true or false based on whether logs show recovery

Logs:
{logs}

Respond only with valid JSON. No extra text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    print("Analyzing logs...\n")
    result = summarize_logs(SAMPLE_LOGS)
    print(json.dumps(result, indent=2))
