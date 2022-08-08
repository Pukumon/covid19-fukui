import streamlit as st
import matplotlib.pyplot as plt
import japanize_matplotlib
import requests
import io
import pandas as pd
from datetime import datetime, date, timedelta, timezone
import numpy as np
import pydeck as pdk
import json
from PIL import Image
import urllib.request


st.sidebar.write("""
## 新型コロナ関連リンク
""")

st.sidebar.write("""
[福井県公認 新型コロナウイルス対策サイト](https://covid19-fukui.com/) 
""")
st.sidebar.write("""
[福井県新型コロナウイルス情報 コロナビ](https://covid19-fukui.bosai-signal.jp) 
""")

st.sidebar.write("""
[福井県新型コロナウイルス感染症のオープンデータ](https://www.pref.fukui.lg.jp/doc/toukei-jouhou/covid-19.html) 
""")

st.sidebar.write("""
[COVID-19 Japan-新型コロナウイルス対策ダッシュボード](https://www.stopcovid19.jp/) 
""")

st.sidebar.write('')
st.sidebar.write("""
(C)2021 Pukumon Go All rights reserved.
""")


# ここからweatherAPI

st.sidebar.write("""
## 福井のお天気情報
""")

url = "https://weatherapi-com.p.rapidapi.com/forecast.json"

querystring = {"q":"fukui","days":"3"}

headers = {
    'x-rapidapi-key': "3dbbb206c5msh3f5cf379ca186f7p10b396jsn4d8d916c30ef",
    'x-rapidapi-host': "weatherapi-com.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

weather = json.loads(response.text)

import ssl
ssl._create_default_https_context = ssl._create_unverified_context #SSL認証に関するエラー返ってきたときの対処法

def forcast(n):
    st.sidebar.write(weather["forecast"]["forecastday"][n]["day"]["condition"]["text"])
    # お天気アイコン表示
    icon_url = "https:" + weather["forecast"]["forecastday"][n]["day"]["condition"]["icon"]
    img_read = urllib.request.urlopen(icon_url).read() #画像データGET
    img_bin = io.BytesIO(img_read) #メモリに保持してディレクトリ偽装みたいなことする
    st.sidebar.image(img_bin)
    
    st.sidebar.write("予想最高気温", weather["forecast"]["forecastday"][n]["day"]["maxtemp_c"], '度')
    st.sidebar.write("予想最低気温", weather["forecast"]["forecastday"][n]["day"]["mintemp_c"], "度")
    st.sidebar.write("日の出", weather["forecast"]["forecastday"][n]["astro"]["sunrise"])
    st.sidebar.write("日の入", weather["forecast"]["forecastday"][n]["astro"]["sunset"])
    

# def weather_icon(i):
#     icon_url = "https:" + weather["forecast"]["forecastday"][i]["day"]["condition"]["icon"]
#     img_read = urllib.request.urlopen(icon_url).read() #画像データGET
#     img_bin = io.BytesIO(img_read) #メモリに保持してディレクトリ偽装みたいなことする
#     st.sidebar.image(img_bin)
    
st.sidebar.write('<b style=color:orange>今日</b>', weather["forecast"]["forecastday"][0]["date"], '<b style=color:orange>の予報</b>', unsafe_allow_html=True)
forcast(0)
# weather_icon(0)

#1時間おきの天気
now = datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M")

if(now < "23:00"):
    st.sidebar.write('<b>1時間おきの予報</b>', unsafe_allow_html=True)

hour_weather = weather["forecast"]["forecastday"][0]["hour"]


for hour in range(24):
    if(hour_weather[hour]["time"][11:16] > now):
        st.sidebar.write(hour_weather[hour]["time"][11:16])
        
        icon_url24 = "https:" + hour_weather[hour]["condition"]["icon"]
        img_read24 = urllib.request.urlopen(icon_url24).read() #画像データGET
        img_bin24 = io.BytesIO(img_read24) #メモリに保持してディレクトリ偽装みたいなことする
        st.sidebar.image(img_bin24)
        
        st.sidebar.write("気温", hour_weather[hour]["temp_c"], "度",  "降水確率", round(hour_weather[hour]["chance_of_rain"], -1), "%")
        # st.sidebar.write(hour_weather[hour]["condition"]["text"])
        # st.sidebar.write("https:" + hour_weather[hour]["condition"]["icon"])

st.sidebar.write("<b style=color:orange>明日</b>", weather["forecast"]["forecastday"][1]["date"], "<b style=color:orange>の予報</b>", unsafe_allow_html=True)
forcast(1)
# weather_icon(1)

st.sidebar.write("<b style=color:orange>明後日</b>", weather["forecast"]["forecastday"][2]["date"], "<b style=color:orange>の予報</b>", unsafe_allow_html=True)
forcast(2)
# weather_icon(2)


    
    


st.title('福井県新型コロナウイルス情報')
now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y/%m/%d %H:%M")
st.info(now + '現在公開分までです\n' + '\nデータ元:福井県新型コロナウイルス感染症のオープンデータhttps://www.pref.fukui.lg.jp/doc/toukei-jouhou/covid-19_d/fil/covid19_patients.csv')
'\n'

url = 'https://www.pref.fukui.lg.jp/doc/toukei-jouhou/covid-19_d/fil/covid19_patients.csv'
r = requests.get(url).content
df = pd.read_csv(io.BytesIO(r), sep=',')
df = df.fillna('非公表').replace({'　': '非公表', '10歳': '10代', '80代　': '80代', '30代 ': '30代'})

# indexの型変更
# df.index = df.index.astype(int)
# df = df.sort_values('No', ascending=False)

st.write('陽性患者属性')
st.dataframe(df[['公表_年月日', '患者_年代',
                 '患者_性別']], width=640, height=200)
'\n'

st.write('日別新規陽性者数')
df_date = pd.to_datetime(df['公表_年月日']).value_counts()
st.bar_chart(df_date)
'\n'

# st.write('居住地別患者数')
# df_area_total = df['患者_居住地'].value_counts(ascending=False)
# st.bar_chart(df_area_total)

# pydeck start
df_latlng = pd.read_csv('./latlng_data.csv')
# st.dataframe(df_latlng, width=800)

# df_join = pd.merge(df['患者_居住地'],
#                    df_latlng[["患者_居住地", "lat", "lon"]],
#                    on="患者_居住地", how="left")

#地域が増えすぎたため非表示

# st.pydeck_chart(pdk.Deck(
#     map_style='mapbox://styles/mapbox/light-v9',
#     initial_view_state=pdk.ViewState(
#         latitude=35.70,
#         longitude=136.00,
#         zoom=8.5,
#         pitch=50,
#         bearing=-27
#     ),
#     layers=[
#         pdk.Layer(
#             'HexagonLayer',
#             data=df_join,
#             get_position='[lon, lat]',
#             radius=800,
#             elevation_scale=50,
#             elevation_range=[0, 500],
#             pickable=True,
#             extruded=True,
#         ),
#     ],
# ))

# pydeck end

st.write('年代別患者数')
df_age = df['患者_年代'].value_counts()
st.bar_chart(df_age)

# 円グラフ
st.write('年代別患者割合')

df_age_pie = df['患者_年代'].value_counts().sort_index()

fig = plt.figure(figsize=(10, 10))

count = len(df_age_pie.index)
cmap = plt.get_cmap('Paired')
color = cmap(np.arange(count))

df_age_pie.plot(kind='pie', autopct=lambda p: '{:.1f}%'.format(p) if p > 1 else '', startangle=90,
                counterclock=False, pctdistance=0.75, labeldistance=1.1, textprops={"fontsize": "16"}, colors=color)
plt.pie([100], colors='white', radius=0.5)
plt.legend(df_age_pie.index, fancybox=True,
           fontsize=12, bbox_to_anchor=(1, 0.9))
plt.title('年代別割合', y=0.46, fontsize=18, color='r')

st.pyplot(fig)
# 円グラフ終わり


st.header('直近の状況')
number = st.number_input('直近何日間のデータを見ますか？', min_value=int(
    1), max_value=None,  step=None, format=None, key=None)


today = datetime.today()
#  + timedelta(hours=+9)
span = today - timedelta(days=number)

today_str = today.strftime('%Y年%m月%d日')
span_str = (span + timedelta(1)).strftime('%Y年%m月%d日')
st.write('直近', number, '日間のデータ', span_str, '〜', today_str)

df_date1 = pd.to_datetime(df['公表_年月日'])

df_span = df[['公表_年月日', '患者_年代',
              '患者_性別']][df_date1 > span]

df_span1 = (df_span != 0)
sum_span = df_span1['公表_年月日'].sum().astype(str)

if (len(df_span.index) == 0):  # emptyよりlenのほうが処理が早い
    st.info('ご指定の期間内に陽性者はおりません')
else:
    st.error('ご指定の期間内の新規陽性者数は' + sum_span + '人です')
    st.write('陽性患者属性')
    st.dataframe(df_span, width=600, height=300)

left_column,  right_column = st.beta_columns(2)

df_date_span = pd.to_datetime(df['公表_年月日'])[
    df_date1 > span].dt.date.value_counts()
if not (df_date_span.empty):
    left_column.write('日別新規陽性者数')
    left_column.bar_chart(df_date_span, height=300)
    left_column.table(df_date_span)

# df_area_span = df['患者_居住地'][df_date1 > span].value_counts()
# if not (df_area_span.empty):
#     center_column.write('居住地別患者数')
#     center_column.bar_chart(df_area_span, height=300)
#     center_column.table(df_area_span)

df_age_span = df['患者_年代'][df_date1 > span].value_counts()
if not (len(df_age_span.index) == 0):
    right_column.write('年代別患者数')
    right_column.bar_chart(df_age_span, height=300)
    right_column.table(df_age_span)

df_age_span_pie = df['患者_年代'][df_date1 > span].value_counts().sort_index()

count = len(df_age_span_pie.index)
cmap = plt.get_cmap('Paired')
color = cmap(np.arange(count))

if not (len(df_age_span.index) == 0):
    fig = plt.figure(figsize=(10, 10))
    df_age_span_pie.plot(kind='pie', autopct=lambda p: '{:.1f}%'.format(
        p) if p > 1 else '', startangle=90, counterclock=False, pctdistance=0.75, labeldistance=1.1, textprops={"fontsize": "16"}, colors=color)
    plt.pie([100], colors='white', radius=0.5)
    plt.legend(df_age_span_pie.index, fancybox=True,
               fontsize=12, bbox_to_anchor=(1, 0.9))
    pie_title = '年代別割合\n' + '直近' + str(number) + '日間'
    plt.title(pie_title,  y=0.46, fontsize=18, color='r')
    st.pyplot(fig)

# pydeck start
if not (len(df_age_span.index) == 0):
    df_latlng = pd.read_csv('./latlng_data.csv')
# st.dataframe(df_latlng, width=800)

    # df_join_span = pd.merge(df_span['患者_居住地'],
    #                         df_latlng[["患者_居住地", "lat", "lon"]],
    #                         on="患者_居住地", how="left")
    # st.write(df_join)

    # st.pydeck_chart(pdk.Deck(
    #     map_style='mapbox://styles/mapbox/light-v9',
    #     initial_view_state=pdk.ViewState(
    #         latitude=35.70,
    #         longitude=136.00,
    #         zoom=8.5,
    #         pitch=50,
    #         bearing=-27
    #     ),
    #     layers=[
    #         pdk.Layer(
    #             'HexagonLayer',
    #             data=df_join_span,
    #             get_position='[lon, lat]',
    #             radius=800,
    #             elevation_scale=50,
    #             elevation_range=[0, 100],
    #             pickable=True,
    #             extruded=True,
    #         ),
    #         pdk.Layer(
    #             'ScatterplotLayer',
    #             data=df_join_span,
    #             get_position='[lon, lat]',
    #             get_color='[200, 30, 0, 160]',
    #             get_radius=800,
    #         ),
    #     ],
    # ))

# pydeck end
