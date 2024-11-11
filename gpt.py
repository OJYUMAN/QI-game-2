from openai import OpenAI
import json


client = OpenAI(api_key="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")


def chat_with_gpt(prompt):
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # can use other models like "gpt-4"
    messages=[
        {"role": "system", "content": "You are ChatGPT, a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=1000,  # Adjust this value for longer or shorter responses
    n=1,
    stop=None,
    temperature=0.7)
    return response.choices[0].message.content

# Example of usage
# prompt = "Explain the theory of relativity in simple terms."
# response = chat_with_gpt(prompt)
# print(response)

def handle_prompt(content, number, level, language):
    text = f"""Generate a JSON object containing a list of quiz questions based on the following lesson content. The output should only be in JSON format with no additional text. Each question must include four choices and one correct answer. The JSON structure should look like this:

    {{
        "quiz": [
            {{
                "question": "<insert question here>",
                "choices": [
                    "<choice 1>",
                    "<choice 2>",
                    "<choice 3>",
                    "<choice 4>"
                ],
                "answer": "<correct answer>"
            }}
        ]
    }}

    Please generate {number} questions with a difficulty level of "{level}". Use the {language} to compose the questions.

    Lesson content: "{content}"
    """

    response = chat_with_gpt(text)
    
    # Assuming response is a valid JSON string
    try:
        quiz_data = json.loads(response)
        
        # Write to quiz.json
        with open('quiz.json', 'w', encoding='utf-8') as json_file:
            json.dump(quiz_data, json_file, ensure_ascii=False, indent=4)
        
        print("Quiz questions have been saved to quiz.json.")
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
    except Exception as e:
        print(f"An error occurred: {e}")



