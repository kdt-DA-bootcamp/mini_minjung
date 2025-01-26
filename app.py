#  streamlit 배포

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 전체 제목 추가
st.markdown("<h2 style='text-align: center; color: white;'>콜센터 고객 불만 데이터 시각화 분석</h2>", unsafe_allow_html=True)

# 데이터 로드
data = pd.read_csv("processed_january_negative_customers.csv")

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 환경
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 숫자형 불만 점수 추가
score_mapping = {"긍정": 1, "중립": 5, "부정": 7, "강한 불만": 10}
data['satisfaction_score_numeric'] = data['satisfaction_score'].map(score_mapping)

# 연령대 필드 추가
bins = [0, 19, 29, 39, 49, 59, 69, 79, 100]
labels = ["10대 이하", "20대", "30대", "40대", "50대", "60대", "70대", "80대 이상"]
data['age_group'] = pd.cut(data['age'], bins=bins, labels=labels, right=False)

# 성별 텍스트 매핑 (gender_text만 남김)
gender_mapping = {0: "여성", 1: "남성"}
data['gender_text'] = data['gender'].map(gender_mapping)

# 1. 히트맵
st.markdown("<h4 style='text-align: center; color: white;'>1. 상담 유형별 연령대와 높은 불만 점수</h4>", unsafe_allow_html=True)

# 상담 유형별 연령대와 높은 불만 점수를 계산
pivot_data = data.pivot_table(
    index='age_group',
    columns='type_text',
    values='satisfaction_score_numeric',
    aggfunc='mean',
    fill_value=0
)

# 데이터에 인덱스 번호 추가
pivot_data.reset_index(inplace=True)  # 기존 인덱스를 초기화
pivot_data['번호'] = range(1, len(pivot_data) + 1) 

# 수정된 히트맵 코드
fig1 = plt.figure(figsize=(12, 8))
sns.heatmap(
    pivot_data.set_index('번호').iloc[:, 1:],  # 인덱스 번호를 포함한 히트맵 생성
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    linewidths=0.5,
    linecolor='black',
    cbar_kws={'shrink': 0.8}
)
plt.title("상담 유형별 연령대와 높은 불만 점수", fontsize=16, weight='bold')
plt.xlabel("상담 유형", fontsize=12)
plt.ylabel("연령대", fontsize=12)
plt.tight_layout()
st.pyplot(fig1)

# 히트맵 데이터프레임 출력 및 다운로드
st.write("히트맵에 사용된 데이터:")
st.dataframe(pivot_data)

csv1 = pivot_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="히트맵 데이터 다운로드 (CSV)",
    data=csv1,
    file_name='heatmap_data.csv',
    mime='text/csv',
)

# 2. 성별 및 연령대별 불만 점수 분석
st.markdown("<h4 style='text-align: center; color: white;'>2. 성별 및 연령대별 불만 점수 분석</h4>", unsafe_allow_html=True)

# 성별 및 연령대별 불만 점수 계산
max_scores = data.groupby(["gender_text", "age_group"])["satisfaction_score_numeric"].mean().reset_index()

# 성별별로 최고 점수에 해당하는 연령대를 명시적으로 계산
highlight_groups = max_scores.loc[max_scores.groupby("gender_text")["satisfaction_score_numeric"].idxmax()]

# 차트 생성
fig2 = plt.figure(figsize=(12, 6))
g = sns.FacetGrid(data, col="gender_text", height=6, aspect=1)
g.map(sns.barplot, "age_group", "satisfaction_score_numeric", ci=None, order=labels, palette="coolwarm")

# 최고 점수 막대 강조 및 숫자 레이블 추가
highlight_color = "red"  # 강조 색상

for ax, gender in zip(g.axes.flat, ["여성", "남성"]):
    gender_data = max_scores[max_scores["gender_text"] == gender]
    max_age_group = gender_data.loc[gender_data["satisfaction_score_numeric"].idxmax(), "age_group"]

    for bar, age_group in zip(ax.patches, labels):
        if age_group == max_age_group:
            bar.set_color(highlight_color)
            bar.set_edgecolor("black")
        else:
            bar.set_edgecolor("black")

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{bar.get_height():.1f}",
            ha="center", va="bottom", fontsize=10, color="black"
        )

# 범례 추가
handles = [plt.Rectangle((0, 0), 1, 1, color=highlight_color, label="최고 불만 점수")]
g.fig.legend(handles=handles, loc="upper right", fontsize=10, title="범례")

# 축 제목 및 제목 설정
g.set_titles("{col_name}")
g.set_axis_labels("연령대", "평균 불만 점수")
g.fig.subplots_adjust(top=0.9)
g.fig.suptitle("성별 및 연령대별 불만 점수 분석", fontsize=16, weight="bold", y=1.05)

for ax in g.axes.flat:
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

st.pyplot(g.fig)

# 3. 성별 및 연령대별 불만 점수 추이 (라인 차트)
st.markdown("<h4 style='text-align: center; color: white;'>3. 성별 및 연령대별 불만 점수 추이</h4>", unsafe_allow_html=True)

line_data = data.groupby(["gender_text", "age_group"])["satisfaction_score_numeric"].mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 6))

sns.lineplot(
    data=line_data,
    x="age_group",
    y="satisfaction_score_numeric",
    hue="gender_text",
    marker="o",
    linewidth=2.5,
    palette={"여성": "blue", "남성": "orange"},
    ax=ax,
)

# 숫자 레이블 추가
for gender in line_data["gender_text"].unique():
    gender_data = line_data[line_data["gender_text"] == gender]
    for x, y in zip(gender_data["age_group"], gender_data["satisfaction_score_numeric"]):
        ax.text(x, y + 0.1, f"{y:.1f}", ha="center", fontsize=10, color="black")

# 그래프 설정
ax.set_title("성별 및 연령대별 불만 점수 추이", fontsize=16, weight="bold")
ax.set_xlabel("연령대", fontsize=12)
ax.set_ylabel("평균 불만 점수", fontsize=12)
ax.set_xticks(range(len(line_data["age_group"].unique())))
ax.set_xticklabels(line_data["age_group"].unique(), rotation=45, ha="right")
ax.legend(title="성별", fontsize=10, loc="upper right")
plt.grid(axis="y", linestyle="--", alpha=0.7)

st.pyplot(fig)

# 데이터프레임 출력 및 다운로드
st.write("성별 및 연령대별 불만 점수 데이터:")
st.dataframe(line_data)

csv3 = line_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="성별 및 연령대별 데이터 다운로드 (CSV)",
    data=csv3,
    file_name='gender_age_trend.csv',
    mime='text/csv'
)