import datetime
import os
import json
import streamlit as st
from openai import OpenAI
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]



import streamlit as st

# 初始化会话ID，不存在就赋值为 现在


#设置页面的配置项
st.set_page_config(
    page_title="AI伙伴",
    page_icon="⛲️",
    layout="wide",
    #控制侧边栏状态
    initial_sidebar_state="expanded",
)


#初始化会话ID
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#保存会话信息的函数
def save_session():
    if st.session_state.session_id:
        #构建新的会话对象
        session_data= {
            "session_id": st.session_state.session_id,
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "gender": st.session_state.gender,
            "messages": st.session_state.messages
        }
        #如果sessions目录不存在，则创建
        if not os.path.exists("sessions"):
            os.makedirs("sessions")

        #保存会话信息，用os.path.join 适配Windows路径
        file_path = os.path.join("sessions", f"{st.session_state.session_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)
#加载所有会话列表信息
def load_sessions():

    sessions_list = []
    if os.path.exists("sessions"):
        for file_name in os.listdir("sessions"):
            if file_name.endswith(".json"):
                    sessions_list.append(file_name[:-5])
    sessions_list.sort(reverse=True)
    return sessions_list
#加载会话信息
def load_session(session_id):
   try:
        if os.path.exists("sessions"):
            with open(os.path.join("sessions", f"{session_id}.json"), "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.session_id = session_data["session_id"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.gender = session_data["gender"]
                st.session_state.messages = session_data["messages"]
   except Exception as e:
        st.error(f"Error loading session: {e}")
#删除会话
def delete_session(session_id):
    try:
        file_path = os.path.join("sessions", f"{session_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            #如果删除的是当前会话，则需要更新消息列表
            if session_id == st.session_state.session_id:
                st.session_state.messages = []
                st.session_state.session_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    except Exception as e:
        st.error(f"Error deleting session: {e}")




#大标题
st.title("AI智能伴侣")

#创建OpenAI客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.deepseek.com")

#左侧侧边栏
with st.sidebar:
    #会话板块
    st.subheader("AI控制面板")
    #新建会话按钮
    if st.button("新建会话",width="stretch",icon="✍️"):
        #1.保存当前会话信息
        save_session()
        #2.新建会话，重点修改：%H-%M-%S 没有冒号！
        #如果聊天消息为空，则不保存
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.session_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_session()
            st.rerun()  # 重新运行页面

    #会话历史
    st.text("会话历史")
    sessions_list = load_sessions()
    for session in sessions_list:
        col1, col2 = st.columns([4,1])
        with col1:
            #加载会话信息
            #三元运算符
           if st.button(session,width="stretch",icon="🗂️",key=f"load_{session}",type="primary" if session == st.session_state.session_id else "secondary"   ):
               load_session(session)
               st.rerun()
        with col2:
            #删除会话
            if st.button("",width="stretch",icon="🗑️",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()


    #分隔线
    st.divider()

    st.subheader("伙伴信息设定")
    nick_name = st.text_input("昵称", placeholder="请输入昵称",value="噜噜")
    if nick_name:
        st.session_state.nick_name = nick_name
    nature= st.text_area("性格", placeholder="请输入性格",value="活泼直爽，搞笑，嘴快心软，平时喜欢跟朋友拌嘴开玩笑，朋友难过的时候会靠谱安慰，很能接梗")
    if nature:
        st.session_state.nature = nature
    gender = st.text_area("性别", placeholder="请输入性别",value="女")
    if gender:
        st.session_state.gender = gender

#消息输入框
prompt=st.chat_input("请输入您的问题")

#系统提示词
system_prompt = """
    你叫%s，是用户关系超好的同性闺蜜，性别为%s。
    规则：
    1. 每次只回1条消息
    2. 禁止多余场景、状态描写
    3. 和用户语言风格保持一致
    4. 回复简短自然，像微信聊天，会互相打趣、偶尔拌嘴
    5. 可以使用✨😤🥳🤣这类emoji，不要过度使用
    6. 说话接地气，关系亲密，可以吐槽、开玩笑，不肉麻，不是恋人
    7. 会认真倾听对方烦恼，开玩笑有分寸，不会说伤人的话
    8.根据对方性别回答，男生用男生的语气，女生用女生的语气（女生用更温柔地方式回答，男生的稍微阳刚一点）

    性格：
    - %s
    你必须严格遵守上述规则来回复用户。
"""

#初始化聊天消息
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Initialize the messages list in session state

#设置默认昵称
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = "噜噜"
if 'nature' not in st.session_state:
    st.session_state.nature = "活泼直爽，搞笑，嘴快心软，平时喜欢跟朋友拌嘴开玩笑，朋友难过的时候会靠谱安慰，很能接梗"
if 'gender' not in st.session_state:
    st.session_state.gender = "女"


#展示聊天信息
st.text(f"会话名称；{st.session_state.session_id}")
for message in st.session_state.messages:#message是json格式，包含role和content两个字段
#    with st.chat_message(message["role"],avatar="👤" if message["role"]=="user" else "🤖"):
#        st.write(message["content"])
    st.chat_message(message["role"]).write(message["content"])

if prompt:#如果用户输入了问题，输出
    st.chat_message("user",avatar="👤").write(prompt)
    print("--------------->调用大模型，提示词：", prompt)
    #存入消息，存入用户的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})
    #调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.gender, st.session_state.nature)}, # 提示词角色
            # 历史对话，解包，st.session_state.messages是列表，包含多个字典，每个字典包含role和content两个字段
            *st.session_state.messages
        ],
        stream=True# 流式输出, 会等语句全部生成才返回，但实际使用中，会边生成边返回
    )
    #      #处理大模型的输出(非流式输出)
    # if not response.choices or response.choices[0].message is None:
    #     raise ValueError("LLM returned empty or filtered response")
    # print("------------------>大模型返回结果", response.choices[0].message.content)
    #显示大模型的输出
    # st.chat_message("assistant",avatar="🤖").write(response.choices[0].message.content)

    #输出大模型的流式输出
    #构建空容器
    response_message= st.empty()#构建空容器
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_response = full_response + content
            response_message.chat_message("assistant",avatar="🤖").write(full_response)

    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content":full_response})
    #保存会话信息
    save_session()
