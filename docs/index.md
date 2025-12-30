---
layout: home

hero:
  name: "DeepTutor"
  text: "AI-Powered Personalized Learning"
  tagline: Multi-Agent Architecture for Adaptive Education with Knowledge Graph Integration
  image:
    src: /logo.png
    alt: DeepTutor
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/HKUDS/DeepTutor

features:
  - icon: 📚
    title: Massive Document Q&A
    details: Upload textbooks, papers, and manuals. Build AI-powered knowledge repositories with RAG and knowledge graph integration.
  - icon: 🎨
    title: Interactive Visualization
    details: Transform complex concepts into visual aids with step-by-step breakdowns and engaging interactive demonstrations.
  - icon: 🧠
    title: Smart Problem Solver
    details: Dual-loop reasoning with RAG, web search, paper search, and code execution for step-by-step solutions.
  - icon: 🎯
    title: Practice Generator
    details: Generate targeted quizzes and practice problems. Upload reference exams to mimic original style and difficulty.
  - icon: 🔬
    title: Deep Research
    details: Comprehensive topic exploration with systematic analysis, literature review, and novel insight discovery.
  - icon: 💡
    title: Idea Generation
    details: Automated and interactive concept development with multi-source insights and novelty evaluation.
---

## Why DeepTutor?

DeepTutor transforms how students interact with educational materials through a unified multi-agent architecture. Unlike traditional tools, it provides:

- **Deep Understanding** - Not just answers, but guided learning journeys with visual explanations
- **Multi-Modal Support** - PDF, LaTeX, images, code execution, and more
- **Knowledge Graph** - Semantic connections powered by LightRAG for better comprehension
- **All-in-One Platform** - Problem solving, question generation, research, and idea generation

## Quick Demo

```bash
# Clone and setup
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor

# Install dependencies
bash scripts/install_all.sh

# Start the application
python scripts/start_web.py
```

<style>
:root {
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: -webkit-linear-gradient(120deg, #bd34fe 30%, #41d1ff);
}
</style>
