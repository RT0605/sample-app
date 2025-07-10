"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import streamlit as st
import utils
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")

def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant"):
        st.markdown("こんにちは。私は社内文書の情報をもとに回答する生成AIチャットボットです。サイドバーで利用目的を選択し、画面下部のチャット欄からメッセージを送信してください。")

def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):

            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                if message["content"]["mode"] == ct.ANSWER_MODE_1:
                    if "no_file_path_flg" not in message["content"]:
                        st.markdown(message["content"]["main_message"])

                        main_icon = utils.get_source_icon(message['content']['main_file_path'])
                        main_display_text = message['content']['main_file_path']
                        if main_display_text.endswith(".pdf") and "main_page_number" in message["content"]:
                            main_display_text += f"（ページNo.{message['content']['main_page_number']}）"
                        st.success(main_display_text, icon=main_icon)

                        if "sub_message" in message["content"]:
                            st.markdown(message["content"]["sub_message"])
                            for sub_choice in message["content"]["sub_choices"]:
                                sub_icon = utils.get_source_icon(sub_choice['source'])
                                sub_display_text = sub_choice['source']
                                if sub_display_text.endswith(".pdf") and "page_number" in sub_choice:
                                    sub_display_text += f"（ページNo.{sub_choice['page_number']}）"
                                st.info(sub_display_text, icon=sub_icon)
                    else:
                        st.markdown(message["content"]["answer"])

                else:
                    st.markdown(message["content"]["answer"])

                    if "file_info_list" in message["content"]:
                        st.divider()
                        st.markdown(f"##### {message['content']['message']}")
                        for file_info in message["content"]["file_info_list"]:
                            icon = utils.get_source_icon(file_info["file_path"])
                            display_text = file_info["file_path"]
                            if display_text.endswith(".pdf") and "page_number" in file_info:
                                display_text += f"（ページNo.{file_info['page_number']}）"
                            st.info(display_text, icon=icon)

def display_search_llm_response(llm_response):
    """
    「社内文書検索」モードにおけるLLMレスポンスを表示
    """
    if llm_response["context"] and llm_response["answer"] != ct.NO_DOC_MATCH_ANSWER:
        main_file_path = llm_response["context"][0].metadata["source"]
        main_message = "入力内容に関する情報は、以下のファイルに含まれている可能性があります。"
        st.markdown(main_message)

        main_icon = utils.get_source_icon(main_file_path)
        main_display_text = main_file_path
        content = {
            "mode": ct.ANSWER_MODE_1,
            "main_message": main_message,
            "main_file_path": main_file_path,
        }

        if "page" in llm_response["context"][0].metadata:
            main_page_number = llm_response["context"][0].metadata["page"]
            content["main_page_number"] = main_page_number
            if main_display_text.endswith(".pdf"):
                main_display_text += f"（ページNo.{main_page_number}）"

        st.success(main_display_text, icon=main_icon)

        sub_choices = []
        duplicate_check_list = []

        for document in llm_response["context"][1:]:
            sub_file_path = document.metadata["source"]
            if sub_file_path == main_file_path or sub_file_path in duplicate_check_list:
                continue
            duplicate_check_list.append(sub_file_path)
            sub_choice = {"source": sub_file_path}
            if "page" in document.metadata:
                sub_choice["page_number"] = document.metadata["page"]
            sub_choices.append(sub_choice)

        if sub_choices:
            sub_message = "その他、ファイルありかの候補を提示します。"
            st.markdown(sub_message)

            for sub_choice in sub_choices:
                sub_icon = utils.get_source_icon(sub_choice['source'])
                sub_display_text = sub_choice['source']
                if sub_display_text.endswith(".pdf") and "page_number" in sub_choice:
                    sub_display_text += f"（ページNo.{sub_choice['page_number']}）"
                st.info(sub_display_text, icon=sub_icon)

            content["sub_message"] = sub_message
            content["sub_choices"] = sub_choices

    else:
        st.markdown(ct.NO_DOC_MATCH_MESSAGE)
        content = {
            "mode": ct.ANSWER_MODE_1,
            "answer": ct.NO_DOC_MATCH_MESSAGE,
            "no_file_path_flg": True
        }

    return content

def display_contact_llm_response(llm_response):
    """
    「社内問い合わせ」モードにおけるLLMレスポンスを表示
    """
    st.markdown(llm_response["answer"])

    content = {
        "mode": ct.ANSWER_MODE_2,
        "answer": llm_response["answer"]
    }

    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        st.divider()
        message = "情報源"
        st.markdown(f"##### {message}")

        file_info_list = []
        duplicate_check_list = []

        for document in llm_response["context"]:
            file_path = document.metadata["source"]
            if file_path in duplicate_check_list:
                continue
            file_info = {"file_path": file_path}
            if "page" in document.metadata:
                file_info["page_number"] = document.metadata["page"]

            display_text = file_path
            if display_text.endswith(".pdf") and "page_number" in file_info:
                display_text += f"（ページNo.{file_info['page_number']}）"

            icon = utils.get_source_icon(file_path)
            st.info(display_text, icon=icon)

            file_info_list.append(file_info)
            duplicate_check_list.append(file_path)

        content["message"] = message
        content["file_info_list"] = file_info_list

    return content
