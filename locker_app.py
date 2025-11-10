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
            "name": admin_user, 
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

st.title('ロッカー管理システム')

# 3. 管理者メールアドレスの設定
ADMIN_EMAIL = admin_user

# --- 4. タブのコンテンツ関数定義 ---

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
                #
                # ★★★ 修正点 1 (st.success -> st.toast) ★★★
                #
                st.toast(f"【登録完了】ロッカー '{locker_no_reg_tab1}' に '{name_reg_tab1}' さんを登録しました。")
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
            if not student_id_reg_tab2 or not name_reg_tab2:
                st.error('学籍番号と氏名の両方を入力してください。')
            else:
                df_lockers.loc[df_lockers['Locker No.'] == locker_no_reg_tab2, ['Student ID', 'Name']] = [student_id_reg_tab2, name_reg_tab2]
                st.session_state.df = df_lockers 
                #
                # ★★★ 修正点 2 (st.success -> st.toast) ★★★
                #
                st.toast(f"【登録完了】ロッカー '{locker_no_reg_tab2}' に '{name_reg_tab2}' さんを登録しました。")
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
            #
            # ★★★ 修正点 3 (st.success -> st.toast) ★★★
            #
            st.toast(f"【削除完了】ロッカー '{locker_no_del}' の使用者情報を削除しました。")
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
                #
                # ★★★ 修正点 4 (st.success -> st.toast) ★★★
                #
                st.toast(f"ロッカー '{row['Locker No.']}' の使用者を削除しました。")
                st.rerun()
        else:
            cols[3].text("")


# --- 5. メインロジック ---

# 5a. タブを先に定義する
tab1, tab2 = st.tabs(["🗂️ 閲覧・登録用", "🔒 管理者用"])

# 5b. 閲覧・登録用タブ（認証不要）
with tab1:
    display_viewer_tab()

# 5c. 管理者用タブ（認証が必要）
with tab2:
    # ログインフォームをタブの中に表示
    authenticator.login(location='main')

    if st.session_state["authentication_status"]:
        # ログイン成功
        current_user_email = st.session_state["name"] 
        
        if current_user_email == ADMIN_EMAIL: 
            # ★ 管理者の場合 ★
            st.write(f'Welcome *{current_user_email}* (Admin)')
            authenticator.logout('Logout', 'main')
            
            # 管理者用コンテンツを表示
            display_admin_tab()
        else:
            # ★ 一般ユーザーがログインした場合 ★
            st.warning('あなたは管理者として登録されていません。')
            authenticator.logout('Logout', 'main')
            
    elif st.session_state["authentication_status"] is False:
        # ログイン失敗
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        # 初期状態
        st.info('管理者機能にアクセスするには、UsernameとPasswordでログインしてください。')
