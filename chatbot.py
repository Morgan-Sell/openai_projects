import openai
from dotenv import dotenv_values

config = dotenv_values(".env")
openai.api_key = config["OPENAI_API_KEY"]



while True:
    messages = []
    try:
        user_input = input("You: ")
        messages.append({"role": "user", "content": user_input})
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        messages.append(res["choices"][0]["message"].to_dict())
        print(res["choices"][0]["message"]["content"])

        print("MESSAGES: ", messages)

    except KeyboardInterrupt:
        print("Exiting...")
        break

print(res)