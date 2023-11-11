# app/openai_utils.py
import openai

# Load OpenAI API key from the configuration. Hidden key
OPENAI_API_KEY = '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'

openai.api_key = OPENAI_API_KEY

def generate_story_with_openai(prompt):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
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
            engine="gpt-3.5-turbo-instruct",
            prompt = ("generate a multiple-choice question. Ensure that the question follows this format:\n"
                        "[Insert your question text here]\n"
                        "a) [Option A text]\n"
                        "b) [Option B text]\n"
                        "c) [Option C text]\n"
                        "Correct answer: [Indicate which of the options (a, b, or c) is the correct answer]\n"
                        f"based on the following story:\n\n{story_content}"),
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
    #options_prefix = ["Option A", "Option B", "Option C"]  # Puedes personalizar tus opciones aquí

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
            engine="gpt-3.5-turbo-instruct",
            #prompt=f"Lee la siguiente historia:\n\n{story_content}\n\n. Quiero generar imagenes con DALL-E que se relacionen con la hisotoria. Genera 5 prompts de imagenes sobre la historia para enviar a DALL-E. Las imagenes deben tener un estilo animado que sea agradable para niños",
            prompt=f"Read the following story: \n\n{story_content}\n\n. I want to generate images with DALL-E in a style that is animated and child-friendly. Please create 3 image prompts related to the story, in each prompt, include terms to specify that the image has a animation style like cartoon. Do not use characters' own names, use generic terms (child, man, woman, etc.)",            
            max_tokens=2000,  # Adjust the desired length of the generated story
            n=1
        )

        print(response)

        generated_prompts = response.choices[0].text.strip()

        separated_prompts = generated_prompts.split('\n')
        new_separated_prompts = []

        for prompt in separated_prompts:
            if len(prompt) > 5:
                new_separated_prompts.append(prompt)
        

        print('----SEPARETED PROMOPTS------')
        print(new_separated_prompts)

        return new_separated_prompts
    except Exception as e:
        print(f"Error generating story: {e}")
        return None