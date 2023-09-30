# app/openai_utils.py
import openai

# Load OpenAI API key from the configuration
OPENAI_API_KEY = ''

openai.api_key = OPENAI_API_KEY

def generate_story_with_openai(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2000,  # Adjust the desired length of the generated story
            n=1
        )

        generated_story = response.choices[0].text.strip()
        return generated_story
    except Exception as e:
        print(f"Error generating story: {e}")
        return None

def generate_questions_with_openai(story_content):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Generate a multiple-choice questions with only a , b or c ( the options must have the following format : a) , b), c) ) based on the following story:\n\n{story_content}",
            max_tokens=2000,  # Adjust as needed
            temperature = 0.9,
            n=5  # Generate 5 questions
        )

        generated_questions = parse_generated_questions(response.choices)
        return generated_questions
    except Exception as e:
        print(f"Error generating questions with OpenAI: {e}")
        return {}

def parse_generated_questions(choices):
    generated_questions = {}
    for idx, choice in enumerate(choices):
        question_text = f"Question {idx + 1}: {choice.text.strip()}"
        options = ["Option A", "Option B", "Option C"]  # Replace with your options
        generated_questions[question_text] = options

    return generated_questions