from flask import Flask, request, jsonify
from flask_cors import CORS
from htr_module import preprocess_image, infer_image

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])  # Allow requests from localhost:3000 only

@app.route('/convert', methods=['POST'])
def convert_image_to_text():
    # Check if request.files is empty
    if not request.files:
        return jsonify({'error': 'No file uploaded hehe'}), 400

    # Get the uploaded image file
    image_file = request.files['image']

    # Preprocess the image
    processed_image = preprocess_image(image_file)

    # Perform text recognition
    text , probability, corrected= infer_image(processed_image)


    # Return the recognized text
    return jsonify({'message': 'Image processed successfully', 'text': text, 'correction':corrected, 'confidence':probability})

if __name__ == '__main__':
    app.run(debug=True)
