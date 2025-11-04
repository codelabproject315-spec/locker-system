import streamlit as st
import pandas as pd
import numpy as np
import streamlit_authenticator as stauth # 認証ライブラリ
import yaml # 設定ファイル読み込み用
import os # ★★★ Renderのために追加 ★★★

# --- 1. アプリ専用の記憶場所 (session_state) にデータを保存する ---
if 'df' not in st.session_state:
    
    total_lockers = 200
    locker_numbers = [f"{i:03d}" for i in range(1, total_lockers + 1)]
    
    student_ids = [np.nan] * total_lockers
    names = [np.nan] * total_lockers
    
    student_ids[0] = 'S1001' # 001番
    names[0] = '田中 太郎'
    student_ids[1] = 'S1002' # 002番
    names[1] = '鈴木 花子'
    student_ids[3] = 'S1003' # 004番
    names[3] = '佐藤 次郎'
    
    initial_data = {
        'Locker No.': locker_numbers,
        'Student ID': student_ids,
        'Name': names
    }
    st.session_state.df = pd.DataFrame(initial_data)

# --- 2. 認証機能の設定 (パスワード認証版) ---

# Renderの「環境変数」から管理者情報を読み込む
admin_user = os.environ.get("ADMIN_USER")
admin_hash = os.environ.get("ADMIN_HASH")
cookie_name = os.environ.get("COOKIE_NAME")
cookie_key = os.environ.get("COOKIE_KEY")

# 認証ライブラリに渡す「認証情報」の辞書を作成
credentials = {
    "usernames": {
        admin_user: {
            "email": admin_user,
            "name": "Admin User", 
            "password": admin_hash 
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name,
    cookie_key,
    3600
)

# 3. 管理者メールアドレスの設定
ADMIN_EMAIL = admin_user

# --- 4. タブのコンテンツ関数定義 (変更なし) ---

def display_viewer_tab():
    """閲覧・登録用タブの内容を定義する関数（認証不要）"""
    
    st.header('ロッカー空き状況')
    
    df_lockers = st.session_state.df 
    available_lockers = df_lockers[df_lockers['Student ID'].isnull()]
    
    if available_lockers.empty:
        st.warning('現在、空きロッカーはありません。')
    else:
        st.dataframe(available_lockers[['Locker No.']], use_container_width=True, height=300)

    st.divider() 

    st.header('ロッカー新規登録')
    
    available_list_tab1 = available_lockers['Locker No.'].tolist()
    
    if not available_list_tab1:
        st.info('現在、登録できる空きロッカーがありません。')
    else:
        locker_no_reg_tab1 = st.selectbox('空いているロッカーを選択してください:', available_list_tab1, key='reg_locker_select_tab1')
        student_id_reg_tab1 = st.text_input('学籍番号 (例: 2403036)', key='reg_sid_tab1')
        name_reg_tab1 = st.text_input('氏名 (例: 埼玉太郎)', key='reg_name_tab1')
        
        if st.button('この内容で登録する', key='reg_button_tab1'):
            if not student_id_reg_tab1 or not name_reg_tab1:
                st.error('学籍番号と氏名の両方を入力してください。')
            else:
                df_lockers.loc[df_lockers['Locker No.'] == locker_no_reg_tab1, ['Student ID', 'Name']] = [student_id_reg_tab1, name_reg_tab1]
                st.session_state.df = df_lockers 
                st.success(f"【登録完了】ロッカー '{locker_no_reg_tab1}' に '{name_reg_tab1}' さんを登録しました。")
                st.rerun()

def display_admin_tab():
    """管理者用タブの内容を定義する関数（管理者認証が必要）"""
    
    st.header('管理者パネル')
    
    df_lockers = st.session_state.df

    st.subheader('📝 ロッカー新規登録')
    
    available_lockers_tab2 = df_lockers[df_lockers['Student ID'].isnull()]
    available_list_tab2 = available_lockers_tab2['Locker No.'].tolist()

    if not available_list_tab2:
        st.info('現在、登録できる空きロッカーがありません。')
    else:
        locker_no_reg_tab2 = st.selectbox('空いているロッカーを選択してください:', available_list_tab2, key='reg_locker_select_tab2')
        student_id_reg_tab2 = st.text_input('学籍番号 (例: 2403036)', key='reg_sid_tab2')
        name_reg_tab2 = st.text_input('氏名 (例: 埼玉太郎)', key='reg_name_tab2')
        
        if st.button('この内容で登録する', key='reg_button_tab2'):
            #
            # ★★★ ここがエラーになった行です (117行目) ★★★
            #
            if not student_id_reg_tab2 or not name_reg_tab2:
                st.error('学籍番号と氏名の両方を入力してください。')
            else:
                df_lockers.loc[df_lockers['Locker No.'] == locker_no_reg_tab2, ['Student ID', 'Name']] = [student_id_reg_tab2, name_reg_tab2]
                st.session_state.df = df_lockers 
                st.success(f"【登録完了】ロッカー '{locker_no_reg_tab2}' に '{name_reg_tab2}' さんを登録しました。")
                st.rerun()

    st.divider()

    st.subheader('🗑️ 使用者の削除 (プルダウン)')
    
    used_lockers = df_lockers.dropna(subset=['Student ID'])
    used_locker_list = used_lockers['Locker No.'].tolist()
    
    if not used_locker_list:
        st.info('現在、使用中のロッカーはありません。')
    else:
        locker_no_del = st.selectbox('削除するロッカーを選択してください:', used_locker_list, key='del_locker_select')
        
        if st.button('このロッカーの使用者を削除する', type="primary", key='del_button_pulldown'):
            df_lockers.loc[df_lockers['Locker No.'] == locker_no_del, ['Student ID', 'Name']] = [np.nan, np.nan]
            st.session_state.df = df_lockers 
            st.success(f"【削除完了】ロッカー '{locker_no_del}' の使用者情報を削除しました。")
            st.rerun()
            
    st.divider() 

    st.subheader('🗂️ 全ロッカー一覧 (削除ボタン付き)')

    col_header = st.columns([1, 2, 2, 1]) 
    col_header[0].markdown('**Locker No.**')
    col_header[1].markdown('**Student ID**')
    col_header[2].markdown('**Name**')
    col_header[3].markdown('**操作**')
    st.divider()

    for index in st.session_state.df.index:
        row = st.session_state.df.loc[index]
        
        cols = st.columns([1, 2, 2, 1])
        
        cols[0].text(row['Locker No.'])
        cols[1].text(row.fillna('--- 空き ---')['Student ID'])
        cols[2].text(row.fillna('--- 空き ---')['Name'])
        
        if not pd.isnull(row['Student ID']):
            if cols[3].button('削除', key=f"del_{index}", type="primary"):
                st.session_state.df.loc[index, ['Student ID', 'Name']] = [np.nan, np.nan]
                st.success(f"ロッカー '{row['Locker No.']}' の使用者を削除しました。")
                st.rerun()
        else:
            cols[3].text("")


# --- 5. メインロジック（★★ ここからが変更点 ★★） ---

is_admin_logged_in = False

# --- 5a. タイトルと右上のログイン/ログアウトエリアを作成 ---
col1, col2 = st.columns([0.75, 0.25]) # 75% : 25% に分割

with col1:
    st.title('ロッカー管理システム')

with col2:
    st.write("") # ボタンを縦方向に中央揃えするための空白
    
    if st.session_state["authentication_status"]:
        # --- ログイン済み（管理者）の場合 ---
        current_user_email = st.session_state["name"]
        st.write(f'Welcome *{current_user_email}*')
        authenticator.logout('Logout', 'main') # ログアウトボタン
        
        if current_user_email == ADMIN_EMAIL:
            is_admin_logged_in = True
    
    else:
        # --- 未ログインの場合 ---
        if st.button("🔒 管理者ログイン", key="show_login_btn"):
            st.session_state.show_login_modal = True # ボタンが押されたらモーダル表示のフラグを立てる
        st.caption("管理者はこちら") # ボタンの下に説明文


# --- 5b. ログインモーダル（ポップアップ）の処理 ---
if st.session_state.get("show_login_modal", False):
    
    # モーダルウィンドウを作成
    modal = st.modal("管理者ログイン", key="login_modal")
    with modal:
        # モーダルの中にログインフォームを表示
        authenticator.login(location='main')
    
    # ログイン試行後（成功でも失敗でも）はモーダルを非表示にする
    if st.session_state["authentication_status"] is not None:
         st.session_state.show_login_modal = False


# --- 6. タブの定義とコンテンツの実行 ---

if is_admin_logged_in:
    # 管理者がログインしている場合、2つのタブを定義
    tab1, tab2 = st.tabs(["🗂️ 閲覧・登録用", "🔒 管理者用"])
else:
    # 未ログイン/一般ユーザーの場合、1つのタブだけを定義
    tab1, = st.tabs(["🗂️ 閲覧・登録用"])
    
    # ログイン失敗時のエラーメッセージだけ、タブの外（メイン画面）に表示
    if st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    # (初期状態(None)のメッセージはボタンの下に移動)


# 常に「閲覧・登録用」タブの内容を表示する
with tab1:
    display_viewer_tab()

# 管理者ログイン時のみ「管理者用」タブの内容を表示する
if is_admin_logged_in:
    with tab2:
        display_admin_tab()
