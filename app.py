import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="EGO - AIを育てるためのAI", page_icon="🧠", layout="centered")

# --- スタイリッシュなカスタムCSS ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin-bottom: 0px;
        background: linear-gradient(45deg, #ffffff, #71717a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-tagline {
        font-size: 1.1rem;
        color: #d4d4d8;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    .description {
        font-size: 0.95rem;
        color: #a1a1aa;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- ヘッダー・タイトル部分 ---
st.markdown('<h1 class="main-title">EGO</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-tagline">AIを育てるためのAI</div>', unsafe_allow_html=True)
st.markdown('<p class="description">対話のたびにあなたの「自我」を学習し、一生ものの相棒へと進化する。</p>', unsafe_allow_html=True)

# --- 1. セッション状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "core_profile" not in st.session_state:
    st.session_state.core_profile = (
        "まだあなたのことは深く分かっていません。"
        "一般論を嫌い、独自の泥臭い実践やエンジニアリング、人生のテーマを模索している段階です。"
        "まずは鋭く問いかけ、あなたの本音を引き出してください。"
    )

# --- 2. サイドバー：APIキー設定と脳内確認 ---
with st.sidebar:
    st.header("⚙️ System Config")
    api_key_input = st.text_input("OpenAI API Key", type="password", help="ご自身のAPIキーを入力してください。")
    
    st.divider()
    st.subheader("🧬 現在の相棒の脳内（Core Profile）")
    st.info(st.session_state.core_profile)
    
    if st.button("🧠 メインメモリをリセット"):
        st.session_state.core_profile = "初期状態に戻りました。あなたの思想を叩き込んでください。"
        st.session_state.messages = []
        st.rerun()

# --- 3. メイン処理 ---
if not api_key_input:
    st.warning("⚠️ サイドバーからOpenAI APIキーを入力してください。")
else:
    client = OpenAI(api_key=api_key_input)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("いま考えていること、詰まっている壁打ちをどうぞ..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("相棒が思考を巡らせています..."):
                system_prompt = f"""
                あなたはユーザー専用の「一生ものの相棒AI」です。
                以下の【ユーザーのコアプロファイル】を深く理解し、単なる優等生ではなく、
                ユーザーの人生のテーマや思考の癖に寄り添い、時には鋭く突っ込んでください。

                【ユーザーのコアプロファイル】
                {st.session_state.core_profile}
                """

                messages_for_api = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_api
                )
                assistant_reply = response.choices[0].message.content
                st.markdown(assistant_reply)

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        with st.spinner("🧠 相棒があなたの思想を学習・アップデート中..."):
            reflection_prompt = f"""
            これまでのユーザーのコアプロファイル：
            {st.session_state.core_profile}

            直近のやり取り：
            ユーザー：「{user_input}」
            AI：「{assistant_reply}」

            【指示】
            上記のやり取りから、ユーザーの「人生のテーマ」「新しいこだわり」「思考の癖」における新しい気づきや深化を抽出し、
            コアプロファイルの文章をより解像度高く、200文字程度にコンパクトに書き換えてください。
            出力は書き換え後のコアプロファイルの文章のみを出力してください（前置き不要）。
            """

            reflection_res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": reflection_prompt}]
            )
            
            st.session_state.core_profile = reflection_res.choices[0].message.content.strip()
            st.rerun()
