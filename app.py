from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/refined-cars')
def cars():
    '''
        요청 방식
        GET http://localhost:5000/refined-cars?people=5&body-type=소형&environmental-protection=Y&fuel-economy=Y&boycott-in-japan=Y&patriotic-campaign=Y&vegan=N
    '''
    # 인승
    people = request.args.get('people')
    # 바디 타입
    body_type = request.args.get('body-type')
    # 환경 보호
    environmental_protection = request.args.get('environmetal-protection')
    # 연비 좋은 차
    fuel_economy = request.args.get('fuel-economy')
    # 일본 불매
    boycott_in_japan = request.args.get('boycott-in-japan')
    # 애국 캠페인
    patriotic_campaign = request.args.get('patriotic-campaign')
    # 비건자동차
    vegan = request.args.get('vegan')

    return jsonify({"people": people, "body_type": body_type, "environmental_protection": environmental_protection, "fuel_economy": fuel_economy, "boycott_in_japan": boycott_in_japan, "patriotic_campaign": patriotic_campaign, "vegan": vegan})

if __name__ == '__main__':
    app.run()
