from openai import OpenAI

client = OpenAI(api_key="sk-proj-EzUy5QQyRXbGzT77vX5iT3BlbkFJrjEtB3kYzYU8AexqWfLa")

response = client.chat.completions.create(
                model="gpt-4o-2024-05-13",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant.",
                    },
                    {"role": "user", "content": prompt},
                ]
            )

advice = response.choices[0].message.content
print(advice)