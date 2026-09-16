import streamlit as st
import requests
import json
import os

api_key = st.secrets["DASHSCOPE_API_KEY"]
HISTORY_DIR = "chat_sessions"
os.makedirs(HISTORY_DIR, exist_ok=True)

# 获取所有会话文件
def get_session_list():
    files = os.listdir(HISTORY_DIR)
    return [f[:-5] for f in files if f.endswith(".json")]

# 加载指定会话
def load_session(name):
    path = os.path.join(HISTORY_DIR, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 保存指定会话
def save_session(name, data):
    path = os.path.join(HISTORY_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="AI智能伴侣", page_icon="💖", layout="wide")

# 侧边栏会话管理
with st.sidebar:
    st.title("💬 会话管理")
    session_list = get_session_list()
    if "current_session" not in st.session_state:
        if session_list:
            st.session_state.current_session = session_list[0]
        else:
            st.session_state.current_session = "会话1"
            save_session("会话1", [])

    # 新建会话
    new_name = st.text_input("新建会话名称")
    if st.button("➕ 创建会话") and new_name:
        if new_name not in session_list:
            save_session(new_name, [])
        st.session_state.current_session = new_name
        st.rerun()

    # 切换会话
    selected_session = st.selectbox("选择会话", get_session_list(), index=get_session_list().index(st.session_state.current_session))
    if selected_session != st.session_state.current_session:
        st.session_state.current_session = selected_session
        st.rerun()

    # 删除当前会话
    if st.button("🗑️ 删除当前会话"):
        os.remove(os.path.join(HISTORY_DIR, f"{st.session_state.current_session}.json"))
        st.rerun()

    st.divider()
    st.title("⚙️ 伴侣设置")
    companion_name = st.text_input("伴侣名字", value="小伴")
    character_type = st.selectbox(
        "性格选择",
        ["温柔治愈", "活泼元气", "清冷安静", "幽默损友", "知性倾听"]
    )
    user_prompt = st.text_area("自定义人设", height=180, value="""你是我的专属AI智能伴侣，说话自然口语化，不要像机器人。
共情能力强，认真倾听我的心事，聊天轻松简短，不要长篇大论。
记住我们前面的对话内容。""")

system_prompt = f"你的名字叫{companion_name}，性格：{character_type}。{user_prompt}"

# 加载当前选中会话的历史
messages = load_session(st.session_state.current_session)

st.markdown(f"<h1 style='text-align:center'>💖 {companion_name} — AI智能伴侣</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center'>当前会话：{st.session_state.current_session}</p>", unsafe_allow_html=True)
st.divider()

# 渲染当前会话历史
for chat in messages:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

user_input = st.chat_input("输入消息发送给伴侣...")
if user_input:
    messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    msg_list = [{"role": "system", "content": system_prompt}]
    msg_list.extend(messages)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-turbo",
            "input": {
                "messages": msg_list
            },
            "parameters": {
                "result_format": "message"
            }
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
    messages.append({"role": "assistant", "content": answer})
    save_session(st.session_state.current_session, messages)



