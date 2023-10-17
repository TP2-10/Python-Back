# app/openai_utils.py
import openai

# Load OpenAI API key from the configuration
OPENAI_API_KEY = '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'

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
            prompt=f"Generate a multiple-choice questions with only a , b or c ( the options must have the following format : a) , b), c) and mention which is the correct alternantive (a , b or c) based on the following story:\n\n{story_content}",
            max_tokens=2000,  # Adjust as needed
            temperature = 0.9,
            n=5  # Generate 5 questions
        )
        rpta1 = response
        print(rpta1)

        generated_questions = parse_generated_questions(response.choices)
        return generated_questions
    except Exception as e:
        print(f"Error generating questions with OpenAI: {e}")
        return {}

def parse_generated_questions(choices):
    generated_questions = []
    options_prefix = ["Option A", "Option B", "Option C"]  # Puedes personalizar tus opciones aquí

    for idx, choice in enumerate(choices):
        text = choice.text.strip()
        question_parts = text.split('\n')
        
        question_text = question_parts[0]  # El primer elemento es el enunciado de la pregunta
        options = [f"{option}" for _, option in enumerate(question_parts[1:])]
        
        question_data = {
            "id": idx + 1,
            "question_text": question_text,
            "options": options
        }

        generated_questions.append(question_data)

    return generated_questions


def generate_prompts_images_with_openai(story_content):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"En base a esta historia:\n\n{story_content}\n\n. Por favor, genera 5 prompts detallados para enviar a Dall-e y generar imagenes sobre la historia",
            max_tokens=2000,  # Adjust the desired length of the generated story
            n=1
        )

        print(response)

        generated_prompts = response.choices
        return generated_prompts
    except Exception as e:
        print(f"Error generating story: {e}")
        return None