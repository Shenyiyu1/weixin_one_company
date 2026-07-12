# -*- coding: utf-8 -*-
"""Replace Chinese text in article.html with English translations."""
import re
from bs4 import BeautifulSoup

with open('zhihu_article_2045918254108095918_en/article.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# ── Translation mapping: (selector, old_text_pattern) -> new_text ──
# We match by traversing text-bearing elements and replacing their string content.

# For simplicity, we'll directly walk all tags and replace text in translatable elements.
# But since some elements contain mixed content (spans, links, etc.), we need to be careful.

# Instead, let's use a tag-by-tag approach: find all p, li, blockquote, th, td, h1-h4, title
# and replace their text content if it matches Chinese text.

translations = {
    # ── Title & headings ──
    'title': {
        '【Part-1】【OPD综述】三万字长文精讲 2026 上半年的 On-Policy Distillation':
        '[Part-1] [OPD Survey] A 30,000-Word Deep Dive into On-Policy Distillation in H1 2026',
    },
    'h1': {
        '【Part-1】【OPD综述】三万字长文精讲 2026 上半年的 On-Policy Distillation':
        '[Part-1] [OPD Survey] A 30,000-Word Deep Dive into On-Policy Distillation in H1 2026',
    },

    # ── Section: 写在前面的前面 ──
    'h2': {
        '写在前面的前面': 'Before We Begin',
        '0. 写在前面：OPD 为什么 2026 上半年火的一塌糊涂': '0. Preface: Why OPD Exploded in H1 2026',
        '1. OPD 是什么：': '1. What Is OPD?',
        '2. OPD总谱系图': '2. OPD Genealogy Map',
    },

    'blockquote': {
        '本文是一篇个人整理的 OPD（On-Policy Distillation）方向 mini-survey，覆盖 2026-01 ~ 2026-05 上 arXiv 的大概40多篇OPD 相关论文（其中 14 篇是我之前一篇篇精读过的，并在了我的专栏中。另外 大概30篇是为这篇 survey 重新检索 + 粗读后总结的）。目标读者：刚听说 OPD、想搞懂它在干嘛、想从这一波论文里找研究 gap 的同学。写作原则：所有insight都尽可能挂原文原文；abstract 没说的细节不写。':
        'This is a personal mini-survey on OPD (On-Policy Distillation), covering roughly 40+ OPD-related papers posted on arXiv from 2026-01 to 2026-05 (of which 14 I have previously read in depth and covered in my column; the remaining ~30 were re-searched and skimmed for this survey). Target audience: those who have just heard of OPD, want to understand what it does, and are looking for research gaps in this wave of papers. Writing principle: all insights are tied to original papers wherever possible; details not mentioned in abstracts are not included.',

        '主要是为了方便将现有大量的OPD工作归类，根据它们要解决的问题，我粗浅的分成了6个分支，每个分支都在尝试解决OPD的一个核心问题':
        'Primarily to facilitate categorizing the large volume of existing OPD work. Based on the problems they aim to solve, I have roughly divided them into 6 branches, each attempting to address a core problem in OPD.',

        '毕竟OPD很火，论文每天怎么着也得出几篇。写这章的目的，其实就是想让大家在读完任意一篇OPD的论文后，都能根据它核心设计的不同，将其咱们这个有四个正交轴的OPD坐标系中；':
        'After all, OPD is hot — several papers come out every day. The purpose of this chapter is to enable readers, after reading any OPD paper, to place it into our four-axis OPD coordinate system based on its core design differences.',
    },

    # ── Intro paragraphs ──
    'p': {
        '综述的全部link见下面：综述的全部link见下面：': 'All links to the survey are below:',

        '针对26年上半年OPD工作的mini-survey 已经基本上写完了，目前大体分为六个，分别是：':
        'The mini-survey on H1 2026 OPD work is essentially complete. It is broadly divided into six parts:',

        '第0章：写在前面：OPD 为什么 2026 上半年火的一塌糊涂':
        'Chapter 0: Preface — Why OPD Exploded in H1 2026',

        '第1章：OPD是什么': 'Chapter 1: What Is OPD?',

        '第2章：OPD总谱系图': 'Chapter 2: OPD Genealogy Map',

        '第3章：OPD工作的六个分支（可能要分成好几篇来讲了，从第二篇开始讲）':
        'Chapter 3: The Six Branches of OPD Work (likely split across multiple posts, starting from Part 2)',

        '第4章：建立OPD论文的坐标系（准备留到后续再讲）':
        'Chapter 4: Building a Coordinate System for OPD Papers (planned for a later post)',

        '第5章：【个人看法】OPD还有的几个gap（准备留到后续再讲）':
        'Chapter 5: [Personal View] Remaining Gaps in OPD (planned for a later post)',

        '第6章：总结（准备留到后续再讲）':
        'Chapter 6: Conclusion (planned for a later post)',

        '整个mini-survey的第一版写完后统计了下有三万多字，感觉写成一篇就太冗长了。所以，准备是搞成三至四篇blog。这个算是第一篇吧～':
        'After completing the first draft of this mini-survey, I counted over 30,000 characters — too long for a single post. So I plan to split it into three to four blog posts. This is the first one.',

        '第一篇就先入个门写以下三个章节吧':
        "Let's start with the following three chapters as an introduction:",

        '先看一组数字。我在 arXiv 上拉了 2026-01-01 到 2026-05-31 的 OPD / on-policy self-distillation /reverse KL distillation/ rubric distillation 相关论文，去掉一些挂着OPD的名字但明显关系不大的文章外，最终有 43 篇。':
        "Let's look at some numbers. I pulled OPD / on-policy self-distillation / reverse KL distillation / rubric distillation papers from arXiv between 2026-01-01 and 2026-05-31. After removing papers that mention OPD in name only but are clearly unrelated, the final count is 43.",

        '其中，5月单月就18 篇了。OPD 已经从"知识蒸馏的一个变种"被推上了"LLM post-training的主线工具"位置。':
        'Of these, 18 papers appeared in May alone. OPD has been elevated from "a variant of knowledge distillation" to "a mainstream tool for LLM post-training."',

        '腾讯在4 月 1 日（第一版arxiv是这个时间点挂上去的，后续还有几版更新）挂出了第一篇 OPD 专项 survey[A Survey of On-Policy Distillation for Large Language Models]，70-80 页大部头，覆盖了从 2023GKD/MiniLLM 到 2026 春的全部主线。再加上Thinking Machines Lab2025-10 那篇被广泛转发的工程介绍（也是中文圈很多人接触 OPD 的入门读物，转载于微信"On-Policy Distillation 深度剖析"），整个领域在 2026 春进入了"定义清晰、工具收敛、应用爆发"的阶段。':
        'Tencent posted the first dedicated OPD survey [A Survey of On-Policy Distillation for Large Language Models] on April 1 (first arXiv version, with subsequent updates), a 70-80 page tome covering everything from 2023 GKD/MiniLLM through spring 2026. Combined with Thinking Machines Lab\'s widely-shared engineering introduction from 2025-10 (the entry point for many in the Chinese community to OPD, republished on WeChat as "On-Policy Distillation Deep Dive"), the field entered a phase of "clear definitions, converging tools, and exploding applications" by spring 2026.',

        '这篇 blog 想做的事：': 'What this blog aims to do:',

        '这篇 blog 不想做的事：': 'What this blog does NOT aim to do:',

        'OPD 的关键定义性特征只有两条：':
        'OPD has only two key defining characteristics:',

        '个人理解，满足这两条的训练都叫 OPD，剩下所有东西都是在OPD基础上的变种：':
        'In my understanding, any training that satisfies these two criteria is called OPD. Everything else is a variant built on top of OPD:',

        'LLM post-training 的所有方法，本质上都可以用一个三元组描述，也就是：( 谁来生成训练 trajectory , 谁来打分 , 打分粒度 )；':
        'All LLM post-training methods can essentially be described by a triple: (who generates the training trajectory, who scores it, and at what granularity).',

        '把这个三元组填一下：': "Let's fill in this triple:",

        '符号约定（全文统一）：': 'Notation conventions (consistent throughout):',

        'OPD 默认用的是Reverse KL（RKL）：': 'OPD uses Reverse KL (RKL) by default:',

        '注意期望是按student 自己的分布πθ取的——这是 "on-policy" 的来源（rolloutyS∼πθ(⋅∣x)）。':
        'Note that the expectation is taken w.r.t. the student\'s own distribution πθ — this is where "on-policy" comes from (rollout y^S ∼ πθ(·|x)).',

        '对比Forward KL（FKL）：': 'Compare with Forward KL (FKL):',

        '期望按 teacher 的分布πt取。这是经典 KD 用的散度。':
        'The expectation is taken w.r.t. the teacher\'s distribution πt. This is the divergence used in classical KD.',

        '两者的本质区别用一句话讲：reverse KL 是 mode-seeking（学生不去管 teacher 那些它根本到不了的小概率分支，专心模仿 teacher 的主峰），forward KL 是 mode-covering（学生被强迫把 teacher 所有可能的输出都覆盖到，哪怕代价是把概率涂得很平）。想看更详细的分析，可以参考这篇blog【概念讲解】Off-Policy + On-Policy 两段式蒸馏':
        'The essential difference in one sentence: reverse KL is mode-seeking (the student ignores low-probability branches of the teacher that it can never reach, focusing on imitating the teacher\'s main modes), while forward KL is mode-covering (the student is forced to cover all possible teacher outputs, even at the cost of spreading probability mass too thin). For a more detailed analysis, see this blog post: [Concept Explainer] Off-Policy + On-Policy Two-Stage Distillation.',

        '在 LLM 大词表 + teacher-student capacity gap 大的场景里，RKL 几乎一边倒赢。这2026年之前的行业公式吧，也是[Diversity-Aware RKL]在 2026-03-31 的 abstract 里再次复述的事实："RKL has recently emerged as the preferred objective for LLM distillation, consistently outperforming FKL"。':
        'In the LLM setting with large vocabularies and a significant teacher-student capacity gap, RKL wins almost unilaterally. This was already the industry consensus before 2026, and [Diversity-Aware RKL] reiterated this fact in its abstract on 2026-03-31: "RKL has recently emerged as the preferred objective for LLM distillation, consistently outperforming FKL."',

        '但 RKL 也有自己的病：mode-seeking 推到极致就是 mode collapse，student 学到只输出 teacher 主峰的几条路径，多样性塌掉。这就引出了 2026 上半年第一类高频工作：散度本身的修正（DRKL / EOPD 等，在 §3.1 讲）。':
        'But RKL has its own disease: mode-seeking pushed to the extreme becomes mode collapse — the student learns to output only a few paths from the teacher\'s main modes, and diversity collapses. This leads to the first category of high-frequency work in H1 2026: corrections to the divergence itself (DRKL / EOPD, etc., covered in §3.1).',

        '整段伪代码就这么短。所有 2026 上半年的 OPD 论文，绝大多数改的都是这段代码里的一部分：':
        'The entire pseudocode is this short. The vast majority of OPD papers in H1 2026 modify some part of this code:',

        '这就是 OPD 系列工作的整体格局。': 'This is the overall landscape of OPD work.',

        '一句话记住 OPD："student 自己写答案、teacher 在每个 token 位置打分、用打分梯度往 teacher 那边拉。"':
        'Remember OPD in one sentence: "The student writes its own answers, the teacher scores at every token position, and the scoring gradients pull the student toward the teacher."',

        '下面这张图是整个mini-survey 的roadmap，后面章节都围着它转。⭐ = 我之前精读过并写过单独笔记的 14 篇，详情见下面的那个专栏；其余 29 篇是粗读后的论文。':
        'The figure below is the roadmap for this entire mini-survey; all subsequent chapters revolve around it. ⭐ = 14 papers I previously read in depth and wrote individual notes on (see the column below for details); the remaining 29 were skimmed for this survey.',
    },

    # ── List items ──
    'li': {
        '第0章：写在前面：OPD 为什么 2026 上半年火的一塌糊涂':
        'Chapter 0: Preface — Why OPD Exploded in H1 2026',

        '第1章：OPD是什么': 'Chapter 1: What Is OPD?',

        '第2章：OPD总谱系图': 'Chapter 2: OPD Genealogy Map',

        '把 OPD 是什么用最少的公式 + 一张图讲清楚（不假设你读过 GKD/MiniLLM）。':
        'Explain what OPD is with minimal formulas + one diagram (no prior knowledge of GKD/MiniLLM assumed).',

        '把 2026 上半年这 43 篇按"治什么病"切成六个流派，每派挑代表作讲 trick。':
        'Slice the 43 H1 2026 papers into six schools by "what problem they solve," picking representative works from each to explain their tricks.',

        '抽出 4 条横贯所有论文的设计轴，画一张大对比表，让你能把任意一篇新 OPD 论文塞进坐标系。':
        'Extract 4 design axes that cut across all papers, draw a large comparison table, so you can place any new OPD paper into this coordinate system.',

        '谈一谈这半年没人真正解决的 3 个 gap——如果你在找研究方向，可以从这里下手。':
        'Discuss 3 gaps that no one has truly solved in this half year — if you are looking for a research direction, start here.',

        '堆数字（实验结果只在必要时引用）': 'Piling up numbers (experimental results cited only when necessary).',

        '复述 abstract（每个 trick 都尽量讲"它解决什么、怎么解、为什么这样解"）':
        'Paraphrasing abstracts (each trick is explained in terms of "what it solves, how it solves it, and why this approach works").',

        '拍马屁夸某篇论文。': 'Flattering any particular paper.',

        'on-policy：训练数据是 student 自己采样生成的 trajectory，不是 teacher 预先生成的（这一条把 OPD 和经典 KD/SFT 区分开）。':
        'on-policy: the training data consists of trajectories sampled by the student itself, not pre-generated by the teacher (this separates OPD from classical KD/SFT).',

        'token-level dense supervision：每个 token 位置上算 student 的概率分布和 teacher 的概率分布之间的散度（这一条把 OPD 和 RL 区分开——RL 只在 trajectory 末尾或稀疏位点给 reward）。':
        'token-level dense supervision: at every token position, compute the divergence between the student\'s probability distribution and the teacher\'s probability distribution (this separates OPD from RL — RL only provides rewards at the end of the trajectory or at sparse positions).',

        'teacher可以是固定的、可以是 EMA 的、可以是同一个模型加 prompt 偏置的、可以是黑盒 API、可以是 rubric；':
        'The teacher can be fixed, EMA-based, the same model with prompt bias, a black-box API, or a rubric.',

        '散度可以是 reverse KL、forward KL、JS、token-level entropy；':
        'The divergence can be reverse KL, forward KL, JS, or token-level entropy.',

        '监督密度可以是 full rollout、prefix-only、entropy-gated。':
        'The supervision density can be full rollout, prefix-only, or entropy-gated.',

        'student policy 写作πθ（参数θ）；': 'student policy is denoted as πθ (parameter θ);',
        'teacher policy 写作πt；': 'teacher policy is denoted as πt;',
        'prompt 写作x；': 'prompt is denoted as x;',

        'student 自己 rollout 出的样本写作yS∼πθ(⋅∣x)，teacher rollout 出的样本写作yT∼πt(⋅∣x)；':
        'samples from student rollout are denoted as y^S ∼ πθ(·|x), and samples from teacher rollout as y^T ∼ πt(·|x);',

        'token 位置索引写作i，第i个 token 写作yi，之前生成的结果（即"state"）写作y<i=(y1,…,yi−1)。token 级条件分布写作πθ(yi∣x,y<i)，求和指标yi遍历词表V。':
        'the token position index is denoted as i, the i-th token as yi, and the previously generated result (i.e., the "state") as y_{<i} = (y1, ..., y_{i-1}). The token-level conditional distribution is denoted as πθ(yi | x, y_{<i}), where the summation index yi runs over the vocabulary V.',

        '有的工作是改第 1 步：teacher 怎么生 trajectory。比如：黑盒 / rubric / privileged context / best-of-N rollout selection；':
        'Some works modify Step 1: how the teacher generates trajectories. Examples: black-box / rubric / privileged context / best-of-N rollout selection.',

        '有的工作是改第 2 步：teacher 是谁。比如：固定 / EMA / 周期硬拷贝 student / 同模型加 prompt / 另一个领域专家；':
        'Some works modify Step 2: who the teacher is. Examples: fixed / EMA / periodic hard-copy of student / same model with a prompt / another domain expert.',

        '有的工作是改第 3 步：散度怎么选。比如：RKL / FKL / 按 entropy gate / DRKL / clipping':
        'Some works modify Step 3: which divergence to use. Examples: RKL / FKL / entropy-gated / DRKL / clipping.',

        '最后还有的工作改"哪些 token 算 loss"。比如：full rollout / prefix-only / entropy mask / advantage weighted 这些点；':
        'Finally, some works modify "which tokens contribute to the loss." Examples: full rollout / prefix-only / entropy mask / advantage weighted.',

        '如果说，SFT 是别人写答案 student 抄；':
        'If SFT is someone else writing the answer and the student copying it,',

        'RL 是 student 写完一篇拿一个总分（reward）；':
        'and RL is the student writing an essay and getting a single total score (reward),',

        '那OPD 卡在两者中间，student 写答案 + 每个 token 都打分；':
        'then OPD sits between the two: the student writes the answer + every token gets scored.',
    },

    # ── h3 headings ──
    'h3': {
        '1.1SFT/ RL / OPD 三者的本质差别': '1.1 The Essential Differences Between SFT, RL, and OPD',
        '1.2 Reverse KL vs Forward KL：OPD 的分水岭': '1.2 Reverse KL vs Forward KL: The Watershed of OPD',
        '1.3 一份最简 vanilla OPD 伪代码': '1.3 Minimal Vanilla OPD Pseudocode',
    },

    # ── Table cells ──
    'th': {
        '方法': 'Method',
        '生成 trajectory': 'Generates Trajectory',
        '打分者': 'Scorer',
        '粒度': 'Granularity',
    },

    'td': {
        'teacher / 人': 'Teacher / Human',
        '假定每步都对': 'Assumes every step is correct',
        'token-level，但每个 token 等权重': 'Token-level, but equal weight per token',
        'RL（如 GRPO）': 'RL (e.g., GRPO)',
        'student 自己': 'Student itself',
        '序列级稀疏 reward：整条 rollout 给一个 scalar reward R，通过 advantage 反传到每个 token，但 reward 信号本身只有一个标量':
        'Sequence-level sparse reward: a single scalar reward R for the entire rollout, back-propagated to each token via advantage, but the reward signal itself is just one scalar.',
        'teacher 模型的 logit 分布': "Teacher model's logit distribution",
        'token-level dense supervision：每个 token 位置上独立计算 student 和 teacher 分布之间的 KL':
        'Token-level dense supervision: independently compute the KL divergence between student and teacher distributions at every token position.',
    },
}

# ── Apply translations ──
count = 0
for tag_name, mapping in translations.items():
    for el in soup.find_all(tag_name):
        # Skip code/pre children
        if el.find_parent('pre') or el.find_parent('code'):
            continue
        # Get the full text of this element
        text = el.get_text(strip=True)
        for old_text, new_text in mapping.items():
            if old_text == text:
                # Replace the text content while preserving inner HTML structure
                # Find the text node(s) and replace
                for child in el.descendants:
                    if isinstance(child, str) and old_text.strip() in child.strip():
                        # For simple cases where the element contains only this text
                        pass
                # Simpler approach: if the element's stripped text matches, replace the first text node
                if el.string and el.string.strip() == old_text:
                    el.string = new_text
                    count += 1
                    break
                # For elements with mixed content (text + child tags), use string replacement on HTML
                elif el.string is None and el.get_text(strip=True) == old_text:
                    # More complex: need to find which text node holds the content
                    # For now, do inner text replacement
                    for child in list(el.children):
                        if isinstance(child, str) and old_text in child:
                            child.replaceWith(new_text)
                            count += 1
                            break
                    else:
                        # Fallback: replace the entire inner content
                        # This might lose HTML structure but works for simple cases
                        pass
                break
            elif old_text in text and len(old_text) > len(text) * 0.5:
                # Partial match - text contains old_text as a significant portion
                # Try to replace in text nodes
                for child in list(el.children):
                    if isinstance(child, str) and old_text in child:
                        child.replaceWith(child.replace(old_text, new_text))
                        count += 1
                        break

print(f'Applied {count} translations')

with open('zhihu_article_2045918254108095918_en/article.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
print('Done!')
