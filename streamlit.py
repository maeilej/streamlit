import openai
import streamlit as st
from streamlit_chat import message
from streamlit_folium import folium_static
import requests
import pandas as pd
import random
import time
import numpy as np
from PIL import Image
import folium
import streamlit.components.v1 as components
from elasticsearch import Elasticsearch

        

with st.sidebar:
    # App Gallery 메뉴
     choose = st.selectbox("All About Smart Farm Fruits", ["Fruit Searching", "ChatBot", "Fruit Recommendation", "Dashboard"],
                         index=0,
                         format_func=lambda x: f"✨ {x}" if x == "Fruit Searching" else f"🤖 {x}" if x == "ChatBot" else f"🍓 {x}" if x == "Fruit Recommendation" else f"👓 {x}")

if choose == "Fruit Searching":
        
        
    # Elasticsearch 호스트 및 포트 설정
        es = Elasticsearch(['https://~endpoint'], http_auth=('ID', 'PW'))

    # Streamlit 애플리케이션 UI 구성
        st.title('새로운 신품종 검색')
        st.write('----------------------------')
        search_query = st.text_input('원하는 과일을 입력하면 신품종을 추천해드립니다!')

    # Elasticsearch에 쿼리를 보내고 결과를 표시
        if st.button('검색'):
            res = es.search(index="new_variety", body={"query": {"match": {"type": search_query}}, 'size': 1000})
           
            
            for hit in res['hits']['hits']:
            # 각 결과를 카드 형태로 표시
                st.markdown(f"## {hit['_source']['title']}", unsafe_allow_html=True)
                st.image(hit['_source']['img'], caption="이미지", use_column_width=True, width=20)
        
                # 기능과 종류 표시
                
                if "fuction" not in hit['_source'].keys() :
                    st.write(' ')
                else :
                    st.markdown(f"**기능:** {hit['_source']['fuction']}", unsafe_allow_html=True)
                
                st.markdown(f"**종류:** {hit['_source']['type']}", unsafe_allow_html=True)
        
                # 'see more' 버튼 추가
                with st.expander("View more details!"):
                    if "url" not in hit['_source'].keys() :
                        st.write(' ')
                    else :
                        st.write(f"[Download about this fruit!!]({hit['_source']['url']})")
                st.write('----------------------------')



elif choose == "ChatBot":

    # OpenAI API 키 설정
    openai.api_key = 'ai_private_key'
    system_instruction = """
너는 과일추천자야. 
아래는 딸기 종류야. 

장희 딸기, 설향 딸기, 금실 딸기, 죽향 딸기, 메리퀸 딸기, 비타베리, 킹스베리, 만년설 등의 딸기가 있습니다.

▶ 장희 딸기
장희 딸기는 겨울 딸기 중 가장 먼저 출하되는 품종으로 신맛이 거의 없는 딸기입니다.
다만 올해 유독 맹맛의 장희 딸기가 많으니 선별해서 구매해 주세요.
장희 딸기는 끝이 설향이나 금실에 비해 뽀족한 타원형의 형태를 띠고 있습니다.
그리고 1.5kg(750gX2팩) 단위로 들어오고 있습니다.
▶ 설향 딸기
설향 딸기는 대한민국 딸기의 70% 이상을 차지하는 국민대표 딸기 품종입니다.
시중에서 딸기를 구매하시면 대부분 설향 딸기라고 보시면 되겠습니다.
새콤 7 : 달콤 3 이 평균 식감이며 딸기 중에서는 단단함이 덜 한 품종입니다.
단, 가격이 좋은 딸기입니다.
▶ 금실 딸기
금지옥엽 같이 귀한 딸기라는 뜻의 금실은 달고 약한 복숭아 향이 나는 특징이 있습니다.
달콤하면서 과육 또한 단단하고 치밀하여 드시는 식감이 좋은 금실 딸기입니다.
일반적으로 달콤 7 : 새콤 3 이 평균입니다.
몸도 단단하고 하여 케이크 및 디저트 용으로 사용하기 좋습니다.
단, 설향이나 장희에 비해 가격이 비쌉니다.

위의 메뉴 말고는 없다고 생각하면 돼 
""" 
    messages = [{"role": "system", "content": system_instruction}] 

    def generate_response(user_input):
        # OpenAI로부터 응답 생성
        client= openai.ChatCompletion.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 과일 추천자야"},
            {"role": "user", "content": user_input},
        ],
        temperature=0.7,
        max_tokens=2048)

        # 응답 텍스트 추출 및 줄바꿈 제거
        response = ""
        if "choices" in client and client.choices:
            for choice in client.choices:
               response += choice.get("message", {}).get("content", "")
                
        else:
            # 처리할 응답이 없는 경우에 대한 예외 처리
            response = "No response from the model."

        return response

    st.header("🤖 Smartfarm Chatbot")

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    with st.form('form', clear_on_submit=True):
        user_input = st.text_input('You: ', '', key='input')
        submitted = st.form_submit_button('Send')

        if submitted and user_input:
            # 사용자 입력에 대한 응답 생성
            output = generate_response(user_input)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(output)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            # 번역된 사용자 입력과 생성된 응답을 표시
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))

elif choose == "Fruit Recommendation":
        
            
        def strawberry_recommendation_test():
            
            recommendation = None
            NO_recommendation = None
            recommendations = []
            
            st.title("🍓 딸기추천🍓")

            messages = [
                "딸기 종류는 많은데...",
                "내가 찾는 딸기는 뭔지 모르겠다면?",
                "나에게 딱! 맞는 딸기를 추천해드립니다!"
            ]
            
            st.write("")
            st.write("")
            
            # 세 가지 문구를 1초 간격으로 표시
            for msg in messages:
                st.write(msg)
                time.sleep(1)
            st.write("--------")
            
            # 단맛에 대한 선택
            sweet_preference = None  # 변수를 미리 정의합니다.
            sour_preference = None
            intensity_preference = None
            
            col1, col2, col3 = st.columns(3)
            
            # 맞춤 취향 별 선택지

            # 단맛에 대한 선택
            with col1:
                st.subheader("당도")
                sweet_preference = st.radio("", (None, '보통', '상', '최상'), key='sweet_preference')
            
            # 신맛에 대한 선택
            with col2:
                st.subheader("산미")
                sour_preference = st.radio("", (None, '약함', '보통', '강함'), key='sour_preference')
            
            # 경도에 대한 선택
            with col3:
                st.subheader("경도")
                intensity_preference = st.radio("", (None, '부드러움','단단함'), key='intensity_preference')
                
            recommendation = None
            NO_recommendation = None
            recommendations = []

            # 하나라도 선택되지 않은 경우 알림 표시
            if sweet_preference is None or sour_preference is None or intensity_preference is None:
                st.warning("각 문항마다 하나의 선택지를 선택해주세요.")
                return
            
            
            st.write("--------")

            # 모든 가능한 딸기 종류 결정
            if sweet_preference == '상'  and sour_preference == '약함' and intensity_preference =='단단함':
                recommendations.extend(['금실', '메리퀸'])
            elif sweet_preference == '최상'  and sour_preference == '보통' and intensity_preference =='단단함':
                recommendations.append('죽향')
            elif sweet_preference == '상'  and sour_preference == '약함' and intensity_preference =='부드러움':
                recommendations.append('장희')
            elif sweet_preference == '상'  and sour_preference == '보통' and intensity_preference =='부드러움':
                recommendations.extend(['만년설', '옐로우글램'])
    
            elif sweet_preference == '보통'  and sour_preference == '보통' and intensity_preference =='단단함':
                recommendations.extend(['아리향', '비타베리'])
            elif sweet_preference == '보통'  and sour_preference == '보통' and intensity_preference =='부드러움':
                recommendations.extend(['설향', '킹스베리'])
            elif sweet_preference == '보통' and sour_preference == '강함' and intensity_preference =='부드러움':
                recommendations.append('골든벨')
            elif sweet_preference == '보통' and sour_preference == '강함' and intensity_preference =='단단함':
                recommendations.append('육보')
            elif sweet_preference == '상' and sour_preference == '보통' and intensity_preference =='단단함':
                recommendations.append('샤이투')
        
            else:
                st.write("")
                st.write("")
                NO_recommendation = st.subheader("새로운 취향의 탄생! \n 아쉽게도 아직 조건에 맞는 딸기가 나오지 않았어요💫")
    
            # 모든 추천 딸기에 대한 이미지와 설명 추가
            if recommendations:
                for recommendation in recommendations:
                    st.subheader(f"추천하는 딸기 종류는 '{recommendation}'입니다.")
            
                    if recommendation == '설향':
                        st.image('https://tohomeimage.thehyundai.com/PD/PDImages/S/5/6/4/2810000057465_00.jpg?RS=720x864', caption='설향', use_column_width=True)
                        st.write("설향은 복숭아를 연상시키는 산미가 적당한 단맛과 잘 어우러지고 부드러운 식감을 바탕으로 싱그러운 수분을 가득 느낄 수 있습니다.")
                    elif recommendation == '금실':
                        st.image('https://img.choroc.com/newshop/goods/026429/026429_1.jpg', caption='금실', width=30, use_column_width=True)
                        st.write("금실은 과육이 단단하고 드라이해 씹는 맛을 느낄 수 있습니다. 특히 단맛 뒤로 강한 복숭아향과 은은한 산미를 즐길 수 있습니다.")
                    elif recommendation == '죽향':
                        st.image('https://cdn.011st.com/11dims/resize/600x600/quality/75/11src/product/5583160026/B.jpg?747000000', caption='죽향', use_column_width=True)
                        st.write("죽향은 강렬한 단맛과 적당한 산미를 띄고 야생화 꿀향을 풍부하게 느낄 수 있습니다. 단단한 질감을 가지고 있어 장기보관에 유리합니다.")
                    elif recommendation == '메리퀸':
                        st.image('https://tohomeimage.thehyundai.com/PD/PDImages/S/1/8/8/8806079872881_00.jpg?RS=720x864', caption='메리퀸', use_column_width=True)
                        st.write("메리퀸(Merry Queen)은 '모든 이에게 즐거움을 주는 딸기의 여왕'이라는 뜻을 담은 딸기로, 담양군에서 10년 간 연구 개발한 품종으로 매향의 단단함과 설향의 당도를 모두 지닌 진한 딸기맛을 가진 신품종입니다.")
                    elif recommendation == '장희':
                        st.image('https://sanencheong.com/data/goods/21745/2023/11/_temp_17008140469241view.jpg', caption='장희', use_column_width=True)
                        st.write("장희는 길쭉하고 끝이 뾰족한 모양이 특징입니다. 강한 단맛과 수분이 가득해 입에서 녹는듯한 부드러운 식감을 자랑합니다.")
                    elif recommendation == '만년설':
                        st.image('https://www.m-i.kr/news/photo/202101/788269_564746_357.jpg', caption='만년설', use_column_width=True)
                        st.write(
                            "만년설딸기는 항산화작용을 하는 카테킨, 케르세틴 성분이 많이 함유되어 있어, 몸의 혈전을 녹여주는 기능성 딸기입니다. 달콤한 맛이 강하게 올라오며 끝무렵에 살짝 올라오는 적당한 산미, 부드러운 과육이 특징입니다. 마치 부드럽고 달콤한 사탕과 같은 딸기입니다.")
            
                    elif recommendation == '아리향':
                        st.image('https://cdn.011st.com/11dims/resize/600x600/quality/75/11src/product/2667328913/B.jpg?47000000', caption='아리향', use_column_width=True)
                        st.write("아리향은 달걀에 가까운 남다른 크기로 입안 가득 찬 식감을 자랑합니다. 단단한 과육으로 쉽게 무르지 않아 고운 붉은색을 띄는 아리향의 매력을 오래 느낄 수 있습니다. ")
                    elif recommendation == '비타베리':
                        st.image('https://mblogthumb-phinf.pstatic.net/MjAyMzAyMjRfNTIg/MDAxNjc3MjI0NzkzMzM5.62KIOGvzF8_9Jqxy3Q7ix4CxAKkP27vOAqlPd5jKaXcg.5NDX9gJmI7zWHxaRmfqb__ZGcDyMOsscY6PBHNCfLGcg.JPEG.crispynote/717A3014.jpg?type=w800', caption='비타베리', use_column_width=True)
                        st.write("비타베리는 이름처럼 비타민C가 가득 함유된 딸기입니다. 은은한 단맛과 강렬한 산미로 지친 하루에 활기를 충전해보세요!")
                    elif recommendation == '킹스베리':
                        st.image('https://image.kyobobook.co.kr/newimages/giftshop_new/goods/400/1041/hot1675316874935.jpg', caption='킹스베리', use_column_width=True)
                        st.write("킹스베리는 '딸기의 제왕'이라는 수식어와 같이 일반 딸기보다 두 배가량 크고 복숭아향을 가득 머금고 있습니다. ")
                    elif recommendation == '육보':
                        st.image('https://oasisproduct.cdn.ntruss.com/62659/thumb/300', caption='육보', use_column_width=True)
                        st.write("육보는 둥글고 붉은 과육으로 '레드펄'이라고도 불립니다. 과육이 치밀하고 강렬한 산미가 딸기의 새콤달콤함을 잘 나타냅니다.")
                    elif recommendation == '샤이투':
                        st.image('https://cdn.newsfreezone.co.kr/news/photo/202307/486625_465689_248.jpg', caption='샤이투', use_column_width=True)
                        st.write("샤이투는 사랑스러운 분홍빛이 매력적인 딸기입니다. 붉은 빛이 연하다고 달달한 맛이 뒤쳐질 것이라 생각하면 오산입니다! 새콤달콤 딸기의 맛을 제대로 머금고 있답니다!")
                    elif recommendation == '옐로우글램':
                        st.image('https://www.fntoday.co.kr/news/photo/202303/289500_189240_1437.jpg', caption='옐로우글램', use_column_width=True)
                        st.write("옐로우글램은 기존 빨간 딸기에 비해 노랑 빛깔의 띄고 있고, 식감이 부드럽고 향이 좋아 옐로우글램을 찾는 수요층이 점차 늘어나고 있습니다. 알록달록 예쁜 딸기를 찾고 있다면 시도해볼만한 값진 딸기입니다!")
                    else:
                        st.write("")
                        st.write("")
                        NO_recommendation = st.subheader("새로운 취향의 탄생! \n 아쉽게도 아직 조건에 맞는 딸기가 나오지 않았어요💫")
                
        def grape_recommendation_test():
            st.title("🍇 포도추천🍇")

            messages = [
                "포도 종류는 많은데...",
                "내가 찾는 포도는 뭔지 모르겠다면?",
                "나에게 딱! 맞는 포도를 추천해드립니다!"
            ]
            
            st.write("")
            st.write("")
            
            for msg in messages:
                st.write(msg)
                time.sleep(1)
            st.write("--------")
            
            # 가로로 선택지를 나열하기 위해 columns 레이아웃 사용
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("당도")
                sweet_preference = st.radio("", (None, '보통', '상', '최상'), key='sweet_preference')

            with col2:
                st.subheader("산미")
                sour_preference = st.radio("", (None, '약함', '보통', '강함'), key='sour_preference')

            with col3:
                st.subheader("껍질")
                peel_preference = st.radio("", (None, '껍질째 먹을래요','껍질은 빼고 먹을래요'), key='peel_preference')



            recommendation = None
            NO_recommendation = None
            recommendations = []

            # 하나라도 선택되지 않은 경우 알림 표시
            if sweet_preference is None or sour_preference is None or peel_preference is None:
                st.warning("각 문항마다 하나의 선택지를 선택해주세요.")
                return
            
            st.write("--------")
            
            if sweet_preference == '상'  and sour_preference == '보통' and peel_preference =='껍질은 빼고 먹을래요':
                recommendations.extend(['거봉', '흑보석'])
            elif sweet_preference == '보통'  and sour_preference == '보통' and peel_preference =='껍질은 빼고 먹을래요':
                recommendations.append('캠벨포도')
                
            elif sweet_preference == '상'  and sour_preference == '약함' and peel_preference =='껍질은 빼고 먹을래요':
                recommendations.append('충랑포도')
            elif sweet_preference == '보통'  and sour_preference == '약함' and peel_preference =='껍질은 빼고 먹을래요':
                recommendations.append('진옥')
     
            elif sweet_preference == '상'  and sour_preference == '강함' and peel_preference =='껍질째 먹을래요':
                recommendations.append('스텔라')    
            elif sweet_preference == '최상'  and sour_preference == '약함' and peel_preference =='껍질째 먹을래요':
                recommendations.extend(['마이하트포도', '블랙사파이어'])
            elif sweet_preference == '최상'  and sour_preference == '강함' and peel_preference =='껍질째 먹을래요':
                recommendations.append('홍주씨들리스')
            elif sweet_preference == '상' and sour_preference == '보통' and peel_preference =='껍질째 먹을래요':
                recommendations.append('슈팅스타')
            elif sweet_preference == '최상' and sour_preference == '보통' and peel_preference =='껍질째 먹을래요':
                recommendations.append('골드스위트')
            elif sweet_preference == '상' and sour_preference == '약함' and peel_preference =='껍질째 먹을래요':
                recommendations.append('루비스위트')
            elif sweet_preference == '보통' and sour_preference == '강함' and peel_preference =='껍질째 먹을래요':
                recommendations.append('레드클라렛')
        
            # 나머지 조건들 추가

            if recommendations:
                for recommendation in recommendations:
                    st.subheader(f"추천하는 포도 종류는 '{recommendation}'입니다.")
                    # 각 포도에 대한 설명 추가
                    
                    if recommendation == '캠벨포도':
                        st.image('https://mblogthumb-phinf.pstatic.net/MjAyMTA5MjVfMjU1/MDAxNjMyNTQzODE4Mjg4.OvDO42wiKb8EGzQg3xVaJVZiTU9vnDM4FqwTW3whMYsg.9KOGrfTIxWn2jweHjAz_BQ384siba2kU0qA0FNyR3KUg.JPEG.agriculture1234/9ac004713204b.jpg', caption='캠벨포도', use_column_width=True)
                        st.write("캠벨포도는 맑고 깨끗한 단맛이 특징이며, 적당한 단맛과 신선한 포도 향이 어우러져 대중적인 포도입니다.")
                    elif recommendation == '거봉':
                        st.image('https://dnvefa72aowie.cloudfront.net/businessPlatform/bizPlatform/profile/center_biz_7290132/1690813937810/600afbb4ac114b8a37c5ce70019d20334746d5fcaf10de76dfa632991b8782d0.jpeg?q=95&s=1440x1440&t=inside', caption='거봉', use_column_width=True)
                        st.write("거봉은 달콤한 맛이 특징이며, 입안에 넣으면 살짝 증류된 꿀 같은 당도가 입안을 감싸며 달콤한 즐거움을 선사합니다. 큼지막한 포도알이 특징으로 입 안에서 즐거운 식감을 느낄 수 있습니다.")
                    elif recommendation == '충랑포도':
                        st.image('https://www.nongupin.co.kr/news/photo/202101/92282_51620_1516.jpg', caption='충랑포도', use_column_width=True)
                        st.write("충랑포도는 캠벨포도와 거봉을 접목한 포도로, 껍질이 두터워 터짐이 적습니다. 특히 젤리와 같은 쫀득한 식감으로 기분 전환되는 달달함을 선사합니다.")
                    elif recommendation == '흑보석':
                        st.image('https://sitem.ssgcdn.com/15/31/04/item/1000571043115_i1_750.jpg', caption='흑보석', use_column_width=True)
                        st.write("흑보석은 진한 보라색이 감돌고 완전히 익었을 때 단맛과 신맛이 조화로워 기존의 알 굵은 포도의 단조로운 단맛과 달리 톡톡 터지는 느낌을 받을 수 있습니다.")
                    elif recommendation == '스텔라':
                        st.image('https://www.amnews.co.kr/news/photo/202109/47134_34541_458.png', caption='스텔라', use_column_width=True)
                        st.write("스텔라는 모양과 향이 독특한 고당도 포도 품종입니다. 산 함량이 0.44%로 다른 품종보다 높아 새콤달콤한 맛을 느낄 수 있으며, 유기산 중 시키믹산 함량이 높아 체리 ‘좌등금’ 품종과 비슷한 맛과 향을 느낄 수 있습니다.")
                    elif recommendation == '진옥':
                        st.image('https://nongsaro.go.kr/ps/img/curation/20160829/images/contents_03_01.png', caption='진옥', use_column_width=True)
                        st.write(
                            "진옥포도는 농촌진흥청에서 2004년에 육성한 포도 품종으로, 아름다운 흑청색을 띕니다. 자연스러운 단맛과 은은한 산미가 합쳐져 기분좋은 신선함을 선사합니다.")
                    elif recommendation == '마이하트포도':
                        st.image('https://m.eloasis.co.kr/web/product/big/202308/0717c68d45e44a9a87007ad79fc7566d.png', caption='마이하트포도', use_column_width=True)
                        st.write("포도로 사랑을 말한다. 이름 그대로 마이하트포도는 특별한 대상에게 선물하기 아주 좋은 특별한 포도입니다. 높은 당도만큼 달달한 사랑을 전해보세요! ")
                    elif recommendation == '홍주씨들리스':
                        st.image('https://mblogthumb-phinf.pstatic.net/MjAyMzAyMjRfNTIg/MDAxNjc3MjI0NzkzMzM5.62KIOGvzF8_9Jqxy3Q7ix4CxAKkP27vOAqlPd5jKaXcg.5NDX9gJmI7zWHxaRmfqb__ZGcDyMOsscY6PBHNCfLGcg.JPEG.crispynote/717A3014.jpg?type=w800', caption='홍주씨들리스', use_column_width=True)
                        st.write("홍주씨들러스는 농촌진흥청에서 개발한 국내육성품종 적포도입니다. 샤인머스켓과 비슷한 고당도의 포도지만, 단맛속에 숨겨진 새콤함이 조화로운 점이 특징입니다. 항산화 성분까지 풍부한 기능성 포도로 점차 인기가 많아지고 있습니다.")
                    elif recommendation == '슈팅스타':
                        st.image('http://www.newsfm.kr/data/photos/20230937/art_16946946322618_c1da2e.jpg', caption='슈팅스타', use_column_width=True)
                        st.write("슈팅스타는 맛과 간편성, 다양성 등을 중시하는 소비자를 위해 만든 품종으로, 과일 향·신선한 풀 향을 내는 ‘헥산알(hexanal)’, ‘리날로올(linalool)’과 같은 향기 성분이 풍부하여 솜사탕과 같은 맛이 특징입니다. '슈팅스타'라는 이름은 포도알 색이 균일하지 않고 다양한 크기의 점들이 사방으로 퍼진 듯한 형태를 띠는데, 마치 하늘에서 불꽃이 ‘팡’ 터져 흩어지는 모습을 연상케 한다는 점에서 착안하였습니다.")
                    elif recommendation == '블랙사파이어':
                        st.image('https://i.namu.wiki/i/cLhMMKgMBR_A6O5JwjtiSn38T2usLIppQ5gPv7auo3R_X17yfHEChFzrc4u4Ket7SWQr-ZMXgLaaS5C-nKdjPw.webp', caption='블랙사파이어', use_column_width=True)
                        st.write("블랙사파이어는 크고 길쭉한 관 모양에 끝 부분이 보조개처럼 쑥 들어간 모습이 특징으로, 식감은 아삭아삭하고 당도가 높아 인기가 많습니다.")
                    elif recommendation == '골드스위트':
                        st.image('https://shop-phinf.pstatic.net/20230823_190/1692780272695jTi3p_JPEG/%EB%B3%B4%EC%A0%95_PO4A4258.jpg?type=w860', caption='골드스위트', use_column_width=True)
                        st.write("골드스위트는 샤인머스켓보다 더 껍질이 연하고 달콤한 아카시아 향이 가득 퍼지는 포도입니다. 청포도 특유의 씁쓸한 맛이 없고 한 입에 먹기 편해 아이들도 간편히 먹을 수 있습니다.")
                    elif recommendation == '루비스위트':
                        st.image('https://shop-phinf.pstatic.net/20230829_189/1693300683234Vb7XG_JPEG/%EB%A3%A8%EB%B9%84%EC%8A%A4%EC%9C%84%ED%8A%B809.jpg?type=w860', caption='루비스위트', use_column_width=True)
                        st.write("루비스위트는 적포도 계열로, 사과처럼 청량한 식감과 아카시아 향이 특징입니다. 높은 당도를 띄며 씨가 없어 간편히 먹기 좋은 포도입니다.")
                    elif recommendation == '레드클라렛':
                        st.image('https://tohomeimage.thehyundai.com/PD/PDImages/S/6/1/2/2810000301216_00.jpg?RS=720x864', caption='레드클라렛', use_column_width=True)
                        st.write("레드클라렛은 경북농업기술원에서 개발한 적포도입니다. 알이 굵고 강렬한 단맛이 뒷받침된 시원한 맛이 특징입니다.")    

            else:
                st.write("")
                st.write("")
                NO_recommendation = st.subheader("새로운 취향의 탄생! \n 아쉽게도 아직 조건에 맞는 포도가 나오지 않았어요💫")
                
        def peach_recommendation_test():
            st.title("🍑 복숭아 추천 🍑")

            messages = [
                "복숭아 종류는 많은데...",
                "내가 찾는 복숭아는 뭔지 모르겠다면?",
                "나에게 딱! 맞는 복숭아를 추천해드립니다!"
            ]
            

            # 세 가지 문구를 1초 간격으로 표시
            for msg in messages:
                st.write(msg)
                time.sleep(1)
            st.write("--------")
                
            # 맞춤 취향 별 선택지
            # 가로로 선택지를 나열하기 위해 columns 레이아웃 사용
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("당도")
                sweet_preference = st.radio("", (None, '보통', '상', '최상'), key='sweet_preference')

            with col2:
                st.subheader("산미")
                sour_preference = st.radio("", (None, '약함', '보통', '강함'), key='sour_preference')

            with col3:
                st.subheader("경도")
                intensity_preference = st.radio("", (None, '말랑', '중간','단단'), key='intensity_preference')

            recommendation = None
            NO_recommendation = None
            recommendations = []

            # 하나라도 선택되지 않은 경우 알림 표시
            if sweet_preference is None or sour_preference is None or intensity_preference is None:
                st.warning("각 문항마다 하나의 선택지를 선택해주세요.")
                return
            
            st.write("--------")
            
            # 모든 가능한 복숭아 종류 결정
            if sweet_preference == '보통'  and sour_preference == '강함' and intensity_preference =='말랑':
                recommendations.extend(['신황도', '썬프레'])
            elif sweet_preference == '최상'  and sour_preference == '약함' and intensity_preference =='말랑':
                recommendations.append('레드골드')
            elif sweet_preference == '최상'  and sour_preference == '보통' and intensity_preference =='말랑':
                recommendations.append('용궁백도')
            elif sweet_preference == '상'  and sour_preference == '보통' and intensity_preference =='말랑':
                recommendations.append('미백도')
            elif sweet_preference == '보통'  and sour_preference == '하' and intensity_preference =='말랑':
                recommendations.append('용성황도')
        
            elif sweet_preference == '상'  and sour_preference == '보통' and intensity_preference =='중간':
                recommendations.append('그레이트')
            elif sweet_preference == '최상'  and sour_preference == '강함' and intensity_preference =='중간':
                recommendations.append('아까즈끼 ER') 
            elif sweet_preference == '보통'  and sour_preference == '약함' and intensity_preference =='중간':
                recommendations.append('용성황도') 
            elif sweet_preference == '상'  and sour_preference == '약함' and intensity_preference =='중간':
                recommendations.append('납작복숭아') 
            elif sweet_preference == '상'  and sour_preference == '강함' and intensity_preference =='중간':
                recommendations.append('엘바트') 
        
            elif sweet_preference == '상'  and sour_preference == '보통' and intensity_preference =='단단':
                recommendations.extend(['황귀비','천도'])
            elif sweet_preference == '보통'  and sour_preference == '강함' and intensity_preference =='단단':
                recommendations.append('대명')
            elif sweet_preference == '최상'  and sour_preference == '약함' and intensity_preference =='단단':
                recommendations.append('만천하')     
        
            
            # 모든 추천 복숭아에 대한 이미지와 설명 추가
            if recommendations:
                for recommendation in recommendations:
                    st.subheader(f"추천하는 복숭아 종류는 '{recommendation}'입니다.")
            
                    if recommendation == '썬프레':
                        st.image('https://cdn-optimized.imweb.me/upload/S202104263584dd527ccd5/a6b0dc888b9f5.jpeg?w=1536', caption='썬프레', use_column_width=True)
                        st.write("썬프레는 후숙 전에는 산미가 강하게 찌르듯이 올라오며 후숙 후에는 당도가 올라와 은은한 단맛을 바탕으로 찌릿한 산미를 느낄 수 있습니다.")
                    elif recommendation == '레드골드':
                        st.image('https://www.shutterstock.com/image-photo/best-heirloom-peach-varieties-country-260nw-2056377701.jpg', caption='레드골드', use_column_width=True)
                        st.write("레드골드는 당도80% 산미 20%로 아삭함과 새콤달콤함을 모두 갖춘 복숭아로 후숙을 할수록 당도가 높아져 천도중에서도 왕으로 불리는 복숭아입니다. ")
                    elif recommendation == '용궁백도':
                        st.image('https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTA5MDhfMjAy%2FMDAxNjMxMTA5MDkzMjg5.7b1jT2lHOcQN1EDRUETLekAOxXNVCE_TCi1-tLrLzQ0g.hkm6tUwZV1xkjET24xxVrl-Cay6V2G13huQWPqpbSZMg.JPEG.taeyun950108%2F20210908%25A3%25DF214054.jpg&type=sc960_832', caption='용궁백도', use_column_width=True)
                        st.write("용궁백도는 달달함을 가득 품은 쫀쫀한 식감의 복숭아입니다. 껍질을 당기면 쭉 쉽게 까질 정도로 연하고 후숙할수록 단 맛이 진해지는 특징을 가지고 있습니다.")    
                    elif recommendation == '신황도':
                        st.image('https://roout.co.kr/m/p/u/fnGJBa7/c/1eKvPZ42sZR/i/3qaHBcDSJL1.jpg', caption='신황도', use_column_width=True)
                        st.write("신황도는 강렬한 산미를 바탕으로 은은한 단맛이 돋보이는 복숭아입니다.")
                    elif recommendation == '미백도':
                        st.image('https://ojsfile.ohmynews.com/down/images/1/photo70_181018_1[227518].jpg', caption='미백도', use_column_width=True)
                        st.write("미백도는 수분이 가득하고 달달한 맛이 부드러움과 함께 가득 차오르는 것이 특징이다. ")    
                    elif recommendation == '용성황도':
                        st.image('http://www.traveli.co.kr/repository/read/contents/K20150825162023725.JPG', caption='용성황도', use_column_width=True)
                        st.write('용성황도는 적당한 단맛과 낮은 산미로 은은하지만 향긋한 복숭아 향을 가득 머금은 복숭아로 유명하다.')
                    elif recommendation == '황귀비':
                        st.image('https://sitem.ssgcdn.com/97/08/75/item/1000549750897_i1_750.jpg', caption='황귀비', use_column_width=True)
                        st.write("황귀비는 후숙 전에 새콤달콤하면서 아삭하게도 즐길 수 있지만 2~3일 후숙하면 14브릭스까지 올라갈 정도로 높은 당도를 자랑합니다. 이 때 망고처럼 쫀득한 식감으로 즐길 수 있습니다.")
                    elif recommendation == '대명':
                        st.image('https://mblogthumb-phinf.pstatic.net/MjAxNzA3MzFfMTgx/MDAxNTAxNDkzMDcxMTc5.2DY_7aMuBHFluifXeg63dFNnob6knIHllQ0Rm3Rrbysg.cI5u-9q6YjuAG7ldF-EfoiR4urtIMVJP1HqzeHIhyxog.JPEG.justwind703/IMG_2200.JPG?type=w800', caption='대명', use_column_width=True)
                        st.write("대명은 털이 아주 미세하고 과육이 매우 단단하여 씹는 맛을 즐길 수 있습니다. 더운 여름 날 얼음을 아작아작 씹어먹는 듯한 딱복을 선호하는 분들에게 강력 추천합니다.")
                    elif recommendation == '만천하':
                        st.image('https://lh3.googleusercontent.com/proxy/L7CFvzuLCLv-5L6AtK4e3wWEUrHcDLYVV4aECFiNowAd61jWJxxxm9OtUAliQNsQZ3wMhsiWjaaQBvcLa20xYuN8SeuRBr8PBg', caption='만천하', use_column_width=True)
                        st.write("만천하는 매우 강렬한 당도를 자랑하며 산미가 아주 약한 복숭아입니다. 단단한 식감을 바탕으로 장기 보관에도 유리합니다")
                    elif recommendation == '천도':
                        st.image('https://s3.ap-northeast-2.amazonaws.com/cuma.co.kr/resources/products/26603/represent/aiTTNNxyS17TgUEi-resized.jpeg', caption='천도', use_column_width=True)
                        st.write("천도 복숭아는 백도와 황도의 장점만을 모은 복숭아로, 털이 없고 새콤달콤 쫀득한 식감을 자랑합니다.")
                    elif recommendation == '그레이트':
                        st.image('https://www.bariwon.com/data/editor/1808/0bee7ccf49d1bb4153a75e23e211c601_1533156296_0132.jpg', caption='그레이트', use_column_width=True)
                        st.write("그레이트 복숭아는 달콤하고 은은한 달콤함이 돌아가며, 신선하고 산뜻한 향이 느껴집니다. 그레이트 복숭아는 복숭아 특유의 부드럽고 촉촉한 식감과 함께 은은한 산도가 어우러져 상큼한 맛을 내어 이름처럼 맛이 그레이트합니다.")
                    elif recommendation == '아까즈끼 ER':
                        st.image('https://mblogthumb-phinf.pstatic.net/MjAxNjExMjhfMjY2/MDAxNDgwMzM2ODU5NDM2.DqNnF5-o4gci_WETmfllI4X23pcK0q-tUwaP_wzT3l8g.tipIbX6TyCLD4Ig5ks7UzOX21N1XHMEdHdHVv5MIyJUg.JPEG.ds3efv/%EA%B7%B8%EB%A0%88%EC%9D%B4%ED%8A%B8%EC%A0%90%EB%B3%B4.jpg?type=w420', caption='아까즈끼 ER', use_column_width=True)
                        st.write("아까즈끼 ER 복숭아는 강렬한 단맛과 함께 톡쏘는 산미로 더운 여름날의 햇빛을 가득 머금고 고운 빛깔로 고급스러운 느낌을 선사합니다. 부드럽고 깔끔한 후맛이 남아 식사 후 디저트로 제격입니다.")
                    elif recommendation == '용성황도':
                        st.image('https://ecimg.cafe24img.com/pg195b65599565048/cbfarmmall/web/product/big/20221025/d21b72e134a4c0989e708da1cee919ee.jpg', caption='용성황도', use_column_width=True)
                        st.write("용성황도는 적당한 당도에 은은한 산미를 느낄 수 있는 부담없는 복숭아입니다. 적당한 과육 경도에 너무 무르지도, 딱딱하지도 않은 균형잡힌 식감을 선사합니다.")
                    elif recommendation == '납작복숭아':
                        st.image('https://img.hankyung.com/photo/202107/01.26876028.1.jpg', caption='납작복숭아', use_column_width=True)
                        st.write("납작 복숭아는 매우 강렬한 단맛을 지니고 있으며 수분 함량이 높아 한 입 베어 무는 순간 과즙이 입안에 가득 퍼져 복숭아의 진한 풍미를 느낄 수 있습니다.")
                    elif recommendation == '엘바트':
                        st.image('https://sitem.ssgcdn.com/87/31/68/item/2097001683187_i1_750.jpg', caption='엘바트', use_column_width=True)
                        st.write("엘바트는 뛰어난 식감과 짙은 향으로 황도의 황제라고 불리는 복숭아입니다. 노란 과육 속 진한 달콤함이 가득합니다. 또한 쫀득한 식감과 풍부한 향으로 남녀노소 누구나 기분 좋게 즐길 수 있습니다. 풍요로운 가을의 시작을 알리는 엘바트 복숭아로 행복이 넘치는 하루하루를 보내 보세요!")
                
                
            else:
                st.write("")
                st.write("")
                NO_recommendation = st.subheader("새로운 취향의 탄생! \n 아쉽게도 아직 조건에 맞는 복숭아가 나오지 않았어요💫")
        

        if __name__ == '__main__':
            st.header('과일을 선택하세요')
            fruit_choice = st.selectbox(' ', ("선택하세요!","🍓 딸기", "🍇 포도", "🍑 복숭아"))
            st.write("--------")
            
            if fruit_choice == "🍓 딸기":
                strawberry_recommendation_test()
            elif fruit_choice == "🍇 포도":
                grape_recommendation_test()
            elif fruit_choice == "🍑 복숭아":
                peach_recommendation_test()
    
elif choose == "DataFrame":
    

# 데이터 로드 및 표시
    image = Image.open('daily_sales.png')
    st.image(image, caption='Daily Sales')