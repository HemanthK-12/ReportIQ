import openai
response = openai.Embedding.create(
  input="Hello",
  model="text-embedding-ada-002"
)