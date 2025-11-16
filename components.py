import datetime

import altair as alt
import pandas as pd
import streamlit as st


def period_filter(df, CN_HIRE_DATE):
    # 生成日期筛选器
    min_date = df[CN_HIRE_DATE].dt.to_period('M').min().to_timestamp().date()
    max_date = datetime.date.today()
    start_date, end_date = st.sidebar.slider(
        "选择年月区间",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format='YYYY-MM'
    )
    start_period = pd.Period(start_date, freq='M')
    end_period = pd.Period(end_date, freq='M')

    return start_period, end_period


def grade_dist(hired_view, departments, CN_GRADE, CN_NAME, CN_DPT):
    selected_departments = st.multiselect("选择部门", departments, placeholder='全部')

    if selected_departments:
        tmp_view = hired_view[hired_view[CN_DPT].isin(selected_departments)]
    else:
        tmp_view = hired_view

    grade_map = {
        '初中': '专科以下',
        '中专': '专科以下',
        '中专/中技': '专科以下',
        '高中': '专科以下',
        '大专': '专科',
        '专科': '专科',
        '本科': '本科',
        '硕士': '硕士',
        '博士': '博士',
    }
    grades = tmp_view[CN_GRADE].map(grade_map)
    category_order = ['专科以下', '专科', '本科', '硕士', '博士']
    if (grades.isna()).any():
        category_order.append('其他学历')
        grades = grades.fillna('其他学历')
    tmp = tmp_view.assign(**{
        CN_GRADE: pd.Categorical(
            grades,
            categories=category_order,
            ordered=True
        )
    })
    grouped = tmp.groupby(CN_GRADE)[CN_NAME].count().reset_index()
    grouped = grouped.rename(columns={CN_NAME: '人数'})
    chart = alt.Chart(grouped).mark_bar().encode(
        x=alt.X(CN_GRADE, sort=category_order),
        y='人数'
    )

    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-2,
    ).encode(
        text='人数'
    )

    st.altair_chart(chart + text, use_container_width=True)


def dept_dist(hired_df, leaved_df, fired_df, dept_col, name_col):
    # 添加状态列
    hired_df = hired_df.copy()
    hired_df['状态'] = '在职'
    leaved_df = leaved_df.copy()
    leaved_df['状态'] = '离职'
    fired_df = fired_df.copy()
    fired_df['状态'] = '辞退'

    # 合并数据
    combined_df = pd.concat([hired_df[[dept_col, name_col, '状态']],
                             leaved_df[[dept_col, name_col, '状态']],
                             fired_df[[dept_col, name_col, '状态']]])

    # 所有部门
    all_depts = combined_df[dept_col].unique()
    all_status = ['在职', '离职', '辞退']

    # 创建所有部门 × 状态组合
    all_combinations = pd.MultiIndex.from_product([all_depts, all_status], names=[dept_col, '状态']).to_frame(
        index=False)

    # 按部门和状态统计人数
    grouped = combined_df.groupby([dept_col, '状态'])[name_col].count().reset_index()
    grouped = grouped.rename(columns={name_col: '人数'})

    # 补全 0 人情况
    grouped_full = pd.merge(all_combinations, grouped, on=[dept_col, '状态'], how='left')
    grouped_full['人数'] = grouped_full['人数'].fillna(0).astype(int)

    # 绘制分组柱状图
    chart = alt.Chart(grouped_full).mark_bar().encode(
        x=alt.X(f'{dept_col}:N', title='部门'),
        y=alt.Y('人数:Q', title='人数'),
        color=alt.Color('状态:N', scale=alt.Scale(range=['#1f77b4', '#ff7f0e', '#ff1111'])),
        tooltip=[dept_col, '状态', '人数'],
        xOffset='状态:N'  # 核心：不同状态柱子并排显示
    ).properties(width=800, height=400)

    # 在柱子上显示人数
    text = alt.Chart(grouped_full).mark_text(
        dy=-5,
        color='black'
    ).encode(
        x=alt.X(f'{dept_col}:N'),
        y=alt.Y('人数:Q'),
        text='人数:Q',
        xOffset='状态:N'
    )

    st.altair_chart(chart + text, use_container_width=True)
