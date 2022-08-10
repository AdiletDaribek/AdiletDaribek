import torch
from PIL import Image
import ast
import requests
import cv2
from operator import itemgetter
def get_yolo_cars():
    # local best.pt
    model = torch.hub.load('./yolov5', 'custom', path='./model/best(cars).pt', source='local')  # local repo
    model.conf = 0.5
    return model

def get_yolo_plates():
    # local best.pt
    model = torch.hub.load('./yolov5', 'custom', path='./model/best(plates).pt', source='local')  # local repo
    model.conf = 0.5
    return model

def get_yolo_numbers():
    # local best.pt
    model = torch.hub.load('./yolov5', 'custom', path='./model/num7.pt', source='local')  # local repo
    model.conf = 0.5
    return model

def get_yolo_character():
    # local best.pt
    model = torch.hub.load('./yolov5', 'custom', path='./model/character.pt', source='local')  # local repo
    model.conf = 0.5
    return model

cars_model = get_yolo_cars()
plates_model=get_yolo_plates()
numbers_model=get_yolo_numbers()
character_model=get_yolo_character()


def square_numbers(dict,img):
    print('salam')
    y=-1
    tima=[]
    tima_down=[]
    tima_down_num=[]
    while(1):
        height = img.shape[0]
        try:
            y+=1
            name=(dict[y]['name'])
            coor=(dict[y]['xmin'])
            door={'coor':coor,'name':name}
            if(dict[y]['ymax']<((height*6)/10)):
                tima.append(door)
            elif int(ord(dict[y]['name']))>64 and int(ord(dict[y]['name']))<91:
                tima_down.append(door)
            else:
                tima_down_num.append(door)
        except:
            break

    newlist = sorted(tima, key=itemgetter('coor')) 
    newlist_down = sorted(tima_down, key=itemgetter('coor'))
    newlist_down_num = sorted(tima_down_num, key=itemgetter('coor'))
    i=0
    s=''
    for i in newlist:
        s+=i['name']
    i=0
    for i in newlist_down:
        s+=i['name']
    i=0
    for i in newlist_down_num:
        s+=i['name']
    return s

def run_models(img):
    try:
        results= cars_model(img)
        res = results.pandas().xyxy[0].to_json(orient="records")
        dic = ast.literal_eval(res)
        img2 = img[int(dic[0]['ymin']):int(dic[0]['ymax']), int(dic[0]['xmin']):int(dic[0]['xmax'])]

        results= plates_model(img2)
        res = results.pandas().xyxy[0].to_json(orient="records")
        dict = ast.literal_eval(res)
        img3 = img2[int(dict[0]['ymin']): int(dict[0]['ymax']), int(dict[0]['xmin']):int(dict[0]['xmax'])]
        # cv2.imshow("salam",img3)
        # cv2.waitKey(3000)

        results= numbers_model(img3)
        res = results.pandas().xyxy[0].to_json(orient="records")
        dict = ast.literal_eval(res)

        y=-1
        tima=[]
        while(1):
            try:
                y+=1
                if(int(dict[y]['ymax'])<((img3.shape[0]*6)/10)):
                    return square_numbers(dict,img3)
                else:
                    name=(dict[y]['name'])
                    coor=(dict[y]['xmin'])
                    door={'coor':coor,'name':name}
                    tima.append(door)
            except:
                break

        newlist = sorted(tima, key=itemgetter('coor')) 
        i=0
        s=''
        for i in newlist:
            s+=i['name']
        
        results= character_model(img3)
        res = results.pandas().xyxy[0].to_json(orient="records")
        dict = ast.literal_eval(res)
        if(len(dict)==len(s)):
            return s

        else: print('not enough characters') 
    except:
        print('salam')


import cv2
frame = cv2.imread('images/img3.jpeg')
plate=run_models(frame) 

# t=0
# while t<50:
#     try:
#         t+=1
#         print('attempt %s'%t)
#         img=cv2.imread('../square/1 (%s).jpg'%t)
#         cv2.putText(img=img, text=run_models(img), org=(50, 100), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=3, color=(0, 255, 0),thickness=3)
#         cv2.imwrite('../square_num/%s.jpg'%t, img)
#     except:
#         print('not found')
        # height = img2.shape[0]
        # width = img2.shape[1]
        # if(int(height)*int(width)>80000):
        #     cv2.imwrite('salam.jpg',img)
        #     regions = ['mx', 'kz'] # Change to your country
        #     with open('salam.jpg', 'rb') as fp:
        #         response = requests.post(
        #             'https://api.platerecognizer.com/v1/plate-reader/',
        #             data=dict(regions=regions),  # Optional
        #             files=dict(upload=fp),
        #             headers={'Authorization': 'Token 771fe0a5712926ba9a76732dbc7dfbf84aa70cd5'})
        #     res=response.json()
        #     return res['results'][0]['plate']