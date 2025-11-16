import pandas as pd
import streamlit as st

from components import period_filter, grade_dist, dept_dist
from utils import handle_date_column, show_dataframe

TITLE = '公司员工统计分析表'
VERSION = 'v0.1'
st.set_page_config(page_title=TITLE, layout="wide")
st.title(TITLE + " " + VERSION)

CN_NAME = '姓名'
CN_BIRTH_DATE = '出生年月日'
CN_HIRE_DATE = '入职日期'
CN_FIRE_DATE = '离职日期'
CN_GRADE = '最高学历'
CN_DPT = '二级部门'
CN_STATE = '状态'
REQUIRED_CNS = [CN_NAME, '性别', CN_BIRTH_DATE, '年龄', '婚姻状况', '学习形式', CN_GRADE,
                '最高学历毕业院校', '政治面貌', CN_STATE, '职位类型', CN_DPT, '岗位名称', '岗位性质', '工龄',
                '合同到期日', CN_HIRE_DATE, CN_FIRE_DATE, '社保购买公司']

# ===== 文件上传 =====
uploaded_file = st.sidebar.file_uploader("上传 CSV 文件", type=["csv", "xls", "xlsx"])


def main():
    if not uploaded_file:
        st.info("请上传 CSV / EXCEL 文件以进行分析。")
        return

    # 读取 CSV
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("不支持的文件格式。")
        return
    if delta := (set(REQUIRED_CNS) - set(df.columns)):
        st.error(f"缺少必填列[ {', '.join(delta)} ]，请检查文件。")
        return

    df = df[REQUIRED_CNS]

    # 处理日期类型输入
    handle_date_column(df, CN_BIRTH_DATE)
    handle_date_column(df, CN_HIRE_DATE)
    handle_date_column(df, CN_FIRE_DATE)

    st.sidebar.subheader("筛选器")

    # 日期筛选器
    start_period, end_period = period_filter(df, CN_HIRE_DATE)

    # 筛选在职人员视图
    hired_view = df[(df[CN_HIRE_DATE].dt.to_period('M') <= max(start_period, end_period)) & (
            (df[CN_FIRE_DATE].isna()) | (df[CN_FIRE_DATE].dt.to_period('M') > max(start_period, end_period)))]

    # 筛选离职/辞退人员视图
    base_filter = (df[CN_HIRE_DATE].dt.to_period('M') <= max(start_period, end_period)) & (
            (df[CN_FIRE_DATE].notna()) & (df[CN_FIRE_DATE].dt.to_period('M') <= max(start_period, end_period)))
    leaved_view = df[base_filter & (df[CN_STATE] == '离职')]
    fired_view = df[base_filter & (df[CN_STATE] == '辞退')]

    # 筛选在职人员的部门
    departments = df[CN_DPT].dropna().unique().tolist()
    departments.sort()

    # 展示汇总指标
    st.subheader('统计指标')
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.metric("在职人数", len(hired_view))
    with col2:
        st.metric("离职人数", len(leaved_view))
    with col3:
        st.metric("辞退人数", len(fired_view))
    with col4:
        st.metric("部门数", len(departments))

    st.subheader('部门人员分布')
    dept_dist(hired_view, leaved_view, fired_view, CN_DPT, CN_NAME)

    st.subheader('学历分布')
    grade_dist(hired_view, departments, CN_GRADE, CN_NAME, CN_DPT)

    st.subheader('人员清单')
    tab1, tab2, tab3 = st.tabs(["在职", "离职", "辞退"])
    # 展示在职人员清单
    with tab1:
        show_dataframe(st, hired_view)

    # 展示离职人员清单
    with tab2:
        show_dataframe(st, leaved_view)

    # 展示辞退人员清单
    with tab3:
        show_dataframe(st, fired_view)


main()
