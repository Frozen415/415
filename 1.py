import streamlit as st
import dashscope
from dashscope import Generation
from dotenv import load_dotenv
import os

# 加载密钥
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 页面基础配置
st.set_page_config(page_title="AI智能伴侣", page_icon="💖", layout="wide")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------- 侧边栏设置面板 ----------------------
with st.sidebar:
    st.title("⚙️ 伴侣设置")
    companion_name = st.text_input("伴侣名字", value="小伴")
    character_type = st.selectbox(
        "性格选择",
        ["温柔治愈", "活泼元气", "清冷安静", "幽默损友", "知性倾听"]
    )
    user_prompt = st.text_area("自定义人设（可修改）", height=180, value="""你是我的专属AI智能伴侣，说话自然口语化，不要像机器人。
共情能力强，认真倾听我的心事，聊天轻松简短，不要长篇大论。
记住我们前面的对话内容，称呼我为主人。""")
    st.divider()
    if st.button("🗑️ 清空全部对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 拼接最终系统提示词
system_prompt = f"你的名字叫{companion_name}，性格：{character_type}。{user_prompt}"

# ---------------------- 主页面UI ----------------------
st.markdown(f"<h1 style='text-align:center'>💖 {companion_name} — AI智能伴侣</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>随时和我聊聊心事吧</p>", unsafe_allow_html=True)
st.divider()

# 渲染历史对话
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入框
user_input = st.chat_input("输入消息发送给伴侣...")

if user_input:
    # 用户消息存入会话并展示
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 组装千问消息
    qwen_msg_list = [{"role": "system", "content": system_prompt}]
    qwen_msg_list.extend(st.session_state.messages)

    # 流式输出AI回复
    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_text = ""
        response = Generation.call(
            model="qwen-turbo",
            messages=qwen_msg_list,
            result_format="message",
            stream=True
        )
        for chunk in response:
            if chunk.status_code == 200:
                full_text += chunk.output.choices[0].message.content
                resp_placeholder.markdown(full_text)
            else:
                full_text = f"⚠️ 请求异常：{chunk.message}"
                resp_placeholder.markdown(full_text)
    st.session_state.messages.append({"role": "assistant", "content": full_text})
