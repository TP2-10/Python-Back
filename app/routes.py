from flask import request, jsonify, send_file
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from app import app, db
import openai
from app.models import Story, Question, Option , Image
from app.models import User
from app.openai_utils import generate_story_with_openai, generate_questions_with_openai, generate_prompts_images_with_openai
from gtts import gTTS

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing data'}), 400

    user = User(username=username, email=email, password=password)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while processing your request'}), 500


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }
    
    return jsonify(user_data), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        user_list.append(user_data)
    
    return jsonify(user_list), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.verify_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

def split_text_into_segments(text, max_length):
    segments = []
    for i in range(0, len(text), max_length):
        segment = text[i:i + max_length]
        segments.append(segment)
    return segments

@app.route('/stories', methods=['POST'])
#@jwt_required()
def generate_story():
    data = request.get_json()
    plot = data.get('plot')
    mainCharacter = data.get('mainCharacter')
    place = data.get('place')
    genre = data.get('genre')
    audience = data.get('audience')

    if not plot or not mainCharacter or not place or not genre or not audience:
        return jsonify({'error': 'Missing data'}), 400

    # Construct the prompt with the specified characteristics
    prompt = (
        f"Genera una historia con las siguientes caracteristicas: "
        f"sinopsis: {plot}. "
        f"Nombre del personaje principal: {mainCharacter}. "
        f"Lugar donde se encuentra ambientada la historia: {place}. "
        f"Genero: {genre}. "
        f"Publico a quien va dirigida la historia: {audience}. "
        f"La historia debe tener tres partes: inicio, trama y final. "
    )

    print(prompt)

    # Generate the story using the OpenAI API function
    generated_story = generate_story_with_openai(prompt)

    # Split the generated story into segments
    #max_prompt_length = 270  # Adjust the maximum prompt length as needed
    #story_segments = split_text_into_segments(generated_story, max_prompt_length)

    # Save the generated story to the database
    story = Story(prompt=prompt, content=generated_story)
    db.session.add(story)
    db.session.commit()

    #Get images url from fuction
    separated_prompts = generate_prompts_images_with_openai(generated_story)
    print(separated_prompts)

    # Initialize a list to store the image URLs for each segment
    image_urls = []

    for segment in separated_prompts:
        try:
            # Generate an image related to the story segment
            image_response = openai.Image.create(
                prompt=segment,
                n=1,
                size="1024x1024"
            )

            # Retrieve the URL of the generated image
            image_url = image_response['data'][0]['url']

            # Create an Image instance and associate it with the story
            image = Image(story_id=story.id, url=image_url)

            # Add the image to the database session
            db.session.add(image)

            # Append the image URL to the list
            image_urls.append(image_url)

        except Exception as e:
            print(f"Error generating image with OpenAI: {e}")
            # Handle the error as needed

    # Commit the changes to the database session
    db.session.commit()

    rpta = {}
    rpta['story'] = generated_story
    rpta['images'] = image_urls

    # Now, you have a list of image URLs for each segment
    # You can return them in the API response or use them as needed
    #return jsonify({'message': 'Story generated and saved successfully', 'image_urls': image_urls}), 201
    print('REPTA: ', rpta)
    return rpta

@app.route('/stories/<int:story_id>', methods=['GET'])
@jwt_required()
def get_story(story_id):
    story = Story.query.get(story_id)

    if not story:
        return jsonify({'error': 'Story not found'}), 404

    return jsonify({'story': story.content}), 200

@app.route('/stories/questions', methods=['POST'])
def generate_and_store_questions():
    #REQUEST BODY:
    data = request.get_json()
    story = data.get('story')

    # Retrieve the story based on the provided story_id
    #story = Story.query.get(story_id)

    if not story:
        return jsonify({'error': 'Story not found'}), 404

    # Generate questions using the OpenAI API based on the story
    generated_questions = generate_questions_with_openai(story)

    
    # Store the generated questions and options in the database
    #store_generated_questions(story.id, generated_questions)

    #return jsonify({'message': 'Questions generated and stored successfully'}), 201
    print(generated_questions)
    return generated_questions
    

def store_generated_questions(story_id, generated_questions):
    # Iterate through the generated questions and options
    for question_text, options in generated_questions.items():
        # Create a new Question instance and associate it with the story
        question = Question(story_id=story_id, question_text=question_text)
        db.session.add(question)
        db.session.commit()  # Commit here to obtain the question ID

        # Iterate through the options for the current question
        for option_text in options:
            # Create a new Option instance associated with the current question
            option = Option(question_id=question.id, text=option_text)
            db.session.add(option)

    db.session.commit()

@app.route('/stories/<int:story_id>/questions', methods=['GET'])
@jwt_required()
def get_story_questions(story_id):
    # Query the database to retrieve questions for the specific story
    questions = Question.query.filter_by(story_id=story_id).all()

    # Check if the story exists
    story = Story.query.get(story_id)
    if not story:
        return jsonify({'error': 'Story not found'}), 404

    # Create a list to store question data
    questions_data = []

    # Iterate through the retrieved questions and add them to the list
    for question in questions:
        question_data = {
            'id': question.id,
            'question_text': question.question_text,
            'options': [option.text for option in question.options]
        }
        questions_data.append(question_data)

    return jsonify({'story_id': story.id, 'questions': questions_data}), 200


@app.route('/stories/prompts', methods=['POST'])
def generate_prompst_for_images():
    #REQUEST BODY:
    data = request.get_json()
    story = data.get('story')

    if not story:
        return jsonify({'error': 'Story not found'}), 404

    # Generate prompts for images using the OpenAI API based on the story
    generated_prompts = generate_prompts_images_with_openai(story)

    #return jsonify({'message': 'Questions generated and stored successfully'}), 201
    print(generated_prompts)
    return generated_prompts


#GENERAR IMAGENES
@app.route('/stories/prompts/images', methods=['POST'])
def generate_images():
    #REQUEST BODY:
    data = request.get_json()
    story = data.get('story')

    if not story:
        return jsonify({'error': 'Story not found'}), 404

    image_urls = []

    separated_prompts = generate_prompts_images_with_openai(story)

    for segment in separated_prompts:
        try:
            # Generate an image related to the story segment
            image_response = openai.Image.create(
                prompt=segment,
                n=1,
                size="1024x1024"
            )

            # Retrieve the URL of the generated image
            image_url = image_response['data'][0]['url']

            # Create an Image instance and associate it with the story
            image = Image(story_id=story.id, url=image_url)

            # Add the image to the database session
            db.session.add(image)

            # Append the image URL to the list
            image_urls.append(image_url)

        except Exception as e:
            print(f"Error generating image with OpenAI: {e}")
            # Handle the error as needed

    # Commit the changes to the database session
    db.session.commit()

    rpta = image_url
    #rpta['story'] = generated_story
    #rpta['images'] = image_urls

    # Now, you have a list of image URLs for each segment
    # You can return them in the API response or use them as needed
    #return jsonify({'message': 'Story generated and saved successfully', 'image_urls': image_urls}), 201
    print('REPTA: ', rpta)
    return image_url


#SERVICIO DE GENERACION DE AUDIO PARA TEXTO
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.get_json()
        text = data['text']

        # Genera el audio
        tts = gTTS(text, lang='es')
        audio_filename = 'C:\\Users\\carlo\\Documents\\TP2 Proyect\\Backend\\Python-Back\\generated_audio.mp3'
        tts.save(audio_filename)
        print("Hasta aqui:")

        # Envía el archivo de audio al cliente
        return send_file(audio_filename, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 500