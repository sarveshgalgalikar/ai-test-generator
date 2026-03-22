import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What are 3 edge cases a QA engineer should test for a login form?"}
    ]
)

print(message.content[0].text)