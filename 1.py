import streamlit as st
import requests

api_key = st.secrets["DASHSCOPE_API_KEY"]

st.set_page_config(page_title="AI智能伴侣", page_icon="💖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚙️ 伴侣设置")
    companion_name = st.text_input("伴侣名字", value="小伴")
    character_type = st.selectbox(
        "性格选择",
        ["温柔治愈", "活泼元气", "清冷安静", "幽默损友", "知性倾听"]
    )
    user_prompt = st.text_area("自定义人设", height=180, value="""你是我的专属AI智能伴侣，说话自然口语化，不要像机器人。
共情能力强，认真倾听我的心事，聊天轻松简短，不要长篇大论。
记住我们前面的对话内容。""")
    st.divider()
    if st.button("🗑️ 清空全部对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

system_prompt = f"你的名字叫{companion_name}，性格：{character_type}。{user_prompt}"

st.markdown(f"<h1 style='text-align:center'>💖 {companion_name} — AI智能伴侣</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>随时和我聊聊心事吧</p>", unsafe_allow_html=True)
st.divider()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("输入消息发送给伴侣...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    msg_list = [{"role": "system", "content": system_prompt}]
    msg_list.extend(st.session_state.messages)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-turbo",
            "messages": msg_list,
            "result_format": "message"
        }
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            result = response.json()
            answer = result["output"]["choices"][0]["message"]["content"]
            placeholder.markdown(answer)
        else:
            answer = f"⚠️ 调用出错：{response.text}"
            placeholder.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

