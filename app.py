import streamlit as st
from PIL import Image, ImageDraw
import time
import random
import base64
from io import BytesIO

# --- 1. 页面配置：模拟手机竖屏 (Mobile-First CSS) ---
st.set_page_config(page_title="奶茶之战：大侠下山", layout="centered")

def apply_mobile_styles():
    st.markdown("""
    <style>
    /* 模拟手机容器：限制宽度并居中 */
    .main .block-container {
        max-width: 450px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #ffffff;
        border-left: 1px solid #ddd;
        border-right: 1px solid #ddd;
        min-height: 100vh;
    }
    
    /* 漫画气泡 */
    .comic-bubble {
        background-color: #fff;
        border: 3px solid #000;
        border-radius: 15px;
        padding: 12px;
        margin: 10px 0;
        box-shadow: 4px 4px 0px #000;
        font-family: 'Arial', sans-serif;
        line-height: 1.4;
    }
    
    /* 屏幕震动动画 (发音失败触发) */
    @keyframes shake {
      0% { transform: translate(1px, 1px) rotate(0deg); }
      20% { transform: translate(-3px, 0px) rotate(1deg); }
      40% { transform: translate(3px, 2px) rotate(-1deg); }
      60% { transform: translate(-3px, 1px) rotate(0deg); }
      80% { transform: translate(3px, -1px) rotate(1deg); }
      100% { transform: translate(1px, -2px) rotate(-1deg); }
    }
    .shake-active { animation: shake 0.5s; animation-iteration-count: 2; }
    
    /* 视频圆角 */
    video { border-radius: 15px; border: 2px solid #333; }
    </style>
    """, unsafe_allow_html=True)

apply_mobile_styles()

# --- 2. 核心辅助函数 ---

def get_video_html(video_path):
    """将视频转为自动播放的 HTML5 标签"""
    try:
        with open(video_path, 'rb') as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        return f'<video width="100%" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    except:
        return "<p style='color:red;'>视频加载失败，请检查文件名是否为 background_v.mp4</p>"

def create_hero_avatar(face_img):
    """头像圆形合成逻辑"""
    body = Image.open('user_body_kungfu.png').convert("RGBA")
    face = Image.open(face_img).convert("RGBA")
    
    # 尺寸与遮罩 (根据立绘比例，160x160 是经验值)
    h_size = (160, 160)
    face = face.resize(h_size)
    mask = Image.new('L', h_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + h_size, fill=255)
    
    combined = Image.new("RGBA", body.size)
    combined.paste(body, (0, 0))
    # 脖子坐标微调 (165, 45) 是大侠素体的参考点
    combined.paste(face, (165, 45), mask)
    return combined

# --- 3. 状态与剧本控制 ---

if 'step' not in st.session_state:
    st.session_state.step = 'upload'
    st.session_state.progress = 0
    st.session_state.shake = False

# 简化版剧本逻辑
SCRIPT = [
    {"type": "npc", "name": "小美", "text": "欢迎光临！大侠，这里禁止携带宠物，尤其是会大叫的那种。", "pinyin": "Huānyíng guānglín! Dàxiá, zhèlǐ jìnzhǐ xiédài chǒngwù..."},
    {"type": "user", "name": "大侠", "text": "这是我的朋友。", "pinyin": "Zhè shì wǒ de péngyou.", "prop": "chicken_friend.png"},
    {"type": "npc", "name": "小美", "text": "行吧... 一杯至尊龙珠奶茶，100两银子。概不赊账。", "pinyin": "Xíng ba... Yì bēi zhìzūn lóngzhū nǎichá..."},
    {"type": "user", "name": "大侠", "text": "多少钱？", "pinyin": "Duōshǎo qián?", "prop": "fake_money.png"}
]

# --- 4. 流程渲染 ---

# 步骤一：上传头像
if st.session_state.step == 'upload':
    st.title("🧋 奶茶之战")
    st.write("请上传一张正脸照，开始你的江湖漫剧之旅。")
    up_file = st.file_uploader("", type=['jpg', 'png'])
    if up_file:
        hero = create_hero_avatar(up_file)
        st.session_state.hero_img = hero
        st.image(hero, width=250, caption="你的武侠化身已就位")
        if st.button("开始演戏", use_container_width=True):
            st.session_state.step = 'play'
            st.rerun()

# 步骤二：漫剧播放
elif st.session_state.step == 'play':
    if st.session_state.progress < len(SCRIPT):
        curr = SCRIPT[st.session_state.progress]
        
        # 1. 顶部：Kling 视频背景
        st.markdown(get_video_html("background_v.mp4"), unsafe_allow_html=True)
        
        # 2. 中间：人物立绘与对话
        char_col, text_col = st.columns([1, 2])
        with char_col:
            if curr['type'] == 'npc':
                st.image("npc_waiter.png", use_column_width=True)
            else:
                st.image(st.session_state.hero_img, use_column_width=True)
        
        with text_col:
            bg_color = "#f0f2f6" if curr['type'] == 'npc' else "#e3f2fd"
            st.markdown(f"""
                <div class="comic-bubble" style="background-color: {bg_color};">
                    <strong>{curr['name']}:</strong><br>
                    <span style="font-size: 1.1rem;">{curr['text']}</span><br>
                    <small style="color: #666;">{curr['pinyin']}</small>
                </div>
            """, unsafe_allow_html=True)
            
            # 如果有道具展示
            if 'prop' in curr:
                st.image(curr['prop'], width=100)

        # 3. 底部：交互区
        st.markdown("---")
        if curr['type'] == 'npc':
            if st.button("继续对话 ➡️", use_container_width=True):
                st.session_state.progress += 1
                st.rerun()
        else:
            st.write("🎤 **请大声朗读上方台词：**")
            # 模拟录音按钮
            if st.button("完成录音并提交", type="primary", use_container_width=True):
                score = random.randint(40, 98)
                if score < 70:
                    st.error(f"⚠️ 内功不足 (得分:{score})！发音不准，请重试。")
                    # 这里可以触发震动逻辑 (CSS注入)
                    st.markdown('<div class="shake-active"></div>', unsafe_allow_html=True)
                else:
                    st.success(f"✅ 神功盖世 (得分:{score})！下一幕开启。")
                    if st.button("前往下一幕"):
                        st.session_state.progress += 1
                        st.rerun()
    else:
        st.balloons()
        st.success("🎉 江湖路远，奶茶已到手！你已完成全部对话练习。")
        if st.button("重新挑战", use_container_width=True):
            st.session_state.progress = 0
            st.rerun()