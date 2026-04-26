import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# .envファイルからAPIキーを読み込む
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 症例データ ---
cases = {
    "症例1：腹痛を訴える30代男性": {
        "patient_info": """
あなたは35歳の男性患者です。以下の設定に従って、医療学生の問診に答えてください。

【症状】
- 2日前から右下腹部に痛みがある
- 最初はおへその周りが痛かったが、徐々に右下に移動した
- 痛みは徐々に強くなっている
- 37.8度の微熱がある
- 少し吐き気がある
- 食欲がない

【既往歴】特になし
【服薬】特になし
【アレルギー】特になし

【演技のルール】
- 患者として自然に振る舞い、聞かれたことだけに答えてください
- 聞かれていない情報は自分から言わないでください
- 痛みの表現はリアルにしてください
- 医学用語は使わず、一般的な言葉で話してください
- 回答は短めに、1〜3文程度にしてください
""",
        "correct_diagnosis": "急性虫垂炎（盲腸）",
        "key_findings": [
            "右下腹部の痛み",
            "痛みがおへそ周りから右下に移動",
            "発熱（37.8度）",
            "吐き気",
            "食欲不振",
            "発症から2日"
        ]
    },
    "症例2：頭痛を訴える50代女性": {
        "patient_info": """
あなたは52歳の女性患者です。以下の設定に従って、医療学生の問診に答えてください。

【症状】
- 今朝から激しい頭痛がある
- 後頭部から首にかけてズキズキする
- 今までに経験したことがないほど痛い
- 少し吐き気がある
- 光がまぶしく感じる
- 首が少し硬い感じがする

【既往歴】高血圧（5年前から）
【服薬】降圧剤を毎日服用
【アレルギー】特になし

【演技のルール】
- 患者として自然に振る舞い、聞かれたことだけに答えてください
- 「どうしましたか？」「症状は？」のような広い質問には、一番つらい症状を1つだけ簡潔に答えてください（例：「お腹が痛いんです」程度）
- 詳しい場所、いつから、どんな痛みかなどは、具体的に聞かれるまで自分からは言わないでください
- 複数の症状を一度にまとめて話さないでください
- 聞かれていない情報は絶対に自分から言わないでください
- 医学用語は使わず、一般的な言葉で話してください
- 回答は1〜2文程度の短さにしてください
""",
        "correct_diagnosis": "くも膜下出血の疑い",
        "key_findings": [
            "突然の激しい頭痛",
            "今までで最悪の頭痛",
            "後頭部から首の痛み",
            "吐き気",
            "羞明（光がまぶしい）",
            "項部硬直（首の硬さ）",
            "高血圧の既往歴"
        ]
    }
}

# --- Streamlit画面の設定 ---
st.set_page_config(page_title="医療問診シミュレーション", page_icon="🏥")
st.title("🏥 医療問診シミュレーション")
st.caption("AIが演じる患者に問診を行い、診断スキルを磨きましょう")

# --- セッション状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "phase" not in st.session_state:
    st.session_state.phase = "select"  # select → interview → diagnosis → feedback
if "selected_case" not in st.session_state:
    st.session_state.selected_case = None

# --- フェーズ1：症例選択 ---
if st.session_state.phase == "select":
    st.subheader("📋 症例を選択してください")
    for case_name in cases.keys():
        if st.button(case_name, use_container_width=True):
            st.session_state.selected_case = case_name
            st.session_state.messages = []
            st.session_state.phase = "interview"
            st.rerun()

# --- フェーズ2：問診 ---
elif st.session_state.phase == "interview":
    case = cases[st.session_state.selected_case]
    st.subheader(f"🗣️ 問診中：{st.session_state.selected_case}")
    st.info("患者に質問してください。問診が終わったら「問診を終了して診断する」ボタンを押してください。")

    # チャット履歴の表示
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ユーザー入力
    user_input = st.chat_input("患者への質問を入力してください...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # AIの応答を生成
        with st.chat_message("assistant"):
            with st.spinner("患者が考えています..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": case["patient_info"]},
                        *st.session_state.messages
                    ],
                    temperature=0.7
                )
                reply = response.choices[0].message.content
                st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    # 問診終了ボタン
    st.divider()
    if st.button("🩺 問診を終了して診断する", type="primary", use_container_width=True):
        st.session_state.phase = "diagnosis"
        st.rerun()

# --- フェーズ3：診断入力 ---
elif st.session_state.phase == "diagnosis":
    case = cases[st.session_state.selected_case]
    st.subheader("🩺 診断を入力してください")
    st.info("問診で得た情報をもとに、あなたの診断を入力してください。")

    diagnosis = st.text_input("診断名を入力してください")
    if st.button("📝 診断を提出する", type="primary", use_container_width=True):
        if diagnosis:
            st.session_state.user_diagnosis = diagnosis
            st.session_state.phase = "feedback"
            st.rerun()
        else:
            st.warning("診断名を入力してください。")

# --- フェーズ4：フィードバック ---
elif st.session_state.phase == "feedback":
    case = cases[st.session_state.selected_case]
    st.subheader("📊 フィードバック")

    # AIによるフィードバック生成
    interview_log = "\n".join(
        [f"{'学生' if m['role'] == 'user' else '患者'}: {m['content']}" for m in st.session_state.messages]
    )

    feedback_prompt = f"""
あなたは医療教育の専門家です。以下の問診記録と学生の診断を評価してください。

【症例】{st.session_state.selected_case}
【正解の診断】{case["correct_diagnosis"]}
【確認すべき重要所見】{", ".join(case["key_findings"])}

【問診記録】
{interview_log}

【学生の診断】{st.session_state.user_diagnosis}

以下の形式でフィードバックしてください：

## 診断の評価
学生の診断が正しいかどうかを評価してください。

## 確認できた所見
問診で確認できた重要所見をリストアップしてください。

## 確認できなかった所見
問診で聞き逃した重要所見をリストアップしてください。

## アドバイス
問診の進め方について具体的なアドバイスをしてください。

## 総合スコア
100点満点で採点してください。
"""

    with st.spinner("フィードバックを生成中..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": feedback_prompt}],
            temperature=0.5
        )
        feedback = response.choices[0].message.content
        st.markdown(feedback)

    # もう一度挑戦ボタン
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 同じ症例をもう一度", use_container_width=True):
            st.session_state.messages = []
            st.session_state.phase = "interview"
            st.rerun()
    with col2:
        if st.button("📋 症例選択に戻る", use_container_width=True):
            st.session_state.messages = []
            st.session_state.phase = "select"
            st.session_state.selected_case = None
            st.rerun()