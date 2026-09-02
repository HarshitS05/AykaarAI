# 🇮🇳 AaykarAI — Your Autonomous Income Tax Agent

> An AI agent that actually understands Indian income tax — not a chatbot that guesses at deductions, but an agent that computes them right, every time.

[![Live Demo](https://img.shields.io/badge/Live-aaykarai.streamlit.app-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://aaykarai.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/LLM-Llama%203.3%2070B%20via%20Groq-F55036?style=flat)](https://groq.com/)

**🔗 Try it live: [aaykarai.streamlit.app](https://aaykarai.streamlit.app)**

---

## 🤖 What Is This?

AaykarAI is an **autonomous AI agent** built to navigate one of the most notoriously confusing domains in India: income tax filing. It doesn't just answer tax questions — it reasons through your financial situation, runs the actual calculations, and tells you exactly where you stand.

The agent handles:
- **LTCG / STCG** (Long-term & Short-term Capital Gains) computation
- **Old vs. New Tax Regime** comparison — so you know which one actually saves you money
- **HRA and 80C deductions**
- **ITR form recommendation** — tells you which form you should be filing

---

## 🧠 The Agent Architecture

AaykarAI runs on **Groq's Llama 3.3 70B** for reasoning and conversation — but here's the key design decision: **all actual tax math is deterministic Python, not LLM tool-calling.**

Early builds relied on the LLM calling out to tax-calculation functions directly, but this kept producing malformed function calls — unacceptable when the output is someone's tax liability. So the architecture was rebuilt around a clean separation:

- **The LLM agent** understands intent, gathers financial details conversationally, and decides *what* needs to be calculated
- **Deterministic Python logic** does the actual computation — no hallucinated numbers, no rounding errors, no ambiguity

This split is what makes AaykarAI trustworthy enough to hand real tax questions to, instead of just another LLM wrapper guessing at slab rates.

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Reasoning / Agent | Groq — Llama 3.3 70B |
| Tax Logic | Python (deterministic, rule-based) |
| Interface | Streamlit |
| Deployment | Streamlit Cloud |

---

## ⚡ Quick Start

```bash
git clone https://github.com/HarshitS05/AaykarAI.git
cd AaykarAI
pip install -r requirements.txt
streamlit run app.py
```

Or just use the hosted version: **[aaykarai.streamlit.app](https://aaykarai.streamlit.app)**

---

## 🏆 Recognition

AaykarAI was submitted to **VibeCon** (a YC-affiliated hackathon) and a **Codex program**, alongside [EstateBot](#).

---

## 🔭 Why This Matters

Indian tax filing is a maze of regimes, deductions, and form types that trips up even financially literate people. AaykarAI's bet is simple: an agent that reasons *and* computes correctly beats a chatbot that sounds confident but gets the math wrong.

---

## 🤝 Connect

Built by **Harshit** — MIT Manipal · building AI products for the Indian market.
