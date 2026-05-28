---
marp: true
theme: gaia
size: 16:9
paginate: false
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Helvetica Neue', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
    padding: 80px;
    justify-content: center;
  }
  h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 80px;
    margin: 20px 0;
  }
  h2 {
    color: #333;
    font-weight: 300;
    font-size: 48px;
    margin: 20px 0;
  }
  h3 {
    color: #555;
    font-weight: 400;
    font-size: 36px;
    margin: 15px 0;
  }
  .small {
    font-size: 28px;
    color: #888;
    font-weight: 300;
  }
  .big-number {
    font-size: 100px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
  }
  .warning {
    color: #d63031;
  }
  .center {
    text-align: center;
  }
---

<!-- スライド1: タイトル(オープニング用) -->
<!-- _backgroundColor: #0a0a0a -->
<!-- _color: #ffffff -->

<div class="center">

# AI Security Reviewer

<br>

<div class="small">── for the Spec-Driven era ──</div>

</div>

---

<!-- スライド2: ①SDDとは? -->

<div class="center">

## Have you heard of SDD?

<br>

# Specification-Driven Development

<br>

<div class="small">─ 仕様駆動開発 ─</div>

</div>

---

<!-- スライド3: ②SDDのメリット -->

<div class="center">

### 📝 specification.md
### ⬇
### 🤖 AI Agent
### ⬇
### 💻 Production Code

<br>

# <span class="big-number">78</span> tasks / <span class="big-number">1</span> week

<div class="small">初めての個人開発でも完走</div>

</div>

---

<!-- スライド4: ③SDDの落とし穴 -->
<!-- _backgroundColor: #1a1a2e -->
<!-- _color: #ffffff -->

<div class="center">

## But, there's a trap.

<br>

## ⚠ 仕様書とコードの、乖離

<br>

## ⚠ コードの、ブラックボックス化

</div>

---

<!-- スライド5: ④セキュリティのギャンブル化 -->

<div class="center">

## 🎲 Prompt quality

## 🎲 AI model

## 🎲 Specification depth

## ⬇

# Security becomes a <span class="warning">gamble</span>.

</div>

---

<!-- スライド6: ⑤解決アプローチ -->
<!-- _backgroundColor: #0a0a0a -->
<!-- _color: #ffffff -->

<div class="center">

## So, I built one.

<br>

# 🛡 AI Security Reviewer

<br>

<div class="small">Review SDD apps, with an SDD-built app.</div>

</div>

---

<!-- スライド7: エンディング -->
<!-- _backgroundColor: #0a0a0a -->
<!-- _color: #ffffff -->

<div class="center">

# AI Security Reviewer

<br>

## Review SDD apps,
## with an SDD-built app.

<br>
<br>

<div class="small">github.com/dentsusoken/ai-security-reviewer</div>

</div>
