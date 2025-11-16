import pandas as pd


def show_dataframe(st, df):
    df_to_display = df.reset_index(drop=True)  # 重置索引从0开始
    df_to_display.index += 1
    st.dataframe(df_to_display)


def handle_date_column(df, column_name, _format='%Y/%m/%d %H:%M'):
    df[column_name] = pd.to_datetime(df[column_name], format=_format).dt.normalize()
