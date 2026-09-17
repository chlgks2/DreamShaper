# Dream Shaper — 초기 버전 : 서버 경유 파일 전송 (2023.09) [폐기됨]
#
# 이미지와 음원을 서버가 직접 받아 로컬에 저장하던 방식입니다.
# 음원 한 곡이 수십 MB라 서버가 트래픽을 감당하지 못했고,
# ffmpeg 청크 분할로도 해결되지 않아 S3 직접 업로드로 구조를 바꿨습니다.
#
# 「무엇을 시도했다가 왜 바꿨는지」를 남기기 위해 보존합니다.
# 개발 중 디버그 출력이 그대로 남아 있는 습작 코드입니다.

from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

print('이게뭘까용1',__name__)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5555)
# elif __name__ != '__main__':
    # print('시발아')
    # app.run(host='0.0.0.0', port=5555)
    

print('이게뭘까용2',__name__)

@app.route('/get_test', methods=['GET'])
def hello():
    print('안녕')
    return '안녕하세요'

import os

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return ("포스트됨요" )



@app.route('/post_test', methods=['POST'])
def hello2():
    # 클라이언트가 보낸 이미지 파일에 접근하기 위해 request.form.get를 사용합니다.
    # uploaded_file = request.form.get('img_')
    uploaded_file  = request.files['img_']
    uploaded_music  = request.files['music_']
    print('접속완료1')
    # 파일이 업로드되지 않았다면 예외 처리합니다.
    if not uploaded_file:
        print('개시발')
        return "파일을 업로드하지 않았습니다.", 400
    if not uploaded_music:
        print('음원파일 안옴')
        return "음원파일 안옴요", 400
    
    file_path = "./" + uploaded_music.filename
    uploaded_music.save(file_path)
    print('저장완료')

    # 업로드된 파일을 로컬에 저장합니다.
    image_file_path  = "./" + uploaded_file.filename
    uploaded_file.save(image_file_path )
    print('저장완료')
    
    return "파일이 성공적으로 업로드되었습니다."    

    # if uploaded_file:
    #     # 이미지 파일이 존재하면 파일의 내용을 읽고 처리합니다.
    #     file_contents = uploaded_file.read()

    #     # 현재 디렉토리에 이미지를 저장합니다.
    #     # 파일 이름은 'uploaded_image.jpg'로 지정합니다.
    #     save_path = os.path.join(os.getcwd(), 'uploaded_image.jpg')
        
    #     with open(save_path, 'wb') as f:
    #         f.write(file_contents)

    #     return '이미지 파일 업로드 및 저장 완료'
    # else:
    #     return '이미지 파일이 업로드되지 않았습니다.'

@app.route('/', methods=['GET'])
def eeeee():
    return 'eㄹㄷㄹㄷㄹㄷㄹ'
@app.route('/test', methods=['POST'])
def Test():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400
        print('aaaaaaaaa')
        print(data['message'])
        result = data['message']
        return jsonify({"니가보낸거": result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# datas = {
#     "message": "안녕 난 난 동북이모델링"
# }

# url = "http://172.20.10.5:3000"
# response = requests.post('http://172.17.79.139:3000', data=datas, verify=False)
# print(response.text)    


#172.17.82.82

