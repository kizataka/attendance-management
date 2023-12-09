from io import BytesIO
from streamlit_option_menu import option_menu
import requests
import pandas as pd
import streamlit as st
import json
import datetime
import math

backend_url = 'http://127.0.0.1:8000'

st.title('勤怠管理アプリ')

# メニュー欄
with st.sidebar:
    selected = option_menu('Main Menu', ['勤怠入力', '勤怠管理', '従業員登録'],
                           icons=['pencil-square', 'table', 'person-plus-fill'],
                           menu_icon='cast',
                           default_index=0)

if selected == '勤怠入力':
    st.header('[勤怠入力ページ]')

    # 従業員データを取得
    response = requests.get(f'{backend_url}/users/')
    if response.status_code == 200:
        users = response.json()
    else:
        users = []

    user_names = {user['user_id']: user['name'] for user in users}

    user_name = st.selectbox('氏名を選択してください', options=list(user_names.values()), key='user')
    st.write('')

    # 出退勤の打刻
    if user_name:
        st.write('出勤、または退勤ボタンを押して打刻してください')
        st.write('')

        start_button = st.button('出勤', type='primary', use_container_width=True)  # 出勤ボタン

        st.write('')
        st.write('')

        end_button = st.button('退勤', use_container_width=True)  # 退勤ボタン

        # 出勤時刻の記録
        if start_button:
            selected_user_id = [user_id for user_id, name in user_names.items() if name == user_name][0]
            attendance_data = {
                'user_id': selected_user_id,
                'time_in': datetime.datetime.now().isoformat()
            }
            attendance_response = requests.post(f'{backend_url}/attendance/', json=attendance_data)
            if attendance_response.status_code == 200:
                st.success('出勤時刻が記録されました')
            else:
                st.error('出勤時刻の記録に失敗しました')
                st.write("レスポンスコード:", attendance_response.status_code)
                st.write("レスポンス内容:", attendance_response.json())

        # 退勤時刻の記録
        elif end_button:
            selected_user_id = [user_id for user_id, name in user_names.items() if name == user_name][0]
            attendance_data = {
                'user_id': selected_user_id,
                'time_out': datetime.datetime.now().isoformat()
            }
            attendance_response = requests.patch(f'{backend_url}/attendance/', json=attendance_data)
            if attendance_response.status_code == 200:
                st.success('退勤時刻が記録されました')
            else:
                st.error('退勤時刻の記録に失敗しました')
                st.write("レスポンスコード:", attendance_response.status_code)
                st.write("レスポンス内容:", attendance_response.json())

elif selected == '勤怠管理':
    st.header('[勤怠管理ページ]')
    st.write('')
    st.markdown('##### ここでは各従業員の勤務データを確認できます')

    # デフォルトの日付範囲をアプリを開いた月に設定するための定義
    today = datetime.date.today()
    first_day_of_month = datetime.date(today.year, today.month, 1)
    first_day_of_next_month = datetime.date(today.year + (today.month // 12), ((today.month % 12) + 1), 1)
    last_day_of_month = first_day_of_next_month - datetime.timedelta(days=1)

    # 従業員情報を取得
    response = requests.get(f'{backend_url}/users/')
    if response.status_code == 200:
        users = response.json()
    else:
        users = []

    user_names = {user['user_id']: user['name'] for user in users}  # 従業員の名前リスト

    # 勤務データ検索フォーム
    with st.form('input_data'):
        st.markdown('#### 勤務データ検索フォーム')
        user_name = st.selectbox('従業員を選択してください', options=list(user_names.values()), key='user')
        from_to = st.date_input('取得したいデータの日付範囲を設定してください', value=[first_day_of_month, last_day_of_month])
        st.write('')
        st.write('設定が完了したら以下の検索ボタンを押してください')
        submit_button = st.form_submit_button('検索', type='primary', use_container_width=True)

    # 検索結果を表示
    if submit_button:
        if user_name and from_to:
            selected_user_id = [user_id for user_id, name in user_names.items() if name == user_name][0]  # 指定された従業員のIDを取得
            start_date, end_date = from_to  # 日付範囲の設定

            attendance_response = requests.get(f'{backend_url}/attendance/{selected_user_id}')  # 指定された従業員の勤務データを取得
            
            if attendance_response.status_code == 200:
                attendance_records = attendance_response.json()
                filtered_records = [record for record in attendance_records if start_date <= datetime.datetime.strptime(record['date'], '%Y-%m-%d').date() <= end_date]  # 日付範囲による絞り込み
                
                if len(filtered_records) > 0:  # 該当するデータがある場合
                    st.write('')
                    st.markdown(f'##### {user_name}さんの{start_date}から{end_date}の勤務状況を表示しています')
                    st.write('')

                    df_user = pd.DataFrame(filtered_records)  # データフレームの作成
                    df_user['time_in'] = df_user['time_in'].apply(lambda x: pd.to_datetime(x).strftime('%H:%M:%S'))
                    df_user['time_out'] = df_user['time_out'].apply(lambda x: pd.to_datetime(x).strftime('%H:%M:%S') if pd.notnull(x) else None)
                    df_user['working_hours'] = df_user.apply(lambda row: (datetime.datetime.strptime(row['time_out'], '%H:%M:%S') - datetime.datetime.strptime(row['time_in'], '%H:%M:%S')).total_seconds() / 3600 if row['time_out'] is not None else None, axis=1)
                    
                    user_response = requests.get(f'{backend_url}/user/{selected_user_id}')  # 従業員の時給を取得
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        hourly_wage = user_data['hourly_wage']
                    else:
                        st.error('従業員情報の取得に失敗しました')

                    df_user['wage'] = df_user['working_hours'] * hourly_wage  # 給料のカラム
                    df_user = df_user.round({'working_hours': 2, 'wage': 0})  # 小数点の調整
                    df_user = df_user[['date', 'time_in', 'time_out', 'working_hours', 'wage']]  # 表示するカラムの設定
                    df_user = df_user.rename(columns={
                        'date': '日付',
                        'time_in': '出勤時刻',
                        'time_out': '退勤時刻',
                        'working_hours': '勤務時間（時間）',
                        'wage': '給料（円）'
                    })

                    # 集計結果を表示
                    working_days = len(df_user)
                    sum_working_hours = df_user['勤務時間（時間）'].fillna(0).sum()  # データが入っていない場合はそこを0に
                    sum_wage = math.floor(df_user['給料（円）'].fillna(0).sum())
                    sum_wage = int(sum_wage)
                    sum_wage = "{:,}".format(sum_wage)  # カンマ表記

                    st.markdown('###### 勤務実績：')
                    col1, col2, col3 = st.columns(3)
                    col1.metric('勤務日数', f'{working_days}日')
                    col2.metric('合計勤務時間', f'{sum_working_hours}時間')
                    col3.metric('給与',f'{sum_wage}円')
                    st.write('')

                    # データフレームの表示
                    st.markdown('###### 詳細：')
                    st.table(df_user)

                    # データフレームをエクセルに変換する関数
                    def df_to_xlsx(df):
                        byte_xlsx = BytesIO()
                        writer_xlsx = pd.ExcelWriter(byte_xlsx, engine="xlsxwriter")
                        df.to_excel(writer_xlsx, index=False, sheet_name="Sheet1")
                        ##-----必要に応じてexcelのフォーマット等を設定-----##
                        workbook = writer_xlsx.book
                        worksheet = writer_xlsx.sheets["Sheet1"]
                        format1 = workbook.add_format({"num_format": "0.00"})
                        worksheet.set_column("A:A", None, format1)
                        writer_xlsx.save()
                        ##---------------------------------------------##
                        workbook = writer_xlsx.book
                        out_xlsx = byte_xlsx.getvalue()
                        return out_xlsx
                    
                    # データフレームをエクセルとしてダウンロード
                    xlsx = df_to_xlsx(df_user)
                    st.download_button(label="Excelファイルとしてダウンロード", data=xlsx, file_name=f"{user_name}_{start_date}_{end_date}.xlsx")

                else:   # 該当するデータがない場合
                    st.warning('該当するデータはありません')
            else:
                st.error('データの取得に失敗しました')
                st.write("レスポンスコード:", attendance_response.status_code)
                st.write("レスポンス内容:", attendance_response.json())

elif selected == '従業員登録':
    st.header('[従業員登録ページ]')
    st.write('')
    st.markdown('##### ここでは勤怠管理に使用する従業員の情報を登録することができます')

    # 従業員データの登録
    with st.form('input_data'):
        st.markdown('#### 従業員登録フォーム')
        name = st.text_input(label='氏名を入力してください')
        hourly_wage = st.number_input("時給（半角）を入力してください", min_value=0, step=50)
        data = {
            'name': name,
            'hourly_wage': hourly_wage
        }
        st.write('')
        st.write('入力が完了したら登録ボタンを押してください')
        submit_button = st.form_submit_button('登録', type='primary', use_container_width=True)

        if submit_button:
            if name and hourly_wage > 0:
                headers = {'Content-Type': 'application/json'}
                user_response = requests.post(
                    f'{backend_url}/user/',
                    json=data,
                    headers=headers
                )
                if user_response.status_code == 200:
                    st.success('登録が完了しました')
                else:
                    st.error('登録に失敗しました')
            else:
                st.warning('氏名と時給の両方を記入してください')

    st.write('')

    # 従業員一覧の表示
    st.markdown('#### 従業員一覧')

    users_response = requests.get(f'{backend_url}/users/')
    if users_response.status_code == 200:
        users = users_response.json()
    else:
        users = []

    if users:
        # データフレームの作成
        df = pd.DataFrame(users)
        df['index'] = range(1, len(df)+1)
        df = df[['index', 'user_id', 'name', 'hourly_wage']]

        # カラム名の表示
        header_col1, header_col2, header_col3, header_col4 = st.columns(4)
        header_col1.markdown('#### ID')
        header_col2.markdown('#### 氏名')
        header_col3.markdown('#### 時給')
        header_col4.markdown('#### 削除')

        # 各行のデータを表示
        for index, row in df.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            col1.write(row['user_id'])
            col2.write(row['name'])
            col3.write(f'{row["hourly_wage"]}円')

            # 従業員データの削除
            if col4.button('登録情報を削除', key=f'delete_{row["user_id"]}', type='primary'):
                delete_response = requests.delete(f'{backend_url}/user/{row["user_id"]}')
                if delete_response.status_code == 200:
                    st.success('従業員データが削除されました')
                else:
                    st.error('従業員データの削除に失敗しました')
    else:
        st.warning('登録されている従業員はいません')