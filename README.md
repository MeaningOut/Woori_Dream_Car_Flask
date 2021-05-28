# Woori_Dream_Car_Flask  
- 우리은행 해커톤 Flask 서버

소비신념에 따른 자동차 추천시스템은 Content-based Recommender System으로 구성하였다. 
보통 추천시스템으로 Latent-Factor Model이나 Collaborative Filtering(협업필터링)를 사용하지만 user-to-item 데이터와 user 데이터를 확보하지 못하여
Content-based Recommender System을 선택하였다. 

![img.png](https://github.com/MeaningOut/Woori_Dream_Car_Flask/blob/master/picture1.PNG)

<br><br>

## 1. Utility Matrix 구축하기
먼저 Selenium으로 크롤링한 자동차 정보들을 기반으로 행과 열이 자동차와 Factors로 구성된 Utiltiy Matrix를 구축한다

* Factors : 5가지 소비신념(환경보호, 연비좋은차, 일본불매, 애국캠페인, 비건자동차)로 구성되었다. 
```python
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
```

<br><br>

## 2. 사용자로부터 Factors를 입력받아 user vector를 생성한다
만약 사용자가 선택을 안 한 Factor 요소는 결측값(NaN)이므로 평균으로 빈 칸을 채운다. 

```python
    # user row 생성하기
    def make_user_row(self, e_protection, f_economy, boycott, patriotic, vegan):
        user_row = [None for i in range(5)]
        user_row[0] = (1 if e_protection == 'Y' else 0.5)
        user_row[1] = (1 if f_economy == 'Y' else 0.1)
        user_row[2] = (1 if boycott == 'Y' else 0.5)
        user_row[3] = (1 if patriotic == 'Y' else 0.5)
        user_row[4] = (1 if vegan == 'Y' else 0.5)
        return user_row
```

<br><br>

## 3. Cosine Similarity를 통해 각 자동차의 vector와 user vector의 유사도를 구한다.
각 행(row)과 user vector의 유사도를 구한뒤 결과를 저장한다

```python
        for idx in range(len(u_matrix)):
            # id
            compare_id = int(u_matrix.loc[idx][-1])

            # 유사도 비교
            compare_np = u_matrix.loc[idx][1:-1]
            cosine = cosine_similarity([user_row], [compare_np])[0][0]

            result.append({'id': compare_id, 'cosine': cosine})
```

<br><br>

## 4. 유사도가 높은 순대로 N개만큼 추출하여 Spring boot 서버에게 값들을 넘겨준다.
단, 유사도 결과가 기준치인 0.86이 넘어야지만 서버로 전달될 수 있다. 
0.86이라는 수치는 테스트셋을 생성하여 CASE를 4가지로 나누어 실험한 결과 True인 셋의 최소 유사도들의 평균을 측정하여 나온 수치이다. 

```python
 # 기준치 0.86 이상인 것들만 추출
        thresholds = 0.86

        indices = [i['id'] for i in result if i['cosine'] >= thresholds]
        result_data = self.metaData.loc[indices]
```

<br><br>

## 전체코드

``` python
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
```

## 추천시스템 성능 평가 여부
추천 모델을 평가할 때는 하나의 값을 얼마나 잘 맞추었는지 중점을 두지 않는다. 
이는 추천이 결국 사용자에게 좋아하는 아이템을 선정하려는 결정에 도움을 주려는 목적을 가지고 있기 때문이다.
따라서 얼마나 잘 맞추었는지 보다는 추천된 아이템 중 어떤 아이템이 좋은 아이템이고 어떤 아이템이 나쁜 아이템인지에 중점을 둔다.
Precision과 Recall을 사용하여 여러 번의 실험 중 K개의 아이템 중 사용자가 선택한 아이템이 있다면 0 or 1로 계산하여 총 평가 횟수 중 
맞춘 개수의 Percentage를 구하는 방법으로 성능을 평가할 예정이다

* Precision : 선택된 아이템들 중 몇 개의 아이템이 연관된 아이템인가?
* Recall : 연관된 아이템들 중 몇개의 아이템이 선택되었는가?


