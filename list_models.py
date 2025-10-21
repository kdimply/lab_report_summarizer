import google.generativeai as genai

genai.configure(api_key="AIzaSyAQGDtnLc_Hvjtp6LkcNyhH6WchrhU8bWQ")

models = genai.list_models()
for m in models:
    print(m.name)
