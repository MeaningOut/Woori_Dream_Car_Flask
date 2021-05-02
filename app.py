from flask import Flask, request, jsonify
from model import model

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/refined-cars')
def cars():
    '''
        요청 방식
        GET http://localhost:5000/refined-cars?people=5&body-type=suv&environmental-protection=Y&fuel-economy=Y&boycott-in-japan=Y&patriotic-campaign=Y&vegan=N
    '''
    # 인승
    people = request.args.get('people')
    people = int(people)

    # 바디 타입
    body_type = request.args.get('body-type')

    # 환경 보호
    environmental_protection = request.args.get('e')

    # 연비 좋은 차
    fuel_economy = request.args.get('f')

    # 일본 불매
    boycott_in_japan = request.args.get('b')

    # 애국 캠페인
    patriotic_campaign = request.args.get('p')

    # 비건자동차
    vegan = request.args.get('v')

    # 추천 리스트 받아오기
    result = model.return_recommendations(people, body_type, environmental_protection, fuel_economy, boycott_in_japan, patriotic_campaign, vegan)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
