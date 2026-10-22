import os
import sys
import time
import shutil
import base64
from PIL import Image
import imageio
from selenium import webdriver
from selenium.webdriver.edge.options import Options

# HTML templates for rendering snapshots

HTML_BANNER = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1200px;
    height: 520px;
    background: radial-gradient(circle at 85% 15%, #1e293b 0%, #0f172a 50%, #020617 100%);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    color: #f1f5f9;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 50px 70px;
    overflow: hidden;
    position: relative;
  }
  body::before {
    content: '';
    position: absolute;
    width: 550px;
    height: 550px;
    background: radial-gradient(circle, rgba(14, 165, 233, 0.22) 0%, transparent 70%);
    top: -120px;
    right: 30px;
    pointer-events: none;
  }
  body::after {
    content: '';
    position: absolute;
    width: 450px;
    height: 450px;
    background: radial-gradient(circle, rgba(234, 179, 8, 0.16) 0%, transparent 70%);
    bottom: -120px;
    left: 80px;
    pointer-events: none;
  }
  .left-col {
    max-width: 680px;
    z-index: 2;
  }
  .badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(14, 165, 233, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.5);
    color: #38bdf8;
    padding: 7px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.8px;
    margin-bottom: 22px;
  }
  .badge-pulse {
    width: 9px;
    height: 9px;
    background: #38bdf8;
    border-radius: 50%;
    box-shadow: 0 0 12px #38bdf8;
  }
  h1 {
    font-size: 46px;
    font-weight: 900;
    line-height: 1.15;
    background: linear-gradient(135deg, #ffffff 20%, #38bdf8 65%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 14px;
    letter-spacing: -0.5px;
  }
  .subtitle {
    font-size: 16.5px;
    line-height: 1.55;
    color: #94a3b8;
    margin-bottom: 30px;
  }
  .features-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .feature-pill {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    padding: 10px 14px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13.5px;
    font-weight: 600;
    color: #e2e8f0;
  }
  .feature-pill span {
    font-size: 18px;
  }
  .right-col {
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  .stat-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.4);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 32px 40px;
    width: 320px;
    text-align: center;
    backdrop-filter: blur(16px);
  }
  .stat-badge {
    color: #facc15;
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
  }
  .stat-val {
    font-size: 58px;
    font-weight: 900;
    color: #22c55e;
    line-height: 1;
    margin-bottom: 8px;
    text-shadow: 0 0 30px rgba(34, 197, 94, 0.5);
  }
  .stat-max {
    font-size: 22px;
    color: #64748b;
    font-weight: 600;
  }
  .stat-desc {
    font-size: 13.5px;
    color: #cbd5e1;
    margin-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 12px;
    font-weight: 500;
  }
  .badge-row {
    display: flex;
    gap: 10px;
  }
  .chip {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 12px;
    color: #cbd5e1;
    font-weight: 600;
  }
</style>
</head>
<body>
  <div class="left-col">
    <div class="badge-tag">
      <div class="badge-pulse"></div>
      MICROSOFT REWARDS AUTOMATION v2.1
    </div>
    <h1>Bing Rewards Automation</h1>
    <p class="subtitle">Bộ công cụ tự động hóa tìm kiếm Bing đạt tối đa 150 điểm/ngày cho cả PC Desktop & Mobile Edge với công nghệ chống cooldown 15 phút và giả lập CDP Android.</p>
    
    <div class="features-grid">
      <div class="feature-pill"><span>🛡️</span> Auto-Cooldown 15m (Chống 0đ)</div>
      <div class="feature-pill"><span>📱</span> Giả lập Edge Android (CDP)</div>
      <div class="feature-pill"><span>🚀</span> QuickEdit Fix (Không kẹt Console)</div>
      <div class="feature-pill"><span>🔐</span> Persistent Profile (Đăng nhập 1 lần)</div>
      <div class="feature-pill"><span>🍪</span> Tự đóng Cookie & Overlay</div>
      <div class="feature-pill"><span>📊</span> Live Rewards Points Audit</div>
    </div>
  </div>

  <div class="right-col">
    <div class="stat-card">
      <div class="stat-badge">MỤC TIÊU HÀNG NGÀY</div>
      <div class="stat-val">150 <span class="stat-max">/ 150</span></div>
      <div class="stat-desc">90 PC Desktop + 60 Mobile Edge</div>
    </div>
    <div class="badge-row">
      <div class="chip">Python 3.12+</div>
      <div class="chip">Selenium 4</div>
      <div class="chip">Windows 1-Click</div>
    </div>
  </div>
</body>
</html>
"""

HTML_TERMINAL = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1100px;
    height: 700px;
    background: #080b12;
    padding: 20px;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .window {
    width: 100%;
    height: 100%;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 12px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.85);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .titlebar {
    height: 38px;
    background: #161b22;
    border-bottom: 1px solid #30363d;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
  }
  .window-buttons {
    display: flex;
    gap: 8px;
  }
  .win-btn {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }
  .close { background: #ff5f56; }
  .min { background: #ffbd2e; }
  .max { background: #27c93f; }
  .window-title {
    color: #8b949e;
    font-size: 13px;
    font-weight: 600;
  }
  .body-content {
    flex: 1;
    padding: 18px 24px;
    color: #e6edf3;
    font-size: 13px;
    line-height: 1.45;
    overflow: hidden;
  }
  .ascii-art {
    color: #38bdf8;
    font-weight: bold;
    line-height: 1.15;
    margin-bottom: 6px;
  }
  .version-tag {
    color: #8b949e;
    margin-bottom: 12px;
    font-size: 12.5px;
  }
  .version-tag b { color: #facc15; }
  .guide-box {
    border: 1px solid #1e3a8a;
    background: rgba(30, 58, 138, 0.2);
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 12px;
    color: #93c5fd;
    font-size: 12px;
    line-height: 1.45;
  }
  .stats-box {
    border: 1px solid #0284c7;
    background: rgba(14, 165, 233, 0.1);
    border-radius: 8px;
    padding: 12px 18px;
    margin: 10px 0;
  }
  .stats-title {
    color: #ffffff;
    font-weight: bold;
    font-size: 13px;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
  }
  .stat-line {
    display: flex;
    justify-content: space-between;
    margin: 4px 0;
  }
  .label { color: #cbd5e1; }
  .score { color: #22c55e; font-weight: bold; }
  .status-badge {
    background: rgba(34, 197, 94, 0.25);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.5);
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
  }
  .log-line {
    margin: 3px 0;
    font-size: 12.5px;
  }
  .cyan { color: #38bdf8; }
  .green { color: #4ade80; }
  .yellow { color: #facc15; }
  .blue { color: #60a5fa; }
  .purple { color: #c084fc; }
  .bold { font-weight: bold; }
</style>
</head>
<body>
  <div class="window">
    <div class="titlebar">
      <div class="window-buttons">
        <div class="win-btn close"></div>
        <div class="win-btn min"></div>
        <div class="win-btn max"></div>
      </div>
      <div class="window-title">Bing Rewards Automation Tool v2.1 (Command Prompt)</div>
      <div style="width: 40px;"></div>
    </div>
    <div class="body-content">
      <pre class="ascii-art">
  ██████╗ ██╗███╗   ██╗ ██████╗ 
  ██╔══██╗██║████╗  ██║██╔════╝ 
  ██████╔╝██║██╔██╗ ██║██║  ███╗
  ██╔══██╗██║██║╚██╗██║██║   ██║
  ██████╔╝██║██║ ╚████║╚██████╔╝
  ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ </pre>
      <div class="version-tag">Phiên bản: <b>v2.1 (Anti-Freeze & Mobile Rewards Fix)</b> | Tốc độ gõ phím mô phỏng người thật: <span style="color:#4ade80; font-weight:bold;">80 WPM</span></div>
      
      <div class="guide-box">
        <b>[QUICKEDIT FIX]</b> Windows Console QuickEdit Mode đã tắt. Chuột bấm không làm kẹt tiến trình.<br>
        <b>[PROFILE]</b> Tự động nạp Edge Profile tại: <code>Bing.v2\edge_profile</code> (Duy trì phiên đăng nhập MSA).
      </div>

      <div class="log-line"><span class="cyan">[*]</span> Đang khởi động Microsoft Edge (Chromium Engine)...</div>
      <div class="log-line"><span class="green">[OK]</span> Đã nhận diện phiên làm việc tài khoản Microsoft Rewards hợp lệ.</div>
      <div class="log-line"><span class="cyan">[*]</span> Đang truy vấn modal Points breakdown trên rewards.bing.com/earn...</div>

      <div class="stats-box">
        <div class="stats-title">THỐNG KÊ ĐIỂM MICROSOFT REWARDS HIỆN TẠI (ĐỢT HOÀN TẤT)</div>
        <div class="stat-line">
          <span class="label">Tổng điểm kiếm được hôm nay:</span>
          <span class="score">150 / 150 điểm</span>
        </div>
        <div class="stat-line">
          <span class="label">Desktop Bing search (30 searches @ 3 pts):</span>
          <span><b class="score">90 / 90</b> <span class="status-badge">[ĐÃ ĐẠT TỐI ĐA]</span></span>
        </div>
        <div class="stat-line">
          <span class="label">Mobile Bing search (20 searches @ 3 pts):</span>
          <span><b class="score">60 / 60</b> <span class="status-badge">[ĐÃ ĐẠT TỐI ĐA]</span></span>
        </div>
      </div>

      <div class="log-line"><span class="purple">[CDP]</span> Chuyển đổi thành công: Samsung Galaxy S24 Ultra (EdgA/124.0.0.0, Touch: ON, 390x844).</div>
      <div class="log-line"><span class="yellow">[*]</span> Search [4/4]: "quantum computing breakthroughs 2026" &rarr; Hoàn tất cuộn trang 2 chiều (380px) & Dwell 8.4s.</div>
      <div class="log-line"><span class="green bold">[THÀNH CÔNG] ĐÃ ĐẠT TỐI ĐA 100% ĐIỂM MICROSOFT REWARDS HÔM NAY! (150/150)</span></div>
      <div class="log-line"><span class="green">[OK]</span> Đã làm sạch file keywords.txt. Kết thúc phiên an toàn.</div>
    </div>
  </div>
</body>
</html>
"""

HTML_BREAKDOWN = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 900px;
    height: 540px;
    background: #090d16;
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #f1f5f9;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px;
  }
  .modal {
    width: 100%;
    background: #111827;
    border: 1px solid #374151;
    border-radius: 16px;
    padding: 32px 40px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.7);
  }
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #1f2937;
    padding-bottom: 18px;
    margin-bottom: 24px;
  }
  .modal-title {
    font-size: 24px;
    font-weight: 700;
    color: #f9fafb;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .badge-gold {
    background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
    color: #000;
    font-size: 12px;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 9999px;
  }
  .cards-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 24px;
  }
  .earn-card {
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 20px;
  }
  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .card-name {
    font-weight: 600;
    font-size: 16px;
    color: #e5e7eb;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .card-score {
    font-size: 22px;
    font-weight: 800;
    color: #10b981;
  }
  .progress-bg {
    width: 100%;
    height: 10px;
    background: #374151;
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 10px;
  }
  .progress-fill {
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, #10b981, #34d399);
    border-radius: 999px;
  }
  .card-sub {
    font-size: 13px;
    color: #9ca3af;
    display: flex;
    justify-content: space-between;
  }
  .total-bar {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 10px;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .total-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .total-left .check-icon {
    width: 34px;
    height: 34px;
    background: #10b981;
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 20px;
  }
  .total-title {
    font-size: 15px;
    font-weight: 700;
    color: #f9fafb;
  }
  .total-desc {
    font-size: 13px;
    color: #a7f3d0;
  }
  .total-val {
    font-size: 32px;
    font-weight: 900;
    color: #10b981;
  }
</style>
</head>
<body>
  <div class="modal">
    <div class="modal-header">
      <div class="modal-title">
        <span>Chi tiết điểm thưởng Microsoft Rewards</span>
        <span class="badge-gold">LEVEL 2 MEMBER</span>
      </div>
      <div style="color: #9ca3af; font-size: 13px;">Hôm nay: <b style="color:#10b981;">Đạt tối đa</b></div>
    </div>

    <div class="cards-grid">
      <div class="earn-card">
        <div class="card-top">
          <div class="card-name">💻 PC Bing Search</div>
          <div class="card-score">90 / 90</div>
        </div>
        <div class="progress-bg">
          <div class="progress-fill"></div>
        </div>
        <div class="card-sub">
          <span>30 lượt tìm kiếm (3 điểm / lượt)</span>
          <span style="color:#34d399; font-weight:600;">✓ Hoàn tất</span>
        </div>
      </div>

      <div class="earn-card">
        <div class="card-top">
          <div class="card-name">📱 Mobile Bing Search</div>
          <div class="card-score">60 / 60</div>
        </div>
        <div class="progress-bg">
          <div class="progress-fill"></div>
        </div>
        <div class="card-sub">
          <span>20 lượt tìm kiếm (3 điểm / lượt)</span>
          <span style="color:#34d399; font-weight:600;">✓ Hoàn tất</span>
        </div>
      </div>
    </div>

    <div class="total-bar">
      <div class="total-left">
        <div class="check-icon">✓</div>
        <div>
          <div class="total-title">Chúc mừng! Bạn đã cày xong tất cả điểm tìm kiếm hôm nay</div>
          <div class="total-desc">Tự động hóa hoàn toàn bằng Bing Rewards Tool v2.1 với Anti-Cooldown</div>
        </div>
      </div>
      <div class="total-val">150 PTS</div>
    </div>
  </div>
</body>
</html>
"""

HTML_MOBILE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1000px;
    height: 640px;
    background: #0b0f19;
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #f1f5f9;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 40px;
    padding: 30px;
  }
  .phone-frame {
    width: 290px;
    height: 580px;
    background: #000;
    border-radius: 40px;
    border: 5px solid #334155;
    box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 0 1px #475569;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    position: relative;
  }
  .notch {
    width: 100px;
    height: 20px;
    background: #000;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
  }
  .phone-screen {
    flex: 1;
    background: #f8fafc;
    color: #0f172a;
    display: flex;
    flex-direction: column;
    padding-top: 24px;
    overflow: hidden;
  }
  .bing-mobile-bar {
    padding: 12px 14px;
    background: #fff;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .bing-mobile-search {
    flex: 1;
    background: #f1f5f9;
    border-radius: 20px;
    padding: 8px 14px;
    font-size: 12px;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .rewards-chip {
    background: #0284c7;
    color: #fff;
    font-size: 11px;
    font-weight: bold;
    padding: 3px 8px;
    border-radius: 12px;
  }
  .serp-results {
    padding: 14px;
    font-size: 12px;
  }
  .result-card {
    background: #fff;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 10px;
  }
  .result-url { font-size: 10px; color: #64748b; margin-bottom: 2px; }
  .result-title { font-size: 13px; font-weight: 700; color: #0284c7; margin-bottom: 4px; }
  .result-desc { font-size: 11px; color: #475569; line-height: 1.4; }
  .touch-pointer {
    position: absolute;
    width: 28px;
    height: 28px;
    background: rgba(14, 165, 233, 0.4);
    border: 2px solid #0ea5e9;
    border-radius: 50%;
    top: 320px;
    left: 140px;
  }

  .info-panel {
    max-width: 540px;
  }
  .cdp-tag {
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 14px;
  }
  h2 {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 14px;
    line-height: 1.2;
  }
  p {
    font-size: 15px;
    color: #94a3b8;
    line-height: 1.55;
    margin-bottom: 20px;
  }
  .cdp-feature-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .cdp-item {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14px;
  }
  .cdp-item code {
    background: #0f172a;
    color: #38bdf8;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
  }
</style>
</head>
<body>
  <div class="phone-frame">
    <div class="notch"></div>
    <div class="phone-screen">
      <div class="bing-mobile-bar">
        <div style="font-weight:bold; color:#0284c7; font-size:14px;">b</div>
        <div class="bing-mobile-search">renewable energy solutions 2026</div>
        <div class="rewards-chip">+3 PTS</div>
      </div>
      <div class="serp-results">
        <div class="result-card">
          <div class="result-url">https://energy.gov/clean-tech</div>
          <div class="result-title">Top Clean Energy Innovations</div>
          <div class="result-desc">Comprehensive breakdown of sustainable power infrastructure breakthroughs for 2026.</div>
        </div>
        <div class="result-card">
          <div class="result-url">https://technologyreview.com/energy</div>
          <div class="result-title">Next-Gen Solar & Battery Storage</div>
          <div class="result-desc">How grid-scale storage is transforming modern renewable adoption worldwide.</div>
        </div>
      </div>
    </div>
    <div class="touch-pointer"></div>
  </div>

  <div class="info-panel">
    <div class="cdp-tag">CHROME DEVTOOLS PROTOCOL (CDP)</div>
    <h2>Giả Lập Edge Android Hoàn Hảo</h2>
    <p>Giải quyết triệt để lỗi Mobile bị 0/60 điểm. Tool chuyển đổi giao diện sang Samsung Galaxy S24 Ultra với đầy đủ Client Hints và mô phỏng cảm ứng ngón tay người thật.</p>

    <div class="cdp-feature-list">
      <div class="cdp-item">
        <span>📲</span>
        <div><b>User-Agent & Client Hints:</b> <code>EdgA/124.0.0.0</code> & <code>Sec-CH-UA-Mobile: ?1</code></div>
      </div>
      <div class="cdp-item">
        <span>👆</span>
        <div><b>Touch Emulation:</b> Cảm ứng đa điểm 5 touch points & cuộn trang 2 chiều</div>
      </div>
      <div class="cdp-item">
        <span>📐</span>
        <div><b>Màn hình di động chuẩn:</b> Viewport <code>390x844</code> @ 3x DeviceScaleFactor</div>
      </div>
      <div class="cdp-item">
        <span>📡</span>
        <div><b>Kích hoạt Telemetry:</b> Chờ tải <code>#b_results</code> trước khi ghi nhận điểm</div>
      </div>
    </div>
  </div>
</body>
</html>
"""

HTML_COOLDOWN = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1000px;
    height: 420px;
    background: #090e17;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px;
  }
  .box {
    width: 100%;
    background: #0f172a;
    border: 2px solid #eab308;
    border-radius: 12px;
    padding: 28px 36px;
    box-shadow: 0 10px 40px rgba(234, 179, 8, 0.2);
  }
  .title {
    color: #eab308;
    font-size: 20px;
    font-weight: 800;
    text-align: center;
    letter-spacing: 1px;
    margin-bottom: 12px;
    text-shadow: 0 0 15px rgba(234, 179, 8, 0.4);
  }
  .desc {
    color: #94a3b8;
    font-size: 13.5px;
    text-align: center;
    line-height: 1.5;
    margin-bottom: 24px;
  }
  .progress-container {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
  }
  .progress-tag {
    background: #0284c7;
    color: #fff;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
  }
  .progress-bar-wrap {
    flex: 1;
    margin: 0 20px;
    height: 18px;
    background: #334155;
    border-radius: 999px;
    overflow: hidden;
  }
  .progress-bar-fill {
    width: 65%;
    height: 100%;
    background: linear-gradient(90deg, #38bdf8, #eab308);
  }
  .timer-val {
    font-size: 22px;
    font-weight: bold;
    color: #facc15;
    min-width: 140px;
    text-align: right;
  }
  .shortcuts {
    display: flex;
    justify-content: center;
    gap: 30px;
    font-size: 12px;
    color: #64748b;
  }
  .shortcuts span b {
    color: #cbd5e1;
    background: #334155;
    padding: 2px 6px;
    border-radius: 4px;
  }
</style>
</head>
<body>
  <div class="box">
    <div class="title">⏳ KÍCH HOẠT THỜI GIAN NGHỈ COOLDOWN 15 PHÚT AN TOÀN</div>
    <div class="desc">
      Microsoft Rewards giới hạn chỉ tính điểm cho 3-4 lượt tìm kiếm trong mỗi block 15 phút.<br>
      Tool tự động tạm dừng an toàn để tránh bị phạt 0 điểm và sẽ tự động tiếp tục đợt tiếp theo.
    </div>

    <div class="progress-container">
      <div class="progress-tag">[COOLDOWN]</div>
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill"></div>
      </div>
      <div class="timer-val">09:42 còn lại</div>
    </div>

    <div class="shortcuts">
      <span>💡 Thu nhỏ cửa sổ này để làm việc khác</span>
      <span>Bấm <b>[Enter]</b> hoặc <b>[Space]</b> để bỏ qua chờ</span>
      <span>Bấm <b>[Ctrl+C]</b> để dừng an toàn</span>
    </div>
  </div>
</body>
</html>
"""

def generate_assets():
    print("[*] Khoi tao Edge Headless de render snapshots...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,800")
    
    driver = webdriver.Edge(options=options)
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    assets_dirs = [
        os.path.join(base_dir, "assets"),
        os.path.join(base_dir, "Bing.v2", "assets")
    ]
    for ad in assets_dirs:
        os.makedirs(ad, exist_ok=True)

    temp_html_path = os.path.join(base_dir, "temp_render.html")

    def save_snapshot(html_content, filename, width, height):
        driver.set_window_size(width, height)
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        driver.get(f"file:///{temp_html_path.replace(os.sep, '/')}")
        time.sleep(0.6)
        dest1 = os.path.join(assets_dirs[0], filename)
        driver.save_screenshot(dest1)
        shutil.copy(dest1, os.path.join(assets_dirs[1], filename))
        size_kb = os.path.getsize(dest1) / 1024
        print(f"  [OK] Da tao {filename} ({width}x{height}) - {size_kb:.1f} KB")
        return dest1

    print("[*] 1. Render PNG Snapshots:")
    save_snapshot(HTML_BANNER, "banner.png", 1200, 520)
    save_snapshot(HTML_TERMINAL, "terminal_snapshot.png", 1100, 700)
    save_snapshot(HTML_BREAKDOWN, "rewards_breakdown.png", 900, 540)
    save_snapshot(HTML_MOBILE, "mobile_emulation.png", 1000, 640)
    save_snapshot(HTML_COOLDOWN, "cooldown_timer.png", 1000, 420)

    # 2. Render Animated GIF and MP4
    print("\n[*] 2. Render Animated GIF & Video MP4:")
    
    frames_html = [
        # Frame 1: Quickstart launch
        ("""<!DOCTYPE html><html><body style="margin:0; background:#0d1117; color:#e6edf3; font-family:'Cascadia Code', monospace; padding:30px;">
        <div style="border:1px solid #30363d; border-radius:10px; padding:25px; background:#161b22;">
          <h2 style="color:#58a6ff; margin:0 0 15px 0;">🚀 BING REWARDS AUTOMATION v2.1 - STARTUP</h2>
          <p style="color:#7ee787; font-size:16px;">[1/3] Kiem tra Python 3.12 64-bit... [OK]</p>
          <p style="color:#7ee787; font-size:16px;">[2/3] Kiem tra Moi truong ao venv... [OK]</p>
          <p style="color:#7ee787; font-size:16px;">[3/3] Khoi chay bing_auto.py engine... [OK]</p>
          <hr style="border:0; border-top:1px solid #30363d; margin:15px 0;">
          <p style="color:#facc15; font-size:15px; font-weight:bold;">&gt;&gt; [QUICKEDIT FIX] Windows QuickEdit Mode da duoc vo hieu hoa! Chuot bam khong bao gio bi ket console.</p>
        </div></body></html>""", 960, 540),

        # Frame 2: Mode selection menu
        ("""<!DOCTYPE html><html><body style="margin:0; background:#0d1117; color:#e6edf3; font-family:'Cascadia Code', monospace; padding:30px;">
        <div style="border:2px solid #0284c7; padding:24px; border-radius:12px; background:#0f172a;">
          <h2 style="color:#38bdf8; margin:0 0 14px 0;">CHỌN CHẾ ĐỘ TÌM KIẾM BING REWARDS</h2>
          <div style="background:rgba(34,197,94,0.15); border:1px solid #22c55e; border-radius:8px; padding:12px; margin-bottom:10px;">
            <p style="color:#4ade80; font-weight:bold; font-size:16px;">[1] Tự động hoàn toàn (Auto-Cooldown) [KHUYÊN DÙNG]</p>
            <p style="color:#cbd5e1; font-size:14px; margin-top:4px;">- Tìm 4 lượt (12đ) &rarr; Chờ 15p &rarr; Tự lặp lại đến khi FULL 150/150 điểm</p>
            <p style="color:#cbd5e1; font-size:14px;">- An toàn 100%, khắc phục triệt để lỗi 0/60 Mobile do giãn cách 15 phút</p>
          </div>
          <p style="color:#facc15; font-size:14px;">[2] Chạy 1 đợt an toàn (4 lượt / 12 điểm) rồi dừng</p>
          <p style="color:#f87171; font-size:14px; margin-top:4px;">[3] Chạy một mạch tất cả (Không nghỉ 15 phút)</p>
          <hr style="border:0; border-top:1px solid #334155; margin:14px 0;">
          <p style="color:#38bdf8; font-size:15px; font-weight:bold;">&gt;&gt; Tự động chọn [1] sau 5 giây... [ĐÃ CHỌN CHẾ ĐỘ 1]</p>
        </div></body></html>""", 960, 540),

        # Frame 3: Fetching Points breakdown
        ("""<!DOCTYPE html><html><body style="margin:0; background:#0d1117; color:#e6edf3; font-family:'Cascadia Code', monospace; padding:30px;">
        <div style="border:1px solid #10b981; padding:24px; border-radius:12px; background:#064e3b22;">
          <h2 style="color:#10b981; margin:0 0 16px 0;">THỐNG KÊ ĐIỂM MICROSOFT REWARDS HIỆN TẠI</h2>
          <div style="display:flex; justify-content:space-between; font-size:16px; margin:8px 0;">
            <span>💻 Desktop Bing search:</span>
            <span style="color:#facc15; font-weight:bold;">12 / 90 điểm [CẦN SEARCH 26 LƯỢT]</span>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:16px; margin:8px 0;">
            <span>📱 Mobile Bing search:</span>
            <span style="color:#facc15; font-weight:bold;">0 / 60 điểm [CẦN SEARCH 20 LƯỢT]</span>
          </div>
          <hr style="border:0; border-top:1px solid #065f46; margin:16px 0;">
          <p style="color:#38bdf8; font-size:15px; font-weight:bold;">[*] Đợt 1: Thực hiện 4 lượt tìm kiếm PC Desktop an toàn...</p>
        </div></body></html>""", 960, 540),

        # Frame 4: Running PC search
        ("""<!DOCTYPE html><html><body style="margin:0; background:#0d1117; color:#e6edf3; font-family:'Cascadia Code', monospace; padding:30px;">
        <div style="border:1px solid #38bdf8; padding:24px; border-radius:12px; background:#0c192c;">
          <h2 style="color:#38bdf8; margin:0 0 12px 0;">[PC_DESKTOP] Tìm kiếm tự nhiên có tương tác</h2>
          <p style="font-size:15px; color:#e2e8f0; margin-bottom:8px;">[1/4] Gõ phím mô phỏng người thật: <span style="color:#4ade80; font-weight:bold;">"sustainable energy solutions 2026"</span></p>
          <p style="font-size:14px; color:#94a3b8;">&bull; Trang kết quả (#b_results) render thành công trong 1.1s</p>
          <p style="font-size:14px; color:#94a3b8;">&bull; Cuộn trang 2 chiều 340px &bull; Dwell time ngẫu nhiên 8.5s &bull; Kích hoạt beacon /rewards/</p>
          <hr style="border:0; border-top:1px solid #1e3a5f; margin:14px 0;">
          <p style="color:#10b981; font-size:15px; font-weight:bold;">[OK] Hoàn thành lượt tìm kiếm 1/4 (+3 điểm Desktop)</p>
        </div></body></html>""", 960, 540),

        # Frame 5: Switching to Mobile CDP
        ("""<!DOCTYPE html><html><body style="margin:0; background:#0d1117; color:#e6edf3; font-family:'Cascadia Code', monospace; padding:30px;">
        <div style="border:1px solid #c084fc; padding:24px; border-radius:12px; background:#2e106522;">
          <h2 style="color:#c084fc; margin:0 0 12px 0;">📱 [CDP] KÍCH HOẠT GIẢ LẬP EDGE ANDROID (S24 ULTRA)</h2>
          <p style="font-size:14px; color:#cbd5e1; margin-bottom:6px;">&bull; User-Agent: <span style="color:#38bdf8;">Mozilla/5.0 ... EdgA/124.0.0.0 (Client Hints Mobile: ?1)</span></p>
          <p style="font-size:14px; color:#cbd5e1; margin-bottom:12px;">&bull; Viewport: <span style="color:#38bdf8;">390x844 (Scale 3x)</span> | Touch Emulation: <span style="color:#4ade80; font-weight:bold;">ENABLED</span></p>
          <hr style="border:0; border-top:1px solid #4c1d95; margin:14px 0;">
          <p style="color:#4ade80; font-size:15px; font-weight:bold;">[MOBILE] [1/4] Search: "cloud artificial intelligence chips"</p>
          <p style="color:#a78bfa; font-size:14px; margin-top:6px;">&bull; Telemetry Mobile ghi nhận điểm hợp lệ (+3 điểm Mobile)</p>
        </div></body></html>""", 960, 540),

        # Frame 6: 15-minute cooldown countdown
        ("""<!DOCTYPE html><html><body style="margin:0; background:#0d1117; color:#e6edf3; font-family:'Cascadia Code', monospace; padding:30px;">
        <div style="border:2px solid #eab308; padding:26px; border-radius:12px; text-align:center; background:#1e1a06;">
          <h2 style="color:#eab308; margin-bottom:12px;">⏳ COOLDOWN 15 PHÚT AN TOÀN ĐANG ĐẾM NGƯỢC</h2>
          <p style="color:#cbd5e1; font-size:14px; margin-bottom:16px;">Microsoft chỉ cộng điểm 3-4 lượt search/15 phút. Tool tạm dừng an toàn chống bị phạt 0 điểm.</p>
          <div style="background:#0f172a; border:1px solid #334155; padding:16px; border-radius:8px; margin:16px 0;">
            <span style="color:#38bdf8; font-size:22px; font-weight:bold;">[COOLDOWN] █████████░░░░░ 09:15 còn lại...</span>
          </div>
          <p style="color:#94a3b8; font-size:13px;">[Mẹo]: Thu nhỏ cửa sổ làm việc khác &bull; Bấm [Enter] để bỏ qua &bull; Bấm [Ctrl+C] để dừng</p>
        </div></body></html>""", 960, 540),

        # Frame 7: 100% Achievement Final
        ("""<!DOCTYPE html><html><body style="margin:0; background:#0d1117; color:#e6edf3; font-family:'Segoe UI', sans-serif; padding:30px;">
        <div style="border:2px solid #10b981; padding:30px; border-radius:16px; text-align:center; background:rgba(16,185,129,0.12); box-shadow:0 10px 40px rgba(16,185,129,0.2);">
          <h1 style="color:#10b981; font-size:36px; margin-bottom:14px;">🎉 THÀNH CÔNG! ĐẠT TỐI ĐA 150/150 ĐIỂM</h1>
          <div style="display:flex; justify-content:center; gap:40px; margin:20px 0;">
            <div style="background:#0f172a; padding:16px 30px; border-radius:10px; border:1px solid #10b981;">
              <div style="color:#94a3b8; font-size:14px;">Desktop Bing</div>
              <div style="color:#22c55e; font-size:28px; font-weight:900;">90 / 90</div>
            </div>
            <div style="background:#0f172a; padding:16px 30px; border-radius:10px; border:1px solid #10b981;">
              <div style="color:#94a3b8; font-size:14px;">Mobile Bing</div>
              <div style="color:#22c55e; font-size:28px; font-weight:900;">60 / 60</div>
            </div>
          </div>
          <p style="color:#a7f3d0; font-size:15px; font-weight:600;">Toàn bộ tiến trình chạy tự động 100% &bull; Không cần bất kỳ can thiệp thủ công nào!</p>
        </div></body></html>""", 960, 540)
    ]

    pil_images = []
    for idx, (f_html, fw, fh) in enumerate(frames_html):
        driver.set_window_size(fw, fh)
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(f_html)
        driver.get(f"file:///{temp_html_path.replace(os.sep, '/')}")
        time.sleep(0.5)
        temp_frame_path = os.path.join(assets_dirs[0], f"frame_{idx}.png")
        driver.save_screenshot(temp_frame_path)
        img = Image.open(temp_frame_path).convert("RGB")
        pil_images.append(img)
        try: os.remove(temp_frame_path)
        except: pass

    # Clean up temp html
    try: os.remove(temp_html_path)
    except: pass

    # Save animated GIF (duration 2000ms per frame, loop forever)
    gif_path = os.path.join(assets_dirs[0], "demo_run.gif")
    pil_images[0].save(
        gif_path,
        save_all=True,
        append_images=pil_images[1:],
        duration=[2200, 2400, 2200, 2400, 2400, 2600, 3200],
        loop=0,
        optimize=True
    )
    shutil.copy(gif_path, os.path.join(assets_dirs[1], "demo_run.gif"))
    size_gif_kb = os.path.getsize(gif_path) / 1024
    print(f"  [OK] Da tao demo_run.gif ({len(pil_images)} frames) - {size_gif_kb:.1f} KB")

    # Save MP4 video
    mp4_path = os.path.join(assets_dirs[0], "demo_video.mp4")
    try:
        import numpy as np
        video_frames = []
        durations = [3, 4, 3, 4, 4, 4, 5]  # seconds for each scene
        fps = 2
        for img, sec in zip(pil_images, durations):
            np_frame = np.array(img)
            h, w, _ = np_frame.shape
            if h % 16 != 0:
                h = (h // 16) * 16
            if w % 16 != 0:
                w = (w // 16) * 16
            np_frame = np_frame[:h, :w, :]
            for _ in range(sec * fps):
                video_frames.append(np_frame)

        writer = imageio.get_writer(mp4_path, fps=fps, codec='libx264', quality=8)
        for vf in video_frames:
            writer.append_data(vf)
        writer.close()
        shutil.copy(mp4_path, os.path.join(assets_dirs[1], "demo_video.mp4"))
        size_mp4_kb = os.path.getsize(mp4_path) / 1024
        print(f"  [OK] Da tao demo_video.mp4 (Thoi luong: {len(video_frames)//fps}s) - {size_mp4_kb:.1f} KB")
    except Exception as e:
        print(f"  [!] Loi render mp4: {e}")

    driver.quit()
    print("[*] Hoan tat toan bo assets thanh cong!")

if __name__ == "__main__":
    generate_assets()
