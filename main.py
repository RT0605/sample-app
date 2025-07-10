"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
from dotenv import load_dotenv
import logging
import streamlit as st
import utils
from initialize import initialize
import components as cn
import constants as ct

############################################################
# 設定関連
############################################################
st.set_page_config(
    page_title=ct.APP_NAME,
    layout="wide"  # ←★★★画面をワイドモードに設定
)

logger = logging.getLogger(ct.LOGGER_NAME)

############################################################
# 初期化処理
############################################################
try:
    initialize()
except Exception as e:
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)

############################################################
# サイドバーにモード選択ラジオボタンを表示
############################################################
with st.sidebar:
    st.markdown("## 利用目的")
    st.session_state.mode = st.radio(
        label="",
        options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
        label_visibility="collapsed"
    )

    # サイドバー内の補足説明（修正後の画面に合わせる）
    st.markdown(f"### 【「{ct.ANSWER_MODE_1}」を選択した場合】")
    st.info("入力内容と関連性が高い社内文書のありかを検索できます。")
    st.markdown("**【入力例】**\n\n社員の育成方針に関するMTGの議事録")

    st.markdown(f"### 【「{ct.ANSWER_MODE_2}」を選択した場合】")
    st.info("質問・要望に対して、社内文書の情報をもとに回答を得られます。")
    st.markdown("**【入力例】**\n\n人事部に所属している従業員情報を一覧化して")

############################################################
# メイン画面の表示
############################################################
# 中央寄せにするための空のカラムを左右に設置（レイアウト調整）
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    cn.display_app_title()  # アプリのタイトル表示
    cn.display_initial_ai_message()  # AIメッセージの初期表示

    # 注意文を黄色で表示するために「st.warning()」を追加
    st.warning("具体的に入力したほうが期待通りの回答を得やすいです。")

    # 会話ログ表示
    try:
        cn.display_conversation_log()
    except Exception as e:
        logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
        st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
        st.stop()

    # チャット入力欄の表示
    chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)

    # チャット送信時の処理
    if chat_message:
        logger.info({"message": chat_message, "application_mode": st.session_state.mode})
        with st.chat_message("user"):
            st.markdown(chat_message)

        res_box = st.empty()
        with st.spinner(ct.SPINNER_TEXT):
            try:
                llm_response = utils.get_llm_response(chat_message)
            except Exception as e:
                logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
                st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
                st.stop()

        with st.chat_message("assistant"):
            try:
                if st.session_state.mode == ct.ANSWER_MODE_1:
                    content = cn.display_search_llm_response(llm_response)
                elif st.session_state.mode == ct.ANSWER_MODE_2:
                    content = cn.display_contact_llm_response(llm_response)
                logger.info({"message": content, "application_mode": st.session_state.mode})
            except Exception as e:
                logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
                st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
                st.stop()

        st.session_state.messages.append({"role": "user", "content": chat_message})
        st.session_state.messages.append({"role": "assistant", "content": content})
