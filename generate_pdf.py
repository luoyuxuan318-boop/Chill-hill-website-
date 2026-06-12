#!/usr/bin/env python3
"""Generate a print-ready PDF from the brand visual handbook HTML.
Uses the existing index.html data, renders all sections at once,
then prints via headless Chrome with proper page styling."""

import re
import json
import subprocess
import os

BASE = '/Users/luoyuxuan/Desktop/秋山社·品牌视觉手册'

# Read the original HTML
with open(f'{BASE}/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. Build print CSS (brand-aligned, A4, beautiful typography)
# ============================================================
print_css = '''
  @page {
    size: A4;
    margin: 20mm 18mm 22mm 18mm;
    @bottom-center {
      content: "— " counter(page) " —";
      font-family: "PingFang SC", "Hiragino Sans GB", sans-serif;
      font-size: 9px;
      color: #c4a97a;
      letter-spacing: 2px;
    }
  }

  @page:first {
    @bottom-center {
      content: none;
    }
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #2c2416;
    background: #fff;
    line-height: 1.8;
  }

  /* ── Cover Page ── */
  .pdf-cover {
    page-break-after: always;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, #f9f6f0 0%, #ede6d8 40%, #f5f1ea 100%);
    text-align: center;
    position: relative;
  }
  .pdf-cover .cover-logo {
    width: 80px;
    margin-bottom: 32px;
    opacity: 0.85;
  }
  .pdf-cover .cover-brand {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: 12px;
    color: #2c2416;
    margin-bottom: 8px;
  }
  .pdf-cover .cover-brand-en {
    font-size: 14px;
    letter-spacing: 6px;
    color: #8b6f47;
    text-transform: uppercase;
    margin-bottom: 48px;
  }
  .pdf-cover .cover-divider {
    width: 60px;
    height: 2px;
    background: #b8973e;
    margin: 0 auto 40px;
  }
  .pdf-cover .cover-title {
    font-size: 17px;
    letter-spacing: 8px;
    color: #6b5e4a;
    font-weight: 500;
  }
  .pdf-cover .cover-subtitle {
    font-size: 10px;
    letter-spacing: 4px;
    color: #c4a97a;
    margin-top: 12px;
    text-transform: uppercase;
  }
  .pdf-cover .cover-slogan {
    position: absolute;
    bottom: 80px;
    font-size: 14px;
    letter-spacing: 4px;
    color: #8b6f47;
    font-weight: 600;
  }
  .pdf-cover .cover-slogan-en {
    font-size: 9px;
    letter-spacing: 3px;
    color: #c4b89a;
    margin-top: 6px;
  }

  /* ── Section Title Page (for major sections) ── */
  .section-title-page {
    page-break-before: always;
    page-break-after: avoid;
    padding-top: 80px;
    margin-bottom: 36px;
  }
  .section-num {
    font-size: 56px;
    font-weight: 700;
    color: #ede6d8;
    letter-spacing: 2px;
    line-height: 1;
    margin-bottom: -8px;
  }
  .section-label {
    font-size: 24px;
    font-weight: 700;
    color: #2c2416;
    letter-spacing: 6px;
    margin-bottom: 12px;
  }
  .section-desc {
    font-size: 11px;
    color: #6b5e4a;
    letter-spacing: 2px;
    padding-bottom: 24px;
    border-bottom: 2px solid #ede6d8;
  }

  /* ── Info Card (Section 01) ── */
  .info-block {
    background: #f9f6f0;
    border-radius: 6px;
    padding: 28px 32px;
    margin-bottom: 16px;
    border-left: 3px solid #b8973e;
  }
  .info-row {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
    align-items: baseline;
    font-size: 13px;
  }
  .info-label {
    color: #8b6f47;
    font-weight: 600;
    letter-spacing: 2px;
    min-width: 80px;
    font-size: 12px;
  }
  .info-value {
    color: #2c2416;
    letter-spacing: 1px;
  }
  .info-kw {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .info-kw span {
    font-size: 11px;
    padding: 3px 12px;
    border-radius: 10px;
    background: rgba(139,111,71,0.08);
    color: #8b6f47;
    letter-spacing: 1px;
  }
  .info-divider {
    border: none;
    border-top: 1px solid rgba(0,0,0,0.06);
    margin: 18px 0;
  }
  .info-intro {
    font-size: 13px;
    color: #2c2416;
    line-height: 2;
  }
  .info-slogan {
    margin-top: 16px;
    text-align: right;
  }
  .info-slogan .cn {
    font-size: 18px;
    font-weight: 700;
    color: #8b6f47;
    letter-spacing: 4px;
  }
  .info-slogan .en {
    font-size: 11px;
    color: #6b5e4a;
    letter-spacing: 2px;
    margin-top: 4px;
  }

  /* ── Brand Tone (Section 02) ── */
  .brand-block {
    background: #f9f6f0;
    border-radius: 6px;
    padding: 28px 32px;
    margin-bottom: 20px;
    border-left: 3px solid #8b6f47;
  }
  .brand-block .brand-name {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #2c2416;
  }
  .brand-block .brand-name .en {
    font-size: 13px;
    font-weight: 400;
    color: #6b5e4a;
    letter-spacing: 2px;
    margin-left: 12px;
  }
  .brand-block .meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
  }
  .brand-block .meta-row span {
    font-size: 11px;
    color: #8b6f47;
    background: rgba(139,111,71,0.06);
    padding: 3px 12px;
    border-radius: 10px;
    letter-spacing: 1px;
  }
  .brand-block .brand-intro {
    font-size: 13px;
    color: #2c2416;
    line-height: 2;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(0,0,0,0.05);
  }
  .brand-block .brand-slogan {
    text-align: right;
    margin-top: 14px;
    font-size: 16px;
    font-weight: 700;
    color: #8b6f47;
    letter-spacing: 3px;
  }
  .tone-box {
    background: #f5f1ea;
    border-radius: 6px;
    padding: 22px 28px;
    margin-top: 20px;
  }
  .tone-box .tone-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #2c2416;
    margin-bottom: 8px;
  }
  .tone-box .tone-kws {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .tone-box .tone-kws span {
    font-size: 11px;
    padding: 4px 14px;
    border-radius: 10px;
    background: rgba(139,111,71,0.1);
    color: #8b6f47;
    letter-spacing: 1px;
  }

  /* ── Image Grid ── */
  .img-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin: 20px 0;
  }
  .img-card {
    background: #fff;
    border: 1.5px dashed #c4a97a;
    border-radius: 6px;
    overflow: hidden;
    page-break-inside: avoid;
  }
  .img-card .img-wrap {
    width: 100%;
    min-height: 140px;
    max-height: 240px;
    background: linear-gradient(135deg, #f5f0e8, #ede6d8);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
  .img-card .img-wrap img {
    width: 100%;
    height: 100%;
    max-height: 240px;
    object-fit: contain;
    display: block;
  }
  .img-card .img-info {
    padding: 10px 12px;
  }
  .img-card .img-info .title {
    font-size: 12px;
    font-weight: 700;
    color: #2c2416;
    letter-spacing: 1px;
  }
  .img-card .img-info .sub {
    font-size: 10px;
    color: #6b5e4a;
    margin-top: 2px;
  }

  /* ── Full-width large image (system diagrams, overviews) ── */
  .img-full {
    width: 100%;
    margin: 16px 0 24px;
    page-break-inside: avoid;
  }
  .img-full .img-wrap {
    width: 100%;
    min-height: 180px;
    max-height: 420px;
    background: linear-gradient(135deg, #f5f0e8, #ede6d8);
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .img-full .img-wrap img {
    width: 100%;
    max-height: 420px;
    object-fit: contain;
    display: block;
  }
  .img-full .img-info {
    padding: 10px 4px 0;
    text-align: center;
  }
  .img-full .img-info .title {
    font-size: 13px;
    font-weight: 700;
    color: #2c2416;
    letter-spacing: 2px;
  }
  .img-full .img-info .sub {
    font-size: 10px;
    color: #6b5e4a;
    margin-top: 2px;
  }

  .sys-label {
    font-size: 12px;
    color: #8b6f47;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 6px;
  }

  /* ── Section Label ── */
  .section-subhead {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px;
    page-break-after: avoid;
  }
  .section-subhead .dot {
    width: 7px;
    height: 7px;
    background: #b8973e;
    border-radius: 50%;
  }
  .section-subhead span {
    font-size: 12px;
    font-weight: 700;
    color: #8b6f47;
    letter-spacing: 2px;
  }
  .section-subhead .tag {
    font-size: 9px;
    background: #2c2416;
    color: #e8d5b0;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 1px;
  }



  .platform-douyin { background: #e0e0e0 !important; color: #333 !important; }

  /* ── Large Image (full-width) ── */
  .full-img-wrap {
    width: 100%;
    margin: 16px 0;
    background: linear-gradient(135deg, #f5f0e8, #ede6d8);
    border-radius: 6px;
    overflow: hidden;
    page-break-inside: avoid;
  }
  .full-img-wrap img {
    width: 100%;
    display: block;
  }

  /* ── Page break utilities ── */
  .page-break { page-break-before: always; }
  .avoid-break { page-break-inside: avoid; }
'''

# ============================================================
# 2. Extract theme data from original HTML's JavaScript
# ============================================================
# Find the themes array in the JS
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if not script_match:
    print("ERROR: Could not find script block")
    exit(1)

js_code = script_match.group(1)

# Extract themes array content
themes_match = re.search(r'var themes = \[(.*?)\];', js_code, re.DOTALL)
if not themes_match:
    print("ERROR: Could not find themes array")
    exit(1)

themes_text = themes_match.group(1)

# We'll build the print HTML by extracting data manually
# since parsing JS safely is complex, let's hardcode based on the HTML we read

print("Building print HTML from theme data...")

# ============================================================
# 3. Build the print HTML
# ============================================================

# Helper functions (same as original)
def our(name):
    return f'images/{name}'



# Build our design cards HTML
def our_cards_html(items):
    cards = ''
    for o in items:
        cards += f'''
        <div class="img-card">
          <div class="img-wrap">
            <img src="{o['img']}" alt="{o['title']}" loading="lazy">
          </div>
          <div class="img-info">
            <div class="title">{o['title']}</div>
            <div class="sub">{o['sub']}</div>
          </div>
        </div>'''
    return f'<div class="section-subhead"><div class="dot"></div><span>秋山 · 现有设计</span><div class="tag">OURS</div></div><div class="img-grid">{cards}</div>'

# Build full-width large images (for system diagrams, overviews, posters)
def full_img_html(img_path, title='', sub=''):
    info = ''
    if title:
        info = f'<div class="img-info"><div class="title">{title}</div>' + (f'<div class="sub">{sub}</div>' if sub else '') + '</div>'
    return f'''
    <div class="img-full">
      <div class="img-wrap">
        <img src="{img_path}" alt="{title}" loading="lazy">
      </div>
      {info}
    </div>'''

def full_img_grid_html(items):
    cards = ''
    for o in items:
        cards += full_img_html(o['img'], o.get('title', ''), o.get('sub', ''))
    return f'<div class="section-subhead"><div class="dot"></div><span>秋山 · 现有设计</span><div class="tag">OURS</div></div>{cards}'

# Build mood board cards (no info labels, just images)
def mood_grid_html(images):
    cards = ''
    for img in images:
        cards += f'''
        <div class="img-card">
          <div class="img-wrap"><img src="{img}" alt="" loading="lazy"></div>
        </div>'''
    return f'<div class="img-grid">{cards}</div>'

# ============================================================
# Section data (extracted from the HTML)
# ============================================================

sections_html = ''

# ── Section 01: Brand Info ──
sections_html += '''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">01</div>
  <div class="section-label">品牌信息</div>
  <div class="section-desc">品牌身份 · 核心定位 · 价值主张</div>
</div>
<div class="info-block">
  <div class="info-row"><span class="info-label">品牌名称</span><span class="info-value">秋山社</span><span class="info-value" style="color:#6b5e4a;font-size:12px;margin-left:4px;">Chill Hill</span></div>
  <div class="info-row"><span class="info-label">品牌行业</span><span class="info-value">以咖啡、音乐、精酿为基底的生活方式品牌</span></div>
  <div class="info-row"><span class="info-label">品牌定位</span><span class="info-value">松弛、有度治愈</span></div>
  <div class="info-row"><span class="info-label">品牌调性</span><div class="info-kw"><span>克制</span><span>自然</span><span>温度</span><span>呼吸感</span><span>东方美学</span></div></div>
  <hr class="info-divider">
  <div class="info-intro">秋山社（Chill Hill）是一个以咖啡、音乐、精酿为基底的生活方式品牌。源于山林之间的宁静，我们希望创造一个能让情绪自然流动的空间。透过咖啡、简餐与民谣，让我们重新连接日常中的松弛感。</div>
  <div class="info-slogan"><div class="cn">秋山有度，情绪无束</div><div class="en">Chill by the hill, free to feel.</div></div>
</div>
'''

# ── Section 02: Brand Tone ──
mood_images = [f'images/moodboard-{i:02d}.jpg' for i in range(1, 6)]

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">02</div>
  <div class="section-label">品牌调性</div>
  <div class="section-desc">情绪版 · 品牌人格 · 视觉感受 —— 品牌的灵魂温度</div>
</div>
<div class="brand-block">
  <div class="brand-name">秋山社<span class="en">Chill Hill</span></div>
  <div class="meta-row"><span>以咖啡、音乐、精酿为基底的生活方式品牌</span><span>松弛、有度治愈</span><span>克制</span><span>自然</span></div>
  <div class="brand-intro">秋山社（Chill Hill）是一个以咖啡、音乐、精酿为基底的生活方式品牌。源于山林之间的宁静，我们希望创造一个能让情绪自然流动的空间。咖啡不是终点，而是通往松弛感的起点。透过咖啡、简餐与民谣，我们重新连接日常中的松弛感。</div>
  <div class="brand-slogan">秋山有度，情绪无束</div>
</div>
<div class="tone-box">
  <div class="tone-title">品牌关键词 / Tone Keywords</div>
  <div class="tone-kws"><span>松弛感</span><span>克制</span><span>自然</span><span>温度</span><span>呼吸感</span><span>东方美学</span></div>
</div>
<div class="section-subhead"><div class="dot"></div><span>情绪版 / Mood Board</span></div>
{mood_grid_html(mood_images)}
'''

# ── Section 03: Packaging ──
sys_html = ''
for label, fname in [('系统一：简约设计感', 'packaging-system-01.jpg'), ('系统二：潮流设计感', 'packaging-system-02.jpg'), ('系统三：莫兰迪色极简版', 'packaging-system-03.jpg')]:
    sys_html += f'''
    <div class="avoid-break">
      <div class="sys-label">{label}</div>
      {full_img_html(f'images/{fname}', label)}
    </div>'''

packaging_ours = [
    {'img': our('packaging-01.jpg'), 'title': '外卖杯', 'sub': '堂食杯 / 外带杯 / 杯套设计'},
    {'img': our('packaging-02.jpg'), 'title': '打包袋与杯托', 'sub': '外卖袋 / 瓦楞杯托 / 提手设计'},
    {'img': our('packaging-03.jpg'), 'title': '纸巾与封口贴', 'sub': 'logo纸巾 / 餐垫纸 / 季节封口贴'},
]


sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">03</div>
  <div class="section-label">包装系统</div>
  <div class="section-desc">外带杯 · 打包袋 · 餐巾纸 · 杯套 · 封口贴 · 产品包装 —— 品牌触达顾客的第一层肌肤</div>
</div>
<div class="section-subhead"><div class="dot"></div><span>包装系统方案</span></div>
{sys_html}
{our_cards_html(packaging_ours)}
'''

# ── Section 04: Vessels ──
vessels_ours = [
    {'img': our('vessels-01.jpg'), 'title': '堂食咖啡杯（热饮）', 'sub': '陶瓷杯 / 马克杯选品'},
    {'img': our('vessels-02.jpg'), 'title': '堂食咖啡杯（冷饮）', 'sub': '冷饮杯'},
    {'img': our('vessels-03.jpg'), 'title': '木质托盘', 'sub': '托盘'},
    {'img': our('vessels-04.jpg'), 'title': '餐具与托盘', 'sub': '筷子/盘子/碗'},
    {'img': our('vessels-05.jpg'), 'title': '鸡尾酒杯', 'sub': '马天尼杯/蝶形香槟杯/古典杯/白兰地杯/飓风杯'},
    {'img': our('vessels-06.jpg'), 'title': '轻食器皿', 'sub': '粗陶椭圆盘'},
    {'img': our('vessels-07.jpg'), 'title': '福鼎白茶茶具', 'sub': '白瓷'},
    {'img': our('vessels-08.jpg'), 'title': '狗牯脑绿茶茶具', 'sub': '瓷器'},
    {'img': our('vessels-09.jpg'), 'title': '普洱茶茶具', 'sub': '白瓷'},
    {'img': our('vessels-10.jpg'), 'title': '浮梁红茶茶具', 'sub': '瓷器'},
    {'img': our('vessels-11.jpg'), 'title': '成都坝坝盖碗茶茶具', 'sub': '瓷器'},
]

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">04</div>
  <div class="section-label">器皿与杯具</div>
  <div class="section-desc">咖啡杯 · 酒杯 · 茶具 · 餐具 —— 手中的触感决定口中的味道</div>
</div>
{our_cards_html(vessels_ours)}
'''

# ── Section 05: Merch ──
merch_ours = [
    {'img': our('merch-01.jpg'), 'title': '杯具', 'sub': '随行杯'},
    {'img': our('merch-02.jpg'), 'title': '雨伞', 'sub': '生活用品'},
    {'img': our('merch-03.jpg'), 'title': '咖啡杯', 'sub': '家用杯具'},
    {'img': our('merch-04.jpg'), 'title': '杯具与生活方式', 'sub': '保温杯'},
]

overview_html = f'''
<div class="section-subhead"><div class="dot"></div><span>整体调性图</span></div>
{full_img_html('images/merch-overview.jpg', '整体调性图')}'''

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">05</div>
  <div class="section-label">衍生品与周边</div>
  <div class="section-desc">帆布袋 · 徽章贴纸 · 服饰 · 杯具周边 · 生活方式产品 —— 品牌资产的延伸</div>
</div>
{overview_html}
{our_cards_html(merch_ours)}
'''

# ── Section 06: Uniform ──
uniform_ours = [
    {'img': our('uniform-01.jpg'), 'title': '潮流款T恤', 'sub': '主围裙设计 / 面料选择 / logo呈现方式'},
    {'img': our('uniform-02.jpg'), 'title': '基础款T恤', 'sub': '衬衫 / T恤 / 外套 / 季节工服方案'},
    {'img': our('uniform-03.jpg'), 'title': '咖啡师围裙', 'sub': '衬衫 / T恤 / 外套 / 季节工服方案'},
    {'img': our('uniform-04.jpg'), 'title': '基础款围裙', 'sub': '主围裙设计 / 面料选择 / logo呈现方式'},
    {'img': our('uniform-05.jpg'), 'title': '日常工服-基础款', 'sub': '衬衫 / T恤 / 外套 / 季节工服方案'},
    {'img': our('uniform-06.jpg'), 'title': '日常工服-潮流款', 'sub': '衬衫 / T恤 / 外套 / 季节工服方案'},
]

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">06</div>
  <div class="section-label">工服设计</div>
  <div class="section-desc">咖啡师围裙 · 日常工服 · 配饰 —— 穿在身上的品牌表达</div>
</div>
{our_cards_html(uniform_ours)}
'''

# ── Section 07: Product Cards ──
cards_ours = [
    {'img': our('product-card-01.jpg'), 'title': '咖啡卡片设计', 'sub': '命名：情绪价值+艺名 / 大地纹草香纸'},
    {'img': our('product-card-02.jpg'), 'title': '饮品卡片设计', 'sub': '命名：情绪价值+艺名 / 特种纸：树纹或雅柔'},
    {'img': our('product-card-03.jpg'), 'title': '菜单设计', 'sub': '不同品类分区 / 手绘菜单'},
    {'img': our('space-04.jpg'), 'title': '茶卡设计', 'sub': '茶叶说明卡'},
]

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">07</div>
  <div class="section-label">产品卡片设计</div>
  <div class="section-desc">豆卡 · 茶卡 · 桌卡 · 风味描述卡 · 产品信息卡 —— 每一张卡片都是品牌的名片</div>
</div>
{our_cards_html(cards_ours)}
'''

# ── Section 08: Space ──
space_cards = ''
for i in range(1, 9):
    space_cards += f'''
    <div class="img-card">
      <div class="img-wrap"><img src="images/space-img-{i:02d}.jpg" alt="空间 {i}" loading="lazy"></div>
    </div>'''

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">08</div>
  <div class="section-label">空间与氛围</div>
  <div class="section-desc">空间设计 · 氛围营造 · 灯光 · 软装 —— 顾客沉浸其中的完整体验</div>
</div>
<div class="img-grid">{space_cards}</div>
'''

# ── Section 09: Content ──
content_ours = [
    {'img': our('content-01.jpg'), 'title': '宣发海报', 'sub': '参考生活方式类品牌，输出品牌内容、核心价值观、生活方式'},
    {'img': our('content-02.jpg'), 'title': '私域活动', 'sub': '会员活动 / 新品品鉴 / 社群运营 / 活动视觉'},
    {'img': our('content-03.jpg'), 'title': '音乐与演出', 'sub': '演出海报 / 歌单卡 / 舞台背景 / 氛围记录'},
]

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">09</div>
  <div class="section-label">内容与传播</div>
  <div class="section-desc">宣发海报 · 私域活动 · 音乐演出 · 节庆限定 —— 品牌故事的每一次对外表达</div>
</div>
{full_img_grid_html(content_ours)}
'''

# ── Section 10: Photography ──
photo_ours = [
    {'img': our('photo-01.jpg'), 'title': '饮品类产品拍摄', 'sub': '咖啡、茶饮、酒的拍摄方案'},
    {'img': our('photo-02.jpg'), 'title': '茶产品拍摄', 'sub': '茶饮 / 酒饮 / 晚间特调的视觉风格'},
    {'img': our('photo-03.jpg'), 'title': '轻食与甜品拍摄', 'sub': '甜品 / 面包 / 轻食的摆盘与拍摄'},
    {'img': our('photo-04.jpg'), 'title': '出品视觉规范', 'sub': '杯具搭配 / 托盘组合 / 装饰元素 / 灯光标准'},
]

sections_html += f'''
<div class="page-break"></div>
<div class="section-title-page">
  <div class="section-num">10</div>
  <div class="section-label">产品视觉</div>
  <div class="section-desc">产品拍摄风格 · 出品标准 · 视觉规范 —— 每一杯都值得被记录</div>
</div>
{full_img_grid_html(photo_ours)}
'''

# ============================================================
# 4. Assemble final HTML
# ============================================================
print_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>秋山社 · 品牌视觉手册</title>
<style>{print_css}</style>
</head>
<body>

<div class="pdf-cover">
  <img class="cover-logo" src="images/logo.png" alt="logo">
  <div class="cover-brand">秋山社</div>
  <div class="cover-brand-en">Chill Hill</div>
  <div class="cover-divider"></div>
  <div class="cover-title">品 牌 视 觉 手 册</div>
  <div class="cover-subtitle">Brand Visual Handbook</div>
  <div class="cover-slogan">秋山有度，情绪无束</div>
  <div class="cover-slogan-en">Chill by the hill, free to feel.</div>
</div>

{sections_html}

</body>
</html>
'''

# Write print HTML
print_path = f'{BASE}/print.html'
with open(print_path, 'w', encoding='utf-8') as f:
    f.write(print_html)

print(f"Print HTML written to: {print_path}")
print(f"Total size: {len(print_html):,} bytes")

# ============================================================
# 5. Use Chrome headless to print to PDF
# ============================================================
chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
pdf_path = f'{BASE}/秋山社·品牌视觉手册.pdf'

print(f"\nGenerating PDF with Chrome headless...")
cmd = [
    chrome_path,
    '--headless',
    '--disable-gpu',
    '--no-sandbox',
    f'--print-to-pdf={pdf_path}',
    '--print-to-pdf-no-header',
    f'file://{print_path}'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
if result.returncode == 0 and os.path.exists(pdf_path):
    size_kb = os.path.getsize(pdf_path) / 1024
    size_mb = size_kb / 1024
    print(f"PDF generated: {pdf_path}")
    print(f"PDF size: {size_mb:.1f} MB")
else:
    print(f"Chrome error (exit {result.returncode}):")
    print(result.stderr[:500])
    # Try alternate chrome path
    alt_paths = [
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    ]
    for alt in alt_paths:
        if os.path.exists(alt):
            print(f"Trying {alt}...")
            cmd[0] = alt
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
                print(f"PDF generated: {pdf_path} ({size_mb:.1f} MB)")
                break

print("\nDone!")
