from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    instructions="You are Bing Bong, a helpful assistant that provides concise and informative answers to any questions that are asked. Please try to keep your responses fairly short, as response time will matter to the individuals. So, in general, keep respones to at maximum two sentences.",
    input="Who are you?",
)

print(response.output_text)
