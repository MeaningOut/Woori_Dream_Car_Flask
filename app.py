from flask import Flask, request, jsonify
from model import model

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/refined-cars', methods=['POST'])
def cars():
    '''
        요청 방식
        POST http://localhost:5000/refined-cars
    '''
    print(request.values)
    # 인승
    people = int(request.form['people'])

    # 바디 타입
    body_type = request.form['body-type']

    # 환경 보호
    environmental_protection = request.form['environmental-protection']

    # 연비 좋은 차
    fuel_economy = request.form['fuel-economy']

    # 일본 불매
    boycott_in_japan = request.form['boycott-in-japan']

    # 애국 캠페인
    patriotic_campaign = request.form['patriotic-campaign']

    # 비건자동차
    vegan = request.form['vegan']
    print(people, body_type, environmental_protection, fuel_economy, boycott_in_japan, patriotic_campaign, vegan)
    # 추천 리스트 받아오기
    result = model.return_recommendations(people, body_type, environmental_protection, fuel_economy, boycott_in_japan, patriotic_campaign, vegan)
    return jsonify(result)

# imitate woori getNewCarLoanAm
@app.route('/oai/wb/v1/newcar/getNewCarLoanAm', methods=['POST'])
def get_new_car_loan_am():

    params = request.get_json()
    data_header = params['dataHeader']
    data_body = params['dataBody']
    print(data_header, data_body)
    if 'DBPE_ANL_ICM_AM' in data_body and 'CAR_PR' in data_body:
        dbpe_anl_icm_am = data_body['DBPE_ANL_ICM_AM']
        car_pr = data_body['CAR_PR']

        response = dict()
        response['dataHeader'] = dict()
        response['dataBody'] = dict()
        response['dataBody']['HLD_ITCSNO'] = "78900245630"
        response['dataBody']['RSP_TRNO'] = ""
        response['dataBody']['MD_INF'] = ""
        response['dataBody']['ERR_CD'] = ""
        response['dataBody']['ERR_TXT'] = ""
        response['dataBody']['LN_AVL_AM'] = "1000000"
        return jsonify(response), 200
    else:
        return 'Bad request', 400

if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(host='127.0.0.1', debug=True)