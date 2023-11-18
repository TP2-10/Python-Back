# app/openai_utils.py
import openai

# Load OpenAI API key from the configuration. Hidden key
OPENAI_API_KEY = ''

openai.api_key = OPENAI_API_KEY

def generate_story_with_openai(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1500,  # Adjust the desired length of the generated story
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
    
def generate_question_chapter_with_openai(story_content):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt = ("generate a multiple-choice question in spanish. Ensure that the question follows this format:\n"
                        "[Insert your question text here]\n"
                        "a) [Option A text]\n"
                        "b) [Option B text]\n"
                        "c) [Option C text]\n"
                        "Respuesta correcta: [Indicate which of the options (a, b, or c) is the correct answer]\n"
                        f"based on the following story:\n\n{story_content}"),
            max_tokens=2000,  # Adjust as needed
            temperature = 0.9,
            n=1  # Generate 5 questions
        )
        rpta1 = response
        print(rpta1)

        generated_response = parse_generated_questions(response.choices)
        return generated_response
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


def generate_prompt_image_for_chapter(story_content):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            #prompt=f"Lee la siguiente historia:\n\n{story_content}\n\n. Quiero generar imagenes con DALL-E que se relacionen con la hisotoria. Genera 5 prompts de imagenes sobre la historia para enviar a DALL-E. Las imagenes deben tener un estilo animado que sea agradable para niños",
            prompt=f"Read the following story: \n\n{story_content}\n\n. I want to generate a image using DALL-E api in a style that is animated and child-friendly. Please create 1 image prompt related to the story, in the prompt, include terms to specify that the image has a animation style like cartoon. Do not use characters' own names, use generic terms (child, man, woman, etc.)",            
            max_tokens=2000,  # Adjust the desired length of the generated story
            n=1
        )

        print(response)

        image_prompt = response.choices[0].text.strip()

        print('----FINAL PROMOPTS------')
        print(image_prompt)

        return image_prompt
    except Exception as e:
        print(f"Error generating story: {e}")
        return None


def generate_image_for_chapter(image_prompt):

    image_urls = []

    try:
        # Generate an image related to the story segment
        image_response = openai.Image.create(
            prompt=image_prompt,
            n=1,
            size="1024x1024",
            model= "dall-e-3"
        )

        # Retrieve the URL of the generated image
        image_url = image_response['data'][0]['url']

        # Append the image URL to the list
        image_urls.append(image_url)

    except Exception as e:
        print(f"Error generating image with OpenAI: {e}")
        # Handle the error as needed

    rpta = image_urls
    #rpta['story'] = generated_story
    #rpta['images'] = image_urls

    # Now, you have a list of image URLs for each segment
    # You can return them in the API response or use them as needed
    #return jsonify({'message': 'Story generated and saved successfully', 'image_urls': image_urls}), 201
    print('RPTA: ', rpta)
    return image_url
