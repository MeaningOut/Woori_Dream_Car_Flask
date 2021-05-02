# !/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import json
import re

from sklearn import preprocessing
from sklearn.metrics.pairwise import cosine_similarity


class Model:
    def __init__(self):
        cars = pd.read_csv('model/cars_0430.csv', encoding='utf-8-sig')
        cars['id'] = cars.index

        car_cols = ['id', 'big_title', 'sub_title', 'min_price', 'max_price', 'occupancy', 'fuel', 'fuel_efficiency', 'company', 'origin']
        self.metaData = cars[car_cols]

        # 차 외형 json 읽기
        with open('model/cars_appearance.json', 'r', encoding='utf-8') as file:
            car_appearance = json.load(file)
            self.suv_list = car_appearance['suv']
            self.mpv_list = car_appearance['mpv']

    # 인원수, 외형 거르기
    def make_candidate(self, people=0, body_type=''):
        # 인원 수 거르기
        self.metaData = self.metaData[self.metaData['occupancy'] >= people]

        # 외형 거르기
        is_suv = self.metaData['big_title'].isin(self.suv_list)
        is_mpv = self.metaData['big_title'].isin(self.mpv_list)

        if body_type == "suv":
            self.metaData = self.metaData[is_suv]
        elif body_type == "mpv":
            self.metaData = self.metaData[is_mpv]
        elif body_type == "common":
            self.metaData = self.metaData[~(is_suv | is_mpv)]
        return self.metaData

    # Utility Matrix 생성
    def get_utility_matrix(self, df):
        taste_cols = ['e_protection', 'fuel_economy', 'boycott', 'patriotic', 'vegan', 'id']

        # 환경보호
        df[taste_cols[0]] = df['fuel'].map(self.toFuel)

        # 연비 좋은 차
        df['fuel_efficiency'] = df['fuel_efficiency'].map(self.toKML)

        # 연비 정규화
        min_max_scaler = preprocessing.MinMaxScaler()
        columns_names_to_normalize = ['fuel_efficiency']

        x = df[columns_names_to_normalize].values
        x_scaled = min_max_scaler.fit_transform(x)
        df_temp = pd.DataFrame(x_scaled, columns=columns_names_to_normalize, index=df.index)
        df[taste_cols[1]] = df_temp

        # 일본 불매
        df[taste_cols[2]] = df['company'].map(self.toBoycott)

        # 애국 캠페인
        df[taste_cols[3]] = df['origin'].map(self.toPatriotic)

        # 비건 자동차
        df[taste_cols[4]] = df['big_title'].map(self.toVegan)

        return df[taste_cols]

    # 환경보호
    def toFuel(self, value):
        fuel_type = {
            '전기': 1.0, '수소': 1.0, '전기 , 수소': 1.0, '전기 , 가솔린': 0.8,
            'LPG': 0.6, '가솔린': 0.5, '디젤': 0.4, '연료': 0.3
        }

        if value in fuel_type.keys():
            return fuel_type[value]
        return None

    # 연비 좋은 차
    def toKML(self, value):
        if pd.isnull(value):
            return None
        result = None

        # 괄호 안 문자열 제거 and \n 제거
        value = re.sub("\(.*\)|\s-\s.*", '', value)
        value = value.replace("\n", " ")

        if ('km/ℓ' in value) or ('ℓ/100km' in value):
            value = value.replace('ℓ/100km', '').replace('km/ℓ', '')
            # 최대 연비 추출
            result = max([float(s) for s in re.findall(r'-?\d+\.?\d*', value)])
        elif 'mpg' in value:
            max_num = max([float(s) for s in re.findall(r'-?\d+\.?\d*', value)])
            result = round((max_num * 0.425144), 2)
        elif 'km/kg' in value:
            max_num = max([float(s) for s in re.findall(r'-?\d+\.?\d*', value)])
            result = (max_num/5.7)  # 수소 1km = 휘발유 5.7l
        elif 'km/kWh' in value:
            min_num = min([float(s) for s in re.findall(r'-?\d+\.?\d*', value)])

            if min_num >= 2 and min_num < 3:
                result = 19.5
            elif min_num >= 3 and min_num < 4:
                result = 14.5
            elif min_num >= 4 and min_num < 5:
                result = 12.5
            elif min_num >= 5 and min_num < 6:
                result = 10.5
            elif min_num >= 6 and min_num < 7:
                result = 9.5
            else:
                result = 7.5
        return result

    # 일본 불매
    def toBoycott(self, value):
        # 일본 브랜드 리스트
        japan_car_brands = ['토요타', '닛산', '혼다', '마쯔다', '미쓰비시', '렉서스', '미쯔오카',
                            '다이하쓰', '스즈키', '사이언', '스바루', '인피니티', '아큐라', '이스즈']

        # 1 : 일본 브랜드에 속하지 않음, 0 : 속함
        if value in japan_car_brands:
            return 0
        return 1

    # 애국 캠페인
    def toPatriotic(self, value):
        if value == '국산':
            return 1
        elif value == '수입':
            return 0

    # 비건 자동차
    def toVegan(self, value):
        # 비건자동차 리스트
        vegan_car_brands = ['2021 아이오닉 5', '2020 BMW i3', '2021 넥쏘', '2020 볼보 XC40 리차지', '2021 EV6', '2021 EV6 GT',
                            '2021 테슬라 사이버트럭', '2021 테슬라 모델3', '2021 테슬라 모델Y', '2021 테슬라 모델S', '2021 테슬라 모델X']

        if value in vegan_car_brands:
            return 1
        else:
            return 0

    # user row 생성하기
    def make_user_row(self, e_protection, f_economy, boycott, patriotic, vegan):
        user_row = [None for i in range(5)]
        user_row[0] = (1 if e_protection == 'Y' else 0.5)
        user_row[1] = (1 if f_economy == 'Y' else 0.1)
        user_row[2] = (1 if boycott == 'Y' else 0.5)
        user_row[3] = (1 if patriotic == 'Y' else 0.5)
        user_row[4] = (1 if vegan == 'Y' else 0.5)
        return user_row

    # 추천 리스트 가져오기
    def get_recommendations(self, df, e_protection, f_economy, boycott, patriotic, vegan):
        u_matrix = self.get_utility_matrix(df)

        # 결측값을 평균으로 채움
        u_matrix['fuel_economy'] = u_matrix['fuel_economy'].fillna(u_matrix['fuel_economy'].mean())

        # user row 생성
        user_row = self.make_user_row(e_protection, f_economy, boycott, patriotic, vegan)

        # 유사도 비교
        u_matrix = u_matrix.reset_index()
        result = []

        for idx in range(len(u_matrix)):
            # id
            compare_id = int(u_matrix.loc[idx][-1])

            # 유사도 비교
            compare_np = u_matrix.loc[idx][1:-1]
            cosine = cosine_similarity([user_row], [compare_np])[0][0]

            result.append({'id': compare_id, 'cosine': cosine})

        # 유사도 내림차순으로 정렬
        result = sorted(result, key=lambda x: x['cosine'], reverse=True)

        # 기준치 0.86 이상인 것들만 추출
        thresholds = 0.86

        indices = [i['id'] for i in result if i['cosine'] >= thresholds]
        result_data = self.metaData.loc[indices]

        # 디버그 - id, big_title, sub_title
        for i in indices:
            print(result_data.loc[i]['id']+1, '  ', result_data.loc[i]['big_title'], ' ', result_data.loc[i]['sub_title'])

        # 리턴값 정제
        recommendations = result_data[['id', 'min_price', 'max_price']]

        # 평균 price 추가 and min_price&max_price 삭제
        recommendations['avg_price'] = (recommendations['min_price'] + recommendations['max_price']) / 2
        recommendations = recommendations.drop(['min_price', 'max_price'], axis=1)

        sim = [i['cosine'] for i in result if i['cosine'] >= thresholds]
        recommendations['similarity'] = sim

        return recommendations


def pearson_sim(u1, u2):
    u1_c = u1 - u1.mean()
    u2_c = u2 - u2.mean()

    denom = np.sqrt(np.sum(u1_c ** 2) * np.sum(u2_c ** 2))
    if denom != 0:
        return np.sum(u1_c * u2_c) / denom
    else:
        return 0


def return_recommendations(people, body_type, e_protection, f_economy, boycott, patriotic, vegan):
    model = Model()

    car_df = model.make_candidate(people, body_type)
    recommendations = model.get_recommendations(car_df, e_protection, f_economy, boycott, patriotic, vegan)

    # 리턴 : DataFrame(id, price, sim)
    # id는 -1빼고 리턴할 것이다.
    # 리턴 자료형 : 리스트, {"id", "avg_price", "similarity"}
    N = 100     # 리턴 갯수 제한 : 100개
    expected_recommendations = []
    for idx, i in enumerate(recommendations.values.tolist()):
        if idx >= N:
            break
        expected_recommendations.append({"id": int(i[0]+1), "avg_price": i[1], "similarity": i[2]})

    # debug
    print('size : ', len(expected_recommendations))
    print(expected_recommendations)

    return expected_recommendations
