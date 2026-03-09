COMMENTS COLLECTION

reviewer 1:
这是一份基于 ACL ARR 评分标准，针对该论文前三章（摘要、引言、相关工作、方法）的顶尖学术审稿人意见：

### 1. Paper Summary (论文摘要)
本文提出了一种名为 **DeepTutor** 的个性化智能辅导系统（Agentic Tutoring System）。该系统首次将工具增强的问题解答（Problem-Solving）与难度校准的问题生成（Question Generation）整合到一个闭环的交互过程中。其核心创新在于提出了“混合个性化引擎（Hybrid Personalization Engine）”，该引擎结合了静态知识增强（多模态 RAG）和动态个人记忆（Trace Forest）。通过记录多分辨率的交互轨迹，系统能够持续更新包含会话历史、用户弱点和系统自省的三个维度的学习者画像，从而实现问题解答与问题生成之间的双向任务耦合。

### 2. Summary of Strengths (主要优点)
1. **创新的闭环框架 (Novel Closed-Loop Framework)**：将“解题”和“出题”通过共享的记忆结构（Trace Forest）连接成闭环，这一设计非常符合真实的教育学原理。以往的工作大多孤立地处理这两个任务，本文的统一架构具有很高的启发性。
2. **精细化的记忆机制 (Comprehensive Memory Design)**：Trace Forest 的层次化设计（从会话级总结到细粒度的执行记录）以及三维度的学习者画像（$\mathcal{D}_s, \mathcal{D}_w, \mathcal{D}_r$）有效克服了现有系统仅依赖粗粒度技能评分的缺陷，为 LLM 提供了丰富的个性化上下文。
3. **鲁棒的模块化流水线 (Robust Pipeline Architecture)**：方法部分对解题（调查-逐步求解-迭代写作）和出题（对抗式生成-验证）的拆解非常合理。特别是引入了层次化压缩（Hierarchical compression）来防止上下文窗口溢出，以及独立的验证器（Validator）来减少幻觉，这些工程设计都非常扎实。

### 3. Summary of Weaknesses (主要缺点)
1. **Trace Forest 的技术细节略显不足 (Lack of Detail in Trace Forest)**：虽然 Trace Forest 的概念很吸引人，但方法部分对其具体实现（如：节点嵌入 $\mathbf{e}_v$ 是如何生成和更新的？TraceToolkit 的 \textsc{SearchTrace} 是基于什么相似度度量？）描述不够具体，可能会影响复现性。
2. **“对抗式”术语的使用可能被夸大 (Overstated Terminology)**：在 2.4 节（Stage 4）中，作者使用了“Adversarial Q-A Pair Generation”。但从描述来看，这更像是一个标准的“生成-验证-反馈-修改”（Generate-and-Verify with Feedback）流水线，并没有体现出博弈论意义上的对抗训练。建议修改术语或进一步澄清其对抗性体现在何处。
3. **计算开销与延迟的考量缺失 (Complexity and Latency Concerns)**：系统包含多个 LLM Agent、多模态 RAG、代码沙箱执行以及复杂的记忆更新机制。对于一个“实时交互式”辅导系统而言，推理延迟和计算成本是致命的。方法部分完全没有讨论系统在实际运行中的效率问题。
4. **图表与算法的对应关系 (Formatting and Flow)**：Algorithm 1 非常密集，包含了大量符号（如 $\mathcal{I}, \mathcal{T}_i, f_i$），虽然在正文中有所提及，但读者在阅读算法伪代码时仍会感到吃力。

### 4. Comments/Suggestions/Typos (详细意见/建议/拼写错误)
*   **Abstract**: 第73行 "They are unified through..." 中的 "They" 指代略显模糊，建议改为 "These two tasks are unified..."。同句中 "trace forest that continuously refines" 建议加冠词改为 "a trace forest that..."。
*   **Introduction**: 第11行 "An effective human tutor does far more than supply correct answers--it diagnoses..." 使用 "it" 来指代 human tutor 不太自然，建议改为 "they diagnose" 或 "he/she diagnoses"。
*   **Method (Section 2.2.1)**: 在介绍倒数秩融合（Reciprocal Rank Fusion）时，公式是标准的，但建议简要补充图检索（Graph-based retrieval）是如何对其候选节点进行初始排序（$\mathrm{rank}_r(d)$）的。
*   **Method (Section 2.3)**: Stage 1 提到“investigating before planning prevents sub-goals that are too vague”。这是一个非常好的洞察！强烈建议在这里用半句话补充一个具体的例子（例如：“相比于生成‘复习微积分’，系统会生成‘复习链式法则在三角函数中的应用’...”），这会大大增强文章的表达力。

### 5. Soundness (合理性评分及评价)
**评分: 4 (Strong)**
**评价**: 该研究的动机明确，方法设计逻辑严密，特别是在教育学理论（如诊断误区、支架式解释）与 LLM Agent 架构的结合上做得非常出色。如果能进一步补充关于检索排序细节和系统延迟的讨论，合理性将无可挑剔。

### 6. Excitement (兴奋度评分及评价)
**评分: 4.5 (Highly Exciting/Exciting)**
**评价**: 这是一篇令人兴奋的论文。将大模型应用于教育领域的痛点抓得很准，Trace Forest 和闭环反馈机制的设计为个性化 AI 导师提供了一个极具潜力的范式。我非常期待看到后续的实验结果（TutorBench）如何证明这一复杂系统的有效性。

### 7. Overall Assessment (总体评价)
**评分: 4 (Conference - Accept)**
**评价**: 仅从前三章来看，本文具备被顶级会议（如 ACL/EMNLP）接收的强大潜力。文章结构清晰，插图精美（Figure 1 和 Figure 2 质量很高），核心贡献（DeepTutor 框架和 Trace Forest）具有显著的创新性。建议作者在修改时重点提升方法细节的透明度（尤其是记忆检索机制），并适当降温部分略显夸大的术语（如 Adversarial）。


reviewer 2:
## 主要问题
1. **核心新颖性主张偏强，但在前三章范围内没有被充分论证。** 摘要和引言都使用了 `the first` 级别的表述，但当前我看到的前三章还没有给出足够严谨的任务分解、系统边界定义，或与现有 personalized tutoring / agentic RAG / question generation 系统的逐项对比，因此这类 claim 在 ARR 里会很容易被审稿人质疑为“过度宣称”。

```72:76:paper/main.tex
In this paper, we present \textsc{DeepTutor}, the first personalized agentic tutoring system with both citation-grounded problem-solving and difficulty-calibrated question generation.
They are unified through a hybrid personalization engine that couples static knowledge grounding with trace forest that continuously refines an evolving learner profile to customize every interaction.
To further evaluate personalized tutoring abilities, we construct TutorBench, a benchmark containing 100 KB-grounded learner profiles to perform first-person interactive assessments via profile-driven student simulator. 
Generalization experiments on five standard benchmarks further show that our reasoning pipeline lifts solving accuracy by approximately 25\% on average over the backbone model. 
\textsc{DeepTutor} system with full evaluation suites are open-sourced at \url{https://github.com/HKUDS/DeepTutor/tree/eval}.
```

```27:31:paper/sections/intro.tex
\begin{itemize}[nosep,leftmargin=*]
  \item We propose \textsc{DeepTutor}, an agentic tutoring framework that, to the best of our knowledge, is the first to unify tool-augmented problem solving, adversarial question generation, and long-term structured memory into a closed interactive loop.
  \item We introduce \textit{trace forest}, a hierarchical memory architecture in which specialized agents collaboratively maintain a fine-grained, evolving learner model from multi-resolution interaction traces.
  \item We construct \textsc{TutorBench}, a benchmark of 100 knowledge-base-grounded learner profiles paired with a student simulator for first-person interactive evaluation. Experiments on TutorBench and five standard reasoning benchmarks show that \textsc{DeepTutor} substantially outperforms various baselines, providing insights for the future shape of personalized tutoring systems.
\end{itemize}
```

2. **方法章节目前更像“系统蓝图”，还不够像可复现、可验证的研究方法。** `paper/sections/method.tex` 引入了大量模块：KG、VDB、Trace Forest、memory agents、planner、tool agent、writer、generator、validator，但多数仍停留在概念级描述。对 ACL ARR 来说，这会直接拉低 `Soundness` 和 `Reproducibility`，因为读者仍不清楚关键设计到底是什么、哪些是必要创新、哪些只是工程组合。

```111:124:paper/sections/method.tex
\paragraph{Profile Construction.}
\label{sec:injection}
Raw traces must be interpreted into actionable tutoring signals.
We introduce three specialized memory agents to process each new trace tree $T_j$ in parallel, incrementally updating a dedicated dimension of the learner profile $\mathcal{D}$:
\begin{itemize}[nosep,leftmargin=*]
\item Session History $ \mathcal{D}_s$: distills topics covered and performance trends. This will record what has happened, providing general session memories.
\item User Weakness $\mathcal{D}_w$: compares learner responses against reference solutions, labeling each weakness as active or resolved to maintain a prioritized gap inventory, emphasizing where to focus.
\item Self-Reflection $\mathcal{D}_r$: critiques the system's own prior outputs for pedagogical alignment, producing actionable improvement notes, indicating how to improve.
\end{itemize}
Each agent receives the new trace along with its current profile dimension and produces an updated version through incremental revision, preserving long-term trends while incorporating recent signals.
```

3. **个性化记忆机制存在“错误累积/自我强化”风险，但当前方法没有给出足够防护。** 你们让系统把历史交互、弱点诊断、甚至 tutor 自反思都写回 profile；这很有想法，但也意味着一旦前序判断有误，系统可能反复读取并放大错误 learner model。尤其 `Self-Reflection` 与 `User Weakness` 都可能受到模型幻觉影响，前三章里尚未看到 confidence gating、conflict resolution、time decay、human-grounded correction 等机制。

4. **“闭环个性化 tutoring” 的核心科学命题没有被形式化。** 引言里最重要的论点是“解题暴露出的弱点应影响后续出题，而后续表现又应反向更新讲解方式”；这是一个很强、也很值得发表的命题。但在 `paper/sections/intro.tex` 和 `paper/sections/method.tex` 里，这个命题更多是叙事上的闭环，而不是可测量、可证伪的机制。比如：difficulty calibration 如何定义？学习者水平如何估计？“更个性化”到底对应什么客观指标？如果这些不清晰，审稿人会认为贡献更多是系统工程而非研究贡献。

5. **摘要与引言的写作尚不够“ARR-ready”。** 当前文本可读性总体不错，但摘要里有几处句法和指代不够稳，例如 `They are unified...` 的指代模糊，`trace forest that continuously refines...` 的语法不够顺，`lifts solving accuracy by approximately 25% on average` 又是一个非常重的结果性 claim，却没有在摘要中限定 benchmark、setting、baseline 类型。顶会审稿人通常会把这类问题视为“论证不够谨慎”。

## 综合审稿意见
如果我以 **ACL ARR 审稿人** 的角度、且**只基于摘要 + 引言 + 方法** 来打一个暂定印象分，这篇工作属于：

- **选题很强，方向很对，潜在影响力也不错。**
- **系统构想完整，问题意识清晰，`problem solving + question generation + memory` 的统一视角是最有价值的点。**
- **但目前前三章最大的问题是：claim 很大，方法写法偏概念化，关键科学问题还没有被足够“钉实”。**

按 ARR 口径，我会给出一个**暂定**判断：

- `Reviewer Confidence`: **3/5**
- `Soundness`: **2.5/5**
- `Excitement`: **3.5/5**
- `Overall Assessment`: **2.5/5 到 3/5 之间**
- 更具体地说：**如果后续实验和消融非常扎实，有机会到 Findings；如果实验对这些核心机制支撑不够，这篇会更像“下轮重投”。**

## 改进方法
1. **把 novelty claim 收紧。** 除非你们能在 related work 里做非常系统的排他性对比，否则建议把 `the first` 改成更稳健的表述，例如 `among the first`, `to our knowledge, one of the first`, 或者直接强调“we unify ... in a closed-loop tutoring setting”。

2. **把方法从“架构描述”升级成“研究方法描述”。** 最需要补的是一张总表：每个模块的输入、输出、模型、prompt 角色、调用时机、关键超参、失败条件、停止条件。现在读者知道你们“有这些模块”，但还不知道它们“究竟怎么工作”。

3. **明确 trace forest 的更新规则。** 建议补充：node schema、embedding 粒度、写回频率、profile update policy、冲突样本如何处理、旧信息何时衰减。否则 memory 贡献会显得像一个很好听但难以验证的概念。

4. **把 personalization 变成可操作定义。** 例如显式定义：
   - learner proficiency signal
   - weakness severity
   - question difficulty target
   - explanation adaptation dimensions  
   这样后面实验才能自然对应到“是否真的 personalized”。

5. **提前在方法里写出 failure control。** 我最担心的是 profile drift 和 hallucinated weakness。建议补充一致性校验、低置信度不写回、短期/长期记忆分离、以及基于证据的更新门控。

6. **摘要重写一版。** 顶会论文的摘要最好做到三件事：问题界定单句说清、核心技术单句说清、结果边界单句说清。你现在的摘要信息很多，但密度过高、句法稍乱，容易让审稿人第一印象打折。

## 开放问题
1. `User Weakness` 的标签是由谁产生的？是基于 gold reference、rule-based matching，还是纯 LLM judgment？
2. `Self-Reflection` 为什么应该进入 learner profile，而不是只作为 system-side optimization signal？
3. `difficulty-calibrated` 的标定标准是什么？有外部 rubric、IRT 风格定义，还是模型自评？
4. 闭环收益是来自 `memory`、`tool use`、`RAG`，还是三者交互？如果没有强消融，这一点会被反复追问。

如果你愿意，我下一步可以继续直接按 `ACL ARR Review Form` 的格式，帮你把这份意见整理成一版可直接放进 `paper/REVIEW.md` 的正式审稿文本。

reviewer 3:
明白，我重新聚焦到 **Abstract、Introduction、Related Work、Method** 这四个部分，完全不涉及实验章节。以下是修订后的审稿意见。

---

## 综合审稿意见（范围：Abstract + Intro + Related Work + Method）

### Paper Summary

本文提出 DeepTutor，一个工具增强的个性化辅导系统，将引用溯源的问题求解（problem solving）和难度校准的题目生成（question generation）统一在一个闭环框架中。核心贡献为 Hybrid Personalization Engine，耦合静态知识检索（多模态 KG + 向量数据库）与动态个人记忆（Trace Forest），通过三个专用记忆代理持续更新学习者画像，实现"求解暴露弱点 → 驱动出题 → 出题表现反馈修正解释"的双向耦合循环。

---

### Summary of Strengths

**S1. 问题定位精准，动机论证有力。**
Introduction 中"闭环交互循环"（closed interactive loop）的缺失论证逻辑清晰：现有系统要么单做求解要么单做出题，缺乏将两者通过持久化学习者状态耦合起来的设计。§1 第三段对所需两个条件的提炼——(i) 细粒度结构化记忆、(ii) 模块共享并持续更新该记忆——为后续 Method 的展开提供了很好的铺垫。

**S2. 方法的形式化程度高，架构清晰。**
Algorithm 1 提供了完整的伪代码，涵盖从 profile injection 到 trace forest 更新的全流程。符号体系（$\mathcal{D}$, $\mathcal{F}$, $\mathcal{C}_{\text{mem}}$, $\mathcal{C}_{\text{rag}}$）在 Preliminaries 中统一定义，后续各子模块一致使用，读者可以清晰追踪数据流。

**S3. Trace Forest 的可编程记忆设计有新意。**
三层层次化记忆（Session → Planning → Execution）配合 TraceToolkit（SearchTrace / ListTraces / ReadNodes）的接口设计，将被动数据存储转变为可主动查询的结构化记忆。这比简单的对话历史窗口或 summary buffer 更具灵活性，允许不同 agent 以不同粒度按需检索历史。

**S4. 双向任务耦合（Bidirectional Task Coupling）概念有理论价值。**
§2.5 中描述的求解 → $\mathcal{D}_w$ → 出题 → $\mathcal{D}_s$/$\mathcal{D}_r$ → 解释修正循环，在教育学上对应形成性评估（formative assessment）理论，在 LLM 系统设计中尚属少见。

**S5. 叙述结构层次分明。**
Method 各子节遵循一致的"动机 → 技术描述 → 与整体系统的关联"叙述模式，Figure 2 信息量丰富，能有效帮助读者把握全局。

---

### Summary of Weaknesses

**W1. "First" 声明过强，缺乏系统性论证（Critical）。**

摘要和 Contribution (i) 反复使用 "the first personalized agentic tutoring system" 和 "the first to unify tool-augmented problem solving, adversarial question generation, and long-term structured memory"。这种强排他性声明需要有系统性的文献排查支撑，但 Related Work 仅有三段、共12行，远不足以承担此任务。具体问题：

- **经典 ITS 被忽略**：Cognitive Tutor、AutoTutor、BEETLE II 等系统早已集成了问题生成与求解反馈的闭环，且具有长期学习者建模。Related Work 中完全没有讨论这些工作与 DeepTutor 的区别；
- **近期商业/开源系统被忽略**：Khanmigo（Khan Academy + GPT-4）、Duolingo Max 等系统也做了个性化 + 出题 + 求解的整合，应当明确说明本文与这些系统在架构层面的差异；
- **"First" 的精确范围未定义**：是 first open-source？first with trace-based memory？first with tool-augmented agents？需要限定条件。

**W2. Related Work 过于单薄，无法支撑论文的 positioning（Major）。**

整个 Related Work 只有三个 paragraph（Agentic Tool Use / Personalization and Memory / AI for Education），每段仅 3-4 句。对于一篇声称 "first to unify" 三个方向的论文，这样的文献综述是严重不足的：

- **缺少 ITS（Intelligent Tutoring Systems）方向**：这是教育技术的核心领域，有数十年的研究积累，完全没有被讨论；
- **缺少 Knowledge Tracing 方向**：BKT、DKT、SAINT 等知识追踪模型与 Trace Forest 的学习者建模功能存在功能重叠，需要对比并说明差异；
- **每段的 "DeepTutor fills this gap" 式结尾过于公式化**：三段都以"XXX methods lack Y. DeepTutor addresses this with Z"结尾，缺乏对现有工作优缺点的深入分析。

**W3. Method 中多个核心模块的 novelty boundary 模糊（Major）。**

Method 组合了多个已有技术，但未清晰界定哪些是复用、哪些是本文贡献：

- **Static Knowledge Grounding（§2.2.1）**：多模态 KG 构建引用了 RAGAnything [Guo et al.]，RRF 融合引用了 [Cormack et al., 2009]——这一小节中是否有任何本文特有的技术贡献？如果主要是工程整合，应当明确说明；
- **Step-by-step Solving（§2.3 Stage ②）**：ReAct 循环 + adaptive replanning 与 IterResearch [Chen et al., 2026] 高度相似，self-note 机制是否是本文独有的贡献？需要明确对比；
- **"Adversarial" 用词误导**：Generator-Validator 分离是 "generate-then-validate" 模式，并非真正的对抗训练（adversarial training）。在 NLP 社区中 "adversarial" 有明确的技术含义（如 GANs、adversarial examples），这里的使用可能造成混淆。

**W4. Profile Injection 机制（§2.2 末尾）描述不足，是全文最关键的薄弱点（Major）。**

$\mathcal{C}_{\text{mem}}$ 的组装是连接 Trace Forest 与所有 pipeline agent 的核心桥梁，但描述极为简略：

- "top-$k$ most relevant nodes with $k$ allocated proportionally across levels" — 比例如何确定？$k$ 的具体值是多少？是超参数还是自适应的？
- "role-specific slices of $\mathcal{D}$" — planner 收到 $\mathcal{D}_s + \mathcal{D}_w$，writer 收到 $\mathcal{D}_r$——这种硬编码分配的依据是什么？有无替代方案的讨论？
- Token budget 如何在 $\mathcal{C}_{\text{rag}}$ 和 $\mathcal{C}_{\text{mem}}$ 之间分配？当 context window 紧张时如何取舍？
- 缺少一个端到端的 worked example 展示实际注入的内容。

**W5. Trace Forest 形式化与实现细节之间存在空缺（Moderate）。**

- 节点 embedding $\mathbf{e}_v$ 用什么模型生成？是否与 $\mathcal{B}$（RAG 的向量索引）共享同一编码器？
- SearchTrace 的检索是 ANN 还是精确搜索？复杂度如何？
- 三层层次结构（Level 1/2/3）的设计选择缺乏论证——为什么是三层而非两层或四层？§2.2 末尾说 "concrete node types at each level are task-specific and detailed alongside the respective pipelines"，但 §2.3 和 §2.4 中并没有明确列出各 level 的 node types；
- Forest 的增长管理机制（pruning / compaction）未在 Method 中讨论。

**W6. 三个 Memory Agent 的更新机制缺乏形式化（Moderate）。**

§2.2 列出了 $\mathcal{D}_s$（Session History）、$\mathcal{D}_w$（User Weakness）、$\mathcal{D}_r$（Self-Reflection）三个维度，描述为"incremental revision"，但：
- 这些 agent 的输入输出格式是什么？是自然语言文本还是结构化数据？
- "incremental revision" 的具体机制是什么？是完全重写还是 diff-based 更新？
- 当历史越来越长时，profile 如何避免无限膨胀？
- $\mathcal{D}_w$ 中 "active or resolved" 的状态转换逻辑是什么？

**W7. 摘要中指代不清和衔接问题（Minor）。**

Abstract 第四句 "They are unified through a hybrid personalization engine..." — "They" 的指代对象（citation-grounded problem-solving 和 difficulty-calibrated question generation）需要读者回溯推断，建议改为显式主语。此外，摘要在 RAG 的不足（第三句）和 DeepTutor 的方案（第四句）之间缺乏过渡，读者需要自行建立逻辑跳跃。

---

### Comments / Suggestions / Typos

**结构性改进建议：**

1. **扩充 Related Work 至至少一整页**：增加 ITS 经典系统、Knowledge Tracing、LLM-based educational QG 三个方向的讨论。对每个方向，不仅说"它们缺乏X"，更要分析它们各自的优势，然后说明 DeepTutor 如何在此基础上推进。

2. **在 Method 开头增加 "Design Rationale" 段**：解释为什么采用 investigation-solving-writing 三阶段分离而非端到端推理，并引用教育学理论（如 scaffolding theory、Zone of Proximal Development）。当前 Method 读起来更像系统描述而非研究贡献，增加理论支撑可显著提升深度。

3. **为 Profile Injection 增加 worked example**：用一个具体场景（如"初学者询问反向传播"）展示 $\mathcal{C}_{\text{mem}}$ 的实际内容，包括从 Trace Forest 检索了什么、从 $\mathcal{D}$ 中提取了什么、最终注入 prompt 的格式。

4. **弱化 "first" claim**：改为如 "To our knowledge, DeepTutor is the first *open-source agentic framework* that unifies ... within a single closed-loop architecture" 或类似的有限定条件的表述。

**具体文字修正：**

| 位置 | 问题 | 建议修正 |
|------|------|----------|
| Abstract 第4句 | "They are unified" 指代不清 | → "These two capabilities are unified..." |
| Method §2 开头 | "as shown in figure~\ref{}" | → "Figure" 首字母大写 |
| §2.3 Stage ② | "a ReAct-style loop, ~\citep{}" | → 删除逗号和多余空格："a ReAct-style loop~\citep{}" |
| §2.3 Stage ② | tool suite $\mathcal{A}$ 未正式定义 | 在 Notation 段中增加定义 |
| 全文 | "trace forest" 大小写不一致 | 统一为 "Trace Forest"（专有名词）或 "trace forest"（通用概念），选定一种 |
| Related Work ¶1 | "These frameworks target short-horizon tasks" | 过于笼统，应指出具体哪些 framework |
| Related Work ¶2 | "Yet existing methods rarely maintain pedagogically meaningful learner trajectories" | 需要具体引用说明哪些方法被检查过 |
| Algorithm 1 | 正文引用 "line 14" | 建议改为引用操作名 `Compress` 而非行号，避免重编号后失效 |

---

### 预估评分（仅基于 Abs + Intro + Related Work + Method 的写作与方法论质量）

| 维度 | 评分 | 理由 |
|------|------|------|
| **Soundness** | 3.0 | 系统设计合理但 Profile Injection、Memory Agent 更新机制等核心细节不足；novelty boundary 模糊 |
| **Excitement** | 3.5 | Trace Forest + 闭环耦合概念有新意且有教育学理论基础，但"组合创新"需更清晰地与已有工作区分 |
| **Overall** | 3.0 (Findings) | 方法框架有价值，但 Related Work 过于单薄无法支撑 "first" claim，核心机制描述存在缺口 |
| **Reviewer Confidence** | 4 | 熟悉 RAG、Agent、ITS 及教育 AI 领域 |

---

### 改进路线图（按优先级）

| 优先级 | 改进项 | 影响维度 |
|--------|--------|----------|
| **P0** | 扩充 Related Work，增加 ITS 经典系统 + Knowledge Tracing 讨论，精确化 "first" claim 的边界条件 | Soundness ↑, Overall ↑ |
| **P1** | 明确每个子模块的 novelty boundary（表格形式：模块 / 复用来源 / 本文贡献） | Excitement ↑ |
| **P1** | 补全 Profile Injection 的细节 + worked example | Soundness ↑, Reproducibility ↑ |
| **P2** | 增加 Design Rationale 段，引入教育学理论支撑 | Excitement ↑ |
| **P2** | 补全 Trace Forest 实现细节（embedding 模型、检索算法、层数论证） | Soundness ↑ |
| **P2** | 形式化 Memory Agent 的更新机制 | Soundness ↑ |
| **P3** | 修正术语一致性、typos、"adversarial" 用词 | 专业度 ↑ |