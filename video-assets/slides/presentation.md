---
marp: true
theme: default
size: 16:9
style: |
  /* 全体の基本設定：NotionやLinearのようなモダンなフォント指定 */
  section {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    letter-spacing: 0.05em;
  }

  /* 実際のUI画面に寄せた淡いグロー（光）を持つ白背景 */
  .bg-light-glow {
    background-color: #ffffff;
    background-image:
      radial-gradient(circle at top left, rgba(102, 126, 234, 0.15), transparent 40%),
      radial-gradient(circle at bottom right, rgba(118, 75, 162, 0.15), transparent 40%);
    color: #1a1a1a;
  }

  /* 深みのあるダーク背景 */
  .bg-dark {
    background-color: #0a0a0a;
    color: #ffffff;
  }

  /* 警戒感と不穏さを出すダークパープル */
  .bg-dark-purple {
    background-color: #1a1a2e;
    background-image: radial-gradient(circle at center, rgba(118, 75, 162, 0.2), transparent 60%);
    color: #ffffff;
  }

  /* グラデーションテキスト（AI感の象徴） */
  .text-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .text-alert { color: #ff6b6b; font-weight: 600; }
  .text-gray { color: #888888; }

  /* タイポグラフィのメリハリ */
  .title-main { font-size: 3.5em; font-weight: 700; letter-spacing: -0.02em; }
  .subtitle { font-size: 1.2em; font-weight: 300; letter-spacing: 0.1em; color: #888; }
  .text-huge { font-size: 5.5em; font-weight: 800; line-height: 1.1; letter-spacing: -0.03em; }
  .text-large-num { font-size: 4.5em; font-weight: 700; letter-spacing: -0.05em; line-height: 1;}

  /* UI風のカードコンポーネント */
  .card-container { display: flex; gap: 30px; justify-content: center; align-items: center; margin: 40px 0; }
  .card {
    padding: 20px 40px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(102, 126, 234, 0.2);
    box-shadow: 0 8px 30px rgba(0,0,0,0.04);
    font-size: 1.4em;
    font-weight: 500;
    color: #333;
    backdrop-filter: blur(10px);
  }

  /* ダークモード用のリスト */
  ul.minimal-list {
    text-align: left;
    display: inline-block;
    font-size: 1.8em;
    list-style-type: none;
    padding: 0;
    font-weight: 300;
    line-height: 1.6;
  }
  ul.minimal-list li { margin-bottom: 20px; color: #eaeaea; }
  ul.minimal-list li::before {
    content: "—";
    color: #ff6b6b;
    display: inline-block;
    width: 1.5em;
    margin-left: -1.5em;
  }

  .arrow { font-size: 1.5em; color: #667eea; opacity: 0.7; }
---

<!-- _class: bg-dark -->
<div class="title-main text-gradient">AI Security Reviewer</div>
<br>
<div class="subtitle">── for the Spec-Driven era ──</div>
<br><br><br><br><br>
<div style="font-size: 0.7em; color: #555; letter-spacing: 0.05em;">Microsoft AI Agent Hackathon 2026</div>

---

<!-- _class: bg-light-glow -->
<div style="text-align: left; width: 100%; padding-left: 80px; margin-bottom: 20px;">
  <span style="font-size: 1.4em; font-weight: 400; color: #666;">SDDをご存じですか？</span>
</div>

<div class="text-huge text-gradient">SDD</div>
<br>
<div style="font-size: 1.6em; font-weight: 300; color: #555;">Specification-Driven Development</div>
<div style="font-size: 1.1em; color: #888; margin-top: 10px;">仕様駆動開発</div>

---

<!-- _class: bg-light-glow -->
<div class="card-container" style="margin-top: 0;">
  <div class="card">仕様書</div>
  <div class="arrow">➔</div>
  <div class="card">AI</div>
  <div class="arrow">➔</div>
  <div class="card">コード</div>
</div>

<div style="display: flex; justify-content: center; gap: 100px; margin-top: 40px; margin-bottom: 20px;">
  <div style="text-align: left;">
    <div style="font-size: 1em; color: #888; margin-bottom: 10px;">タスク数</div>
    <div class="text-gradient text-large-num">78</div>
  </div>
  <div style="text-align: left;">
    <div style="font-size: 1em; color: #888; margin-bottom: 10px;">開発期間</div>
    <div class="text-gradient text-large-num" style="display: flex; align-items: baseline; gap: 10px;">1<span style="font-size: 0.4em; font-weight: 400;">週間</span></div>
  </div>
</div>

<div style="font-size: 1.6em; font-weight: 600; color: #333;">本来3ヶ月の規模を、たった1週間で。</div>
<div style="font-size: 1em; color: #888; margin-top: 15px;">初めての個人開発でも完走</div>

---

<!-- _class: bg-dark-purple -->
<div style="text-align: left; width: 80%;">
  <div style="font-size: 3em; margin-bottom: 50px; font-weight: 300; letter-spacing: -0.02em;">But, there's a <span class="text-alert">trap</span>.</div>

  <ul class="minimal-list">
    <li>仕様書とコードの乖離</li>
    <li>コードのブラックボックス化</li>
  </ul>

  <br><br>
  <div style="font-size: 1.4em; color: #999; margin-top: 40px;">
    特に懸念したのは… <span class="text-alert" style="font-weight: 600; font-size: 1.2em;">セキュリティ</span>
  </div>
</div>

---

<!-- _class: bg-dark-purple -->
<div style="display: flex; justify-content: space-around; width: 80%; margin-bottom: 40px;">
  <div style="text-align: center;">
    <div style="font-size: 1.2em; color: #aaa; margin-bottom: 15px;">プロンプトの質</div>
    <div style="font-size: 2.5em; opacity: 0.8;">🎲</div>
  </div>
  <div style="text-align: center;">
    <div style="font-size: 1.2em; color: #aaa; margin-bottom: 15px;">AIモデル</div>
    <div style="font-size: 2.5em; opacity: 0.8;">🤖</div>
  </div>
  <div style="text-align: center;">
    <div style="font-size: 1.2em; color: #aaa; margin-bottom: 15px;">仕様書の深さ</div>
    <div style="font-size: 2.5em; opacity: 0.8;">📄</div>
  </div>
</div>

<div class="arrow" style="transform: rotate(90deg); margin: 20px 0;">➔</div>

<div style="font-size: 3.5em; font-weight: 700; margin-top: 20px; letter-spacing: -0.02em;">
  セキュリティが、<br><span class="text-alert">ギャンブル化</span>
</div>

---

<!-- _class: bg-dark -->
<div style="font-size: 1.8em; font-weight: 300; color: #888; margin-bottom: 40px;">So, I built one.</div>

<div style="font-size: 3em; margin-bottom: 20px; opacity: 0.9;">🛡️</div>
<div class="title-main text-gradient" style="font-size: 3em;">AI Security Reviewer</div>

<br><br>
<div style="font-size: 1.5em; font-weight: 300; color: #ccc; letter-spacing: 0.05em;">
  SDDで作ったアプリを、SDDで作ったアプリで守る
</div>

---

<!-- _class: bg-dark -->
<div class="title-main text-gradient" style="font-size: 3em; margin-bottom: 30px;">AI Security Reviewer</div>

<div style="font-size: 2em; font-weight: 300; color: #fff; margin-bottom: 80px;">
  安心な SDD 開発を。
</div>

<div style="font-size: 1em; font-weight: 300; color: #666; letter-spacing: 0.05em; font-family: monospace;">
  github.com/dentsusoken/ai-security-reviewer
</div>
