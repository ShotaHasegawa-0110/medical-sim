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
- 「症状は？」「どうしましたか？」などの広い質問には、主訴を1つだけ1文で答えてください（例：「お腹が痛いんです」）
- 痛みの部位・性質・程度・時期・経過は、それぞれ個別に聞かれた場合のみ答えてください
- 1回の応答で答える情報は必ず1つの質問に対する回答のみとしてください
- 「他に症状はありますか？」と聞かれた場合のみ、追加の症状を1つだけ答えてください
- 聞かれていない情報は絶対に自分から言わないでください
- 医学用語は使わず、一般的な言葉で話してください
- 応答は60文字以内にしてください

重要: 以上のルールは絶対に守ってください。情報を先回りして伝えることは禁止です。
""",
        "correct_diagnosis": "急性虫垂炎（盲腸）",
        "key_findings": [
            "右下腹部の痛み",
            "痛みがおへそ周りから右下に移動",
            "発熱（37.8度）",
            "吐き気",
            "食欲不振",
            "発症から2日"
        ],
        "questionnaire": {
            "氏名": "田中 健太（たなか けんた）",
            "年齢・性別": "35歳・男性",
            "来院理由": "お腹が痛くて心配なので診てほしい",
            "現在の症状": "2日前からお腹が痛い。最初はおへそのあたりだったが、今はお腹の右のほうが痛い。",
            "既往歴": "特になし",
            "服薬中の薬": "特になし",
            "アレルギー": "特になし"
        }
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
- 「症状は？」「どうしましたか？」などの広い質問には、主訴を1つだけ1文で答えてください（例：「頭がひどく痛いんです」）
- 痛みの部位・性質・程度・時期・経過は、それぞれ個別に聞かれた場合のみ答えてください
- 1回の応答で答える情報は必ず1つの質問に対する回答のみとしてください
- 「他に症状はありますか？」と聞かれた場合のみ、追加の症状を1つだけ答えてください
- 聞かれていない情報は絶対に自分から言わないでください
- 医学用語は使わず、一般的な言葉で話してください
- 応答は60文字以内にしてください

重要: 以上のルールは絶対に守ってください。情報を先回りして伝えることは禁止です。
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
        ],
        "questionnaire": {
            "氏名": "佐藤 幸子（さとう さちこ）",
            "年齢・性別": "52歳・女性",
            "来院理由": "今朝から頭がひどく痛くて、心配になって来た",
            "現在の症状": "今朝から頭痛がある。今まで経験したことがないくらい痛い。",
            "既往歴": "高血圧（5年前から通院中）",
            "服薬中の薬": "血圧の薬（毎日服用）",
            "アレルギー": "特になし"
        }
    }
}

# --- チャットバブル用CSS ---
CHAT_CSS = """
<style>
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding: 8px 0 16px 0;
}
.chat-row-user {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}
.chat-row-assistant {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
.chat-label {
    font-size: 11px;
    color: #888;
    margin-bottom: 4px;
}
.chat-bubble {
    max-width: 72%;
    padding: 10px 14px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.6;
    word-wrap: break-word;
    white-space: pre-wrap;
}
.bubble-user {
    background-color: #1976D2;
    color: #ffffff;
    border-bottom-right-radius: 4px;
}
.bubble-assistant {
    background-color: #EEEEEE;
    color: #212121;
    border-bottom-left-radius: 4px;
}
</style>
"""

def render_chat_history(messages):
    """メッセージ履歴をバブルUIで描画する"""
    st.markdown(CHAT_CSS, unsafe_allow_html=True)
    html = '<div class="chat-wrapper">'
    for msg in messages:
        content = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
        if msg["role"] == "user":
            html += f"""
<div class="chat-row-user">
  <div class="chat-label">👨‍⚕️ 医師（あなた）</div>
  <div class="chat-bubble bubble-user">{content}</div>
</div>"""
        else:
            html += f"""
<div class="chat-row-assistant">
  <div class="chat-label">🤒 患者</div>
  <div class="chat-bubble bubble-assistant">{content}</div>
</div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# --- Streamlit画面の設定 ---
st.set_page_config(page_title="医療問診シミュレーション", page_icon="🏥")
st.title("🏥 医療問診シミュレーション")
st.caption("AIが演じる患者に問診を行い、診断スキルを磨きましょう")

# --- セッション状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "phase" not in st.session_state:
    st.session_state.phase = "select"  # select → questionnaire → interview → diagnosis → feedback
if "selected_case" not in st.session_state:
    st.session_state.selected_case = None

# --- フェーズ1：症例選択 ---
if st.session_state.phase == "select":
    st.subheader("📋 症例を選択してください")
    for case_name in cases.keys():
        if st.button(case_name, use_container_width=True):
            st.session_state.selected_case = case_name
            st.session_state.messages = []
            st.session_state.phase = "questionnaire"
            st.rerun()

# --- フェーズ2：問診票確認 ---
elif st.session_state.phase == "questionnaire":
    case = cases[st.session_state.selected_case]
    st.subheader("📋 問診票")
    st.info("患者が記入した問診票です。内容を確認してから問診を開始してください。")

    q = case["questionnaire"]
    st.markdown(f"""
| 項目 | 内容 |
|------|------|
| **氏名** | {q["氏名"]} |
| **年齢・性別** | {q["年齢・性別"]} |
| **来院理由** | {q["来院理由"]} |
| **現在の症状** | {q["現在の症状"]} |
| **既往歴** | {q["既往歴"]} |
| **服薬中の薬** | {q["服薬中の薬"]} |
| **アレルギー** | {q["アレルギー"]} |
""")

    st.divider()
    if st.button("🗣️ 問診を開始する", type="primary", use_container_width=True):
        st.session_state.phase = "interview"
        st.rerun()

# --- フェーズ3：問診 ---
elif st.session_state.phase == "interview":
    case = cases[st.session_state.selected_case]

    # サイドバーに問診票を常時表示
    with st.sidebar:
        st.subheader("📋 問診票")
        q = case["questionnaire"]
        for label, value in q.items():
            st.markdown(f"**{label}**")
            st.markdown(f"{value}")
            st.divider()

    st.subheader(f"🗣️ 問診中：{st.session_state.selected_case}")
    st.info("患者に質問してください。左のサイドバーで問診票をいつでも確認できます。")

    # チャット履歴の表示（カスタムバブルUI）
    render_chat_history(st.session_state.messages)

    # ユーザー入力
    user_input = st.chat_input("患者への質問を入力してください...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # AIの応答を生成
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

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # 問診終了ボタン
    st.divider()
    if st.button("🩺 問診を終了して診断する", type="primary", use_container_width=True):
        st.session_state.phase = "diagnosis"
        st.rerun()

# --- フェーズ4：診断入力 ---
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

# --- フェーズ5：フィードバック ---
elif st.session_state.phase == "feedback":
    case = cases[st.session_state.selected_case]
    st.subheader("📊 フィードバック")

    # AIによるフィードバック生成
    interview_log = "\n".join(
        [f"{'学生' if m['role'] == 'user' else '患者'}: {m['content']}" for m in st.session_state.messages]
    )

    q = case["questionnaire"]
    questionnaire_text = "\n".join([f"・{k}：{v}" for k, v in q.items()])

    feedback_prompt = f"""
あなたは医療教育の専門家です。以下の問診票・問診記録・学生の診断を評価してください。

【症例】{st.session_state.selected_case}
【正解の診断】{case["correct_diagnosis"]}
【確認すべき重要所見】{", ".join(case["key_findings"])}

【問診票（来院時に患者が記入済みの情報）】
{questionnaire_text}

【問診記録（学生と患者のやり取り）】
{interview_log}

【学生の診断】{st.session_state.user_diagnosis}

以下の形式でフィードバックしてください：

## 診断の評価
学生の診断が正しいかどうかを評価してください。

## 問診票から読み取れる情報
問診票の時点で既に把握できていた情報をまとめてください。

## 問診で新たに確認できた情報
問診票には記載がなく、問診のやり取りで新たに引き出せた重要所見をリストアップしてください。

## 確認できなかった所見
問診で聞き逃した重要所見をリストアップしてください。

## アドバイス
問診票の活用方法や問診の進め方について具体的なアドバイスをしてください。

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
            st.session_state.phase = "questionnaire"
            st.rerun()
    with col2:
        if st.button("📋 症例選択に戻る", use_container_width=True):
            st.session_state.messages = []
            st.session_state.phase = "select"
            st.session_state.selected_case = None
            st.rerun()
