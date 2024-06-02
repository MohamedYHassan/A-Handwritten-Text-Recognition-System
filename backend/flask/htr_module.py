from typing import List
from flask import Flask, request, jsonify
from model.preprocessor import TextImagePreprocessor
from model.model import HTRModel
import cv2
import numpy as np
from textblob import TextBlob
from collections import namedtuple
from symspellpy import SymSpell
import pkg_resources


Batch = namedtuple('Batch', 'imgs, gt_texts, batch_size')
CHAR_LIST = 'model/charList.txt'




def preprocess_image(file):
    # Read the image file using OpenCV
    img_array = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    
    # Preprocess the image using the TextImagePreprocessor
    preprocessor = TextImagePreprocessor(target_image_size=(256, 32), dynamic_width=True, padding=16)
    processed_image = preprocessor.process_image(image)
    
    # Return the processed image
    return processed_image


def char_list_from_file() -> List[str]:
    with open(CHAR_LIST) as f:
        return list(f.read())


def infer_image(img):
            
    batch = Batch([img], None, 1)
    model = HTRModel(char_list_from_file(),decoder_type=1,must_restore=True,dump=False)


    recognized, probability  = model.infer_batch(batch, True)
    text = " ".join(recognized)
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt")
    bigram_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_bigramdictionary_en_243_342.txt")
    
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
    suggestions = sym_spell.lookup_compound(text, max_edit_distance=2)
    corrected = ""
    for suggestion in suggestions:
        print(suggestion)
        corrected += str(suggestion)

    probability_str = str(probability[0])
    print(probability_str)
    split_text = corrected.split(",", 1)



    # corrected = TextBlob(text).correct()
    # word_list = []
    # for word in corrected.split():
    #     word_list.append(word + " ")  # Append word with a trailing space

    # print(word_list)

    return recognized, probability_str, split_text[0]






