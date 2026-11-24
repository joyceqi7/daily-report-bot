import os
import smtplib
import requests
import markdown
import feedparser
import random
from bs4 import BeautifulSoup
from youtubesearchpython import VideosSearch
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime

# ================= 1. 配置读取 =================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_PASSWORD = os.environ.get("MAIL_PASS")
SENDER_EMAIL = os.environ.get("MAIL_USER")
RECEIVERS_STR = os.environ.get("MAIL_TO")
RECEIVERS = RECEIVERS_STR.split(",") if RECEIVERS_STR else []

# ================= 2. 视频/灵感墙模块 =================

def get_video_refs():
    print("Searching Video Refs...", flush=True)
    query = "FPS mobile game TikTok trend #Shorts"
    
    link_gameplay = "https://www.youtube.com/results?search_query=FPS+mobile+game+highlight+%23shorts"
    link_funny = "https://www.youtube.com/results?search_query=FPS+mobile+game+funny+moments+%23shorts"
    link_edit = "https://www.youtube.com/results?search_query=FPS+mobile+game+edit+phonk+%23shorts"
    
    try:
        videosSearch = VideosSearch(query, limit=3)
        results = videosSearch.result()['result']
        if not results: raise Exception("No results found")

        video_html = ""
        for vid in results:
            title = vid['title']
            link = vid['link']
            thumb = vid['thumbnails'][0]['url']
            # 尝试使用 wsrv.nl 代理，以防万一能加载出来
            safe_thumb = f"https://wsrv.nl/?url={thumb}&w=280&h=180&fit=cover&a=top"
            duration = vid['duration']
            
            video_html += f"""
            <a href="{link}" target="_blank" class="video-card">
                <div class="thumb-container">
                    <img src="{safe_thumb}" class="video-thumb">
                    <div class="play-overlay">
                        <span class="play-btn">▶</span>
                    </div>
                </div>
                <div class="video-info">
                    <div class="video-title">{title}</div>
                    <div class="video-meta">WATCH NOW • {duration}</div>
                </div>
            </a>
            """
        return video_html

    except Exception as e:
        print(f"Switching to Manifesto Mode ({e}).")
        
        # 即使裂图也保留这个版本，因为你觉得图标版丑
        # 尝试使用 wsrv.nl 代理 Unsplash
        img_tac = "https://wsrv.nl/?url=images.unsplash.com/photo-1616588589676-60b30c3c1681&w=400&h=250&fit=cover"
        img_fun = "https://wsrv.nl/?url=images.unsplash.com/photo-1550745165-9bc0b252726f&w=400&h=250&fit=cover"
        img_vis = "https://wsrv.nl/?url=images.unsplash.com/photo-1550751827-4bd374c3f58b&w=400&h=250&fit=cover"
        
        return f"""
        <div class="manifesto-header">VISUAL INTELLIGENCE</div>
        
        <a href="{link_gameplay}" target="_blank" class="video-card">
            <div class="thumb-container">
                <img src="{img_tac}" class="video-thumb" style="filter: grayscale(100%) contrast(1.2);">
                <div class="manifesto-badge">GAMEPLAY</div>
            </div>
            <div class="video-info">
                <div class="video-title">High-Level Plays</div>
                <div class="video-meta">TREND • SKILL</div>
            </div>
        </a>

        <a href="{link_funny}" target="_blank" class="video-card">
            <div class="thumb-container">
                <img src="{img_fun}" class="video-thumb" style="filter: hue-rotate(45deg) contrast(1.1);">
                <div class="manifesto-badge">MEME & BUG</div>
            </div>
            <div class="video-info">
                <div class="video-title">Viral Moments</div>
                <div class="video-meta">TREND • FUNNY</div>
            </div>
        </a>

        <a href="{link_edit}" target="_blank" class="video-card">
            <div class="thumb-container">
                <img src="{img_vis}" class="video-thumb" style="filter: saturate(0) brightness(1.2);">
                <div class="manifesto-badge">VISUAL ARTS</div>
            </div>
            <div class="video-info">
                <div class="video-title">Cinematic Edits</div>
                <div class="video-meta">TREND • AESTHETIC</div>
            </div>
        </a>
        """

# ================= 3. 锁热情报抓取 =================

def fetch_deep_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')
            for tag in soup(["script", "style", "nav", "footer"]): tag.extract()
            text = " ".join([p.get_text() for p in soup.find_all('p')])
            return text[:600] + "..." 
    except: return ""
    return ""

def get_reddit_top_heat():
    print("Checking Reddit Heat...", flush=True)
    subreddits = ["TikTokhelp", "marketing", "PUBGMobile", "CallOfDutyMobile", "FPSMobile"] 
    content = ""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=3"
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for post in data['data']['children']:
                    score = post['data']['score']
                    if score > 50:
                        content += f"【Reddit高赞 🔥{score}】{post['data']['title']}\n"
        except: pass
    return content

def get_google_viral_news():
    print("Checking Viral News...", flush=True)
    queries = [
        ('TikTok', '"TikTok" AND ("viral" OR "trend") when:2d'),
        ('FPS-Game', '("PUBG Mobile" OR "Free Fire" OR "CODM") AND ("update" OR "event") when:2d')
    ]
    
    content = ""
    for label, q in queries:
        try:
            url = f"https://news.google.com/rss/search?q={q.replace(' ', '%20')}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            if feed.entries:
                top_entry = feed.entries[0]
                deep_text = fetch_deep_content(top_entry.link)
                content += f"\n【News头条-{label}】{top_entry.title}\n(深度摘要: {deep_text})\n"
                for entry in feed.entries[1:3]:
                    content += f"【News速报】{entry.title}\n"
        except: pass
    return content

def ask_ai():
    full_intel = get_reddit_top_heat() + "\n" + get_google_viral_news()
    
    if len(full_intel) < 100:
        full_intel = "今日全网平淡。请分享 3 个 FPS 射击手游在 TikTok 上的通用爆款视频模板。"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    # 🔥 Prompt 核心修改：要求输出 3 个趋势，而不是 1 个
    prompt = f"""
    今天是 {datetime.now().strftime('%Y-%m-%d')}。
    你是 **CrossFire: Legends (CFL)** 的社媒情报分析师。
    
    【情报源】：
    {full_intel}
    
    --------------------------------------------------
    **😡 严重警告 (Identity Check)**：
    1. **CFL 是 FPS 射击游戏**。
    2. **禁止词汇**：禁止出现“球员”、“体能”、“橄榄球”等体育术语。
    3. 忽略体育新闻，只写游戏和社媒趋势！
    
    **写作要求**：
    1. **极简主义**：不要废话，直接给干货。
    2. **禁止表格**。
    
    **内参结构：**
    
    ## 🔥 TOP 3 VIRAL TRENDS
    * **(趋势 1)**: 深度拆解...
    * **(趋势 2)**: 深度拆解...
    * **(趋势 3)**: 深度拆解...
    
    ## ⚔️ MARKET RADAR
    * (竞品/行业动态)
    
    ## 🎬 SCRIPT LAB
    * (爆款脚本)
    * **[BGM]**: ...
    * **[VISUAL]**: ...
    """
    
    try:
        resp = requests.post(url, json={"contents":[{"parts":[{"text": prompt}]}]}, headers={'Content-Type': 'application/json'})
        if resp.status_code == 200:
            text = resp.json()['candidates'][0]['content']['parts'][0]['text']
            return text.replace("|", " ").replace("---", "") 
        else:
            return f"AI Error: {resp.text}"
    except Exception as e:
        return f"Error: {e}"

# ================= 4. 发送邮件 (V31.2 最终定稿版) =================

def send_email():
    if not GEMINI_API_KEY: return

    print("🚀 运行 V31.2 最终定稿版...")
    
    ai_content = ask_ai()
    try:
        body_html = markdown.markdown(ai_content)
    except:
        body_html = f"<pre>{ai_content}</pre>"
        
    video_gallery = get_video_refs()
    
    # 🔥🔥🔥 CSS 视觉规范：V31 深海钛金版 (保持不变) 🔥🔥🔥
    css_style = """
    <style>
        /* 1. 全局: 纯黑底，冷灰字 */
        body, .email-wrapper { margin: 0; padding: 0; background-color: #000000 !important; color: #a1a1aa !important; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; }
        
        /* 2. 容器: 增加深蓝边框，营造商务感 */
        .container { max-width: 600px; margin: 30px auto; background: #0a0a0a; border: 1px solid #1e3a5f; border-radius: 16px; overflow: hidden; box-shadow: 0 0 40px rgba(0,0,0,1); }
        
        /* 3. Header: 银色金属渐变 */
        .header { padding: 50px 30px 20px; background: #0a0a0a; border-bottom: 1px solid #1e3a5f; }
        .header h1 { margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -1px; 
            /* 银色渐变 */
            background: linear-gradient(to bottom, #ffffff 0%, #a1a1aa 100%); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            display: inline-block; 
            color: #ffffff;
        }
        .header p { margin: 10px 0 0; font-size: 10px; color: #52525b !important; text-transform: uppercase; letter-spacing: 3px; font-weight: 600; }
        
        /* 4. 内容区域 */
        .content { padding: 20px 30px 40px; }
        .content p { color: #d4d4d8 !important; font-size: 15px; margin-bottom: 15px; }
        
        /* 5. 标题 H2: 银色金属字 + 极细蓝线 */
        h2 { 
            color: #ffffff !important; 
            font-size: 24px; /* 加大 */
            text-transform: uppercase; 
            letter-spacing: 0.5px;
            margin-top: 55px; 
            margin-bottom: 25px; 
            font-weight: 800; 
            display: flex; 
            align-items: center;
            border-bottom: 1px solid #1e3a5f; /* 深蓝底线 */
            padding-bottom: 10px;
            /* 文字银色渐变 */
            background: linear-gradient(to right, #ffffff, #9ca3af);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        /* 左侧装饰块：深蓝色 */
        h2::before { 
            content: ''; 
            display: inline-block; 
            width: 4px; 
            height: 20px; 
            background: #0ea5e9; /* 天空蓝/电光蓝 */
            margin-right: 15px; 
            box-shadow: 0 0 10px #0ea5e9; /* 蓝色辉光 */
        }
        
        /* 6. 列表 LI: 极简，无背景 */
        ul { padding-left: 0; list-style: none; }
        li { 
            margin-bottom: 14px; 
            padding: 0 0 0 20px; 
            color: #e4e4e7 !important; 
            font-size: 15px;
            position: relative;
        }
        /* 子弹点：蓝色 */
        li::before {
            content: "•";
            color: #0ea5e9; 
            font-weight: bold;
            display: inline-block; 
            width: 1em;
            margin-left: -1em;
            text-shadow: 0 0 5px #0ea5e9; /* 微弱辉光 */
        }
        
        /* 7. 重点 Strong: 霓虹辉光字 (Neon Glow Experiment) */
        strong { 
            color: #e0f2fe !important; /* 极淡的冰蓝白 */
            font-weight: 600; 
            background: transparent !important; 
            padding: 0;
            /* 关键：蓝色文字光晕 */
            text-shadow: 0 0 8px rgba(14, 165, 233, 0.6); 
        }
        
        /* 8. 脚本区: 深蓝边框 */
        blockquote { margin: 30px 0; padding: 25px; background: #050505; border-radius: 8px; font-family: "SF Mono", monospace; font-size: 13px; color: #a1a1a6 !important; border: 1px solid #1e3a5f; }
        
        /* 9. 视频卡片 */
        .manifesto-header { text-align: center; font-size: 10px; color: #444; letter-spacing: 3px; margin: 50px 0 20px; text-transform: uppercase; }
        .video-card { display: flex; align-items: center; background: #0a0a0a; border: 1px solid #1e3a5f; margin-bottom: 16px; border-radius: 12px; overflow: hidden; text-decoration: none; transition: opacity 0.2s; }
        .video-card:hover { border-color: #38bdf8; }
        .thumb-container { position: relative; width: 130px; height: 85px; flex-shrink: 0; }
        .video-thumb { width: 100%; height: 100%; object-fit: cover; opacity: 0.8; }
        .manifesto-badge { position: absolute; bottom: 6px; left: 6px; background: rgba(0,20,40,0.9); color: #38bdf8; font-size: 8px; padding: 2px 6px; border-radius: 4px; font-weight: 700; border: 1px solid #1e3a5f; }
        .video-info { padding: 0 20px; display: flex; flex-direction: column; justify-content: center; }
        .video-title { font-size: 14px; font-weight: 600; color: #f4f4f5 !important; margin-bottom: 5px; }
        .video-meta { font-size: 10px; color: #52525b; text-transform: uppercase; letter-spacing: 1px; }
        
        .footer { padding: 40px; text-align: center; font-size: 11px; color: #3f3f46; border-top: 1px solid #1e3a5f; background: #000000; }
    </style>
    """

    final_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {css_style}
    </head>
    <body>
        <div class="email-wrapper">
            <div class="container">
                <div class="header">
                    <h1>SEA TRENDS</h1>
                    <p>{datetime.now().strftime('%B %d, %Y').upper()} | INTELLIGENCE</p>
                </div>
                
                <div class="content">
                    {body_html}
                    
                    {video_gallery}
                </div>
                
                <div class="footer">
                    Designed by Python & Gemini
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = formataddr((Header("SEA社媒情报局", 'utf-8').encode(), SENDER_EMAIL))
        msg['To'] = Header(",".join(RECEIVERS), 'utf-8')
        msg['Subject'] = Header(f"【早报】SEA游戏社媒热点趋势 ({datetime.now().strftime('%m-%d')})", 'utf-8')
        msg.attach(MIMEText(final_html, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVERS, msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    send_email()
