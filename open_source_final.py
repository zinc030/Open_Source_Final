#zinc030
import dlib
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import os
import gensim.downloader as api
from gensim.models import KeyedVectors
import nltk
from nltk.corpus import wordnet
import time

# nltk.download('wordnet')
# nltk.download('punkt')

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# vectors = api.load('glove-twitter-200')
# vectors.save('vectors.bin')
model = KeyedVectors.load('vectors.bin') #Don't have to download and wait every code run


def is_adjective(word):
    synsets = wordnet.synsets(word)
    for synset in synsets:
        if synset.pos() == 'a':
            return True
    return False

def detect_face(image_path):
    index = 0
    detector = dlib.get_frontal_face_detector()

    img = cv2.imread(image_path)
    faces = detector(img, 1)
    for face in faces:
        left_top = (face.left(), face.top())
        right_bottom = (face.right(), face.bottom())
        midx = int((face.left() + face.right()) / 2)
        midy = int((face.top() + face.bottom()) / 2)
        circlemid = (midx, midy)
        # radi = int(np.sqrt((face.top()-face.bottom())**2+(face.left()-face.right())**2)/2)
        radi = int(np.abs(face.top() - face.bottom()) / 2)
        cv2.rectangle(img, left_top, right_bottom, (0, 0, 255), 2)  # cv2는 RGB아니라 GBR값을 씀
        cv2.circle(img, circlemid, radi, (0, 255, 0), 0)

        # crop = img[face.top():face.bottom(), face.left():face.right()]
        # cv2.imwrite("cropped" + str(index) + ".jpg", crop)
        index += 1

    return index, img


def draw_landmark(image_path):
  detector = dlib.get_frontal_face_detector()
  predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

  img = cv2.imread(image_path)
  faces = detector(img, 1)
  for face in faces:
    shape = predictor(img, face)

    for x in range(68):
      pts = (shape.part(x).x, shape.part(x).y)
      cv2.circle(img, pts, 1, (255, 0, 0), cv2.FILLED, cv2.LINE_AA)

  cv2.imshow('lm', img)
  cv2.waitKey()

# def detect_faces(img): #if there are multiple faces
#   result = []
#   for face_rect in detector(img, 0):
#     shape = predictor(img, face_rect)
#     result.append(shape)
#   return result

adj = []
count = 0
total = 20
altadj = ""
adjidx = 0
flexible_search_keyword = ""

while True:  #generate search query and collect images
    try:
        count, adjidx = 0, 0
        adj = []
        altadj = ""
        search_keyword = input("Enter an adjective and a noun(-1 to quit): ")
        if search_keyword == "-1":
            break
        else:
            words = nltk.word_tokenize(search_keyword)
            if len(words) != 2:
                print("There are more than 2 words")
            if is_adjective(words[0]):
                print(f"{words[0]} is an adjective.")
                flexible_search_keyword = search_keyword

                similar_words = model.most_similar(positive=words, topn=100) #words must be a list of words
                for word, similarity in similar_words:
                    if is_adjective(word):
                        adj.append(word)

                driver = webdriver.Chrome()  # all 20 images must have one face.
                while count < total:
                    if count == total:
                        break
                    search_url = f'https://www.pinterest.com/search/pins/?q={flexible_search_keyword}'
                    driver.get(search_url)
                    time.sleep(5)

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    image_tags = soup.find_all('img', {'src': True})

                    if not os.path.exists(search_keyword):
                        os.makedirs(search_keyword)

                    for img in (image_tags):
                        image_url = img['src']
                        image_url = image_url.replace("236px", "736x", 1)
                        image_name = f"{search_keyword}_{count}.jpg"
                        image_path = os.path.join(search_keyword, image_name)
                        response = requests.get(image_url)
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        nface = detect_face(image_path)[0]
                        if count == total:
                            os.remove(image_path)
                        elif nface < 1:
                            os.remove(image_path)
                        else:
                            count += 1
                    if count < total:
                        flexible_search_keyword = adj[adjidx]+" "+words[1]
                        adjidx += 1
                driver.quit()
            else:
                print(f"{words[0]} is not an adjective.")

    except Exception as e:
        print(e)

# red_channel = image_array[:, :, 0]
# green_channel = image_array[:, :, 1]
# blue_channel  = image_array[:, :, 2]
# print(red_channel.shape)
# print(green_channel.shape)
# print(blue_channel.shape)
#
# merged_image = np.dstack((red_channel, green_channel, blue_channel))
# merged_image = Image.fromarray(merged_image)
# merged_image.save("merged_image.jpg")

save_count = 0
while True: #Edit Image, progress
    try:
        image_path = input("Enter image path that you want to edit(-1 to quit): ")
        if image_path == "-1":
            break
        cvimg = cv2.imread(image_path)
        image = Image.open(image_path)
        image_array = np.array(image)
        while True:
            action = input("What would you like to do with the selected image?" 
                           "\n Flip"
                           "\n Grayscale"
                           "\n Show_Landmark"
                           "\n Save"
                           "\n Back"
                           "\n Please type the exact keywords: ")
            if action.lower() == "back":
                break
            elif action.lower() == "save":
                image.save(f"final_{save_count}.jpg")
                save_count +=1
            elif action.lower() == "flip":
                image = np.fliplr(image_array)
                image = Image.fromarray(image)
            elif action.lower() == "grayscale":
                image = np.dot(image_array, [0.2989, 0.5870, 0.1140])
                image = image.astype(np.unit8)
            elif action.lower() == "show_landmark":
                draw_landmark(image_path)
            else:
                "invalid input"

    except Exception as e:
        print(e)
