# -*- coding: utf-8 -*-
"""Replace Chinese text in English article HTML using direct string replacement."""
import re

with open('zhihu_article_2045918254108095918_en/article.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Direct string replacements: (old_chinese_text, new_english_text)
# Order matters: longer strings first to avoid partial matches
replacements = [
    # ── Title & meta ──
    ('<title>【Part-1】【OPD综述】三万字长文精讲 2026 上半年的 On-Policy Distillation</title>',
     '<title>[Part-1] [OPD Survey] A Deep Dive into On-Policy Distillation in H1 2026</title>'),

    ('<h1>【Part-1】【OPD综述】三万字长文精讲 2026 上半年的 On-Policy Distillation</h1>',
     '<h1>[Part-1] [OPD Survey] A Deep Dive into On-Policy Distillation in H1 2026</h1>'),

    ('作者: <strong>田雷​</strong>',
     'Author: <strong>Tian Lei</strong>'),

    ('原文: <a href=', 'Source: <a href='),

    # ── Section: 写在前面的前面 ──
    ('<h2 id="h_2045918254108095918_0">写在前面的前面</h2>',
     '<h2 id="h_2045918254108095918_0">Before We Begin</h2>'),

    ('<h2 id="h_2045918254108095918_1">0. 写在前面：OPD 为什么 2026 上半年火的一塌糊涂</h2>',
     '<h2 id="h_2045918254108095918_1">0. Preface: Why OPD Exploded in H1 2026</h2>'),

    ('<h2 id="h_2045918254108095918_2">1. OPD 是什么：</h2>',
     '<h2 id="h_2045918254108095918_2">1. What Is OPD?</h2>'),

    ('<h2 id="h_2045918254108095918_6">2. OPD总谱系图</h2>',
     '<h2 id="h_2045918254108095918_6">2. OPD Genealogy Map</h2>'),

    # ── Blockquotes ──
    ('<blockquote>本文是一篇个人整理的 OPD（On-Policy Distillation）方向 mini-survey，覆盖 2026-01 ~ 2026-05 上 arXiv 的大概40多篇OPD 相关论文（其中 14 篇是我之前一篇篇精读过的，并在了我的专栏中。另外 大概30篇是为这篇 survey 重新检索 + 粗读后总结的）。<br><br><b>目标读者</b>：刚听说 OPD、想搞懂它在干嘛、想从这一波论文里找研究 gap 的同学。<br><b>写作原则</b>：所有insight都尽可能挂原文原文；abstract 没说的细节不写。</blockquote>',
     '<blockquote>This is a personal mini-survey on OPD (On-Policy Distillation), covering roughly 40+ OPD-related papers posted on arXiv from 2026-01 to 2026-05 (of which 14 I have previously read in depth and covered in my column; the remaining ~30 were re-searched and skimmed for this survey).<br><br><b>Target Audience</b>: Those who have just heard of OPD, want to understand what it does, and are looking for research gaps in this wave of papers.<br><b>Writing Principle</b>: All insights are tied to original papers wherever possible; details not mentioned in abstracts are omitted.</blockquote>'),

    ('<blockquote>主要是为了方便将现有大量的OPD工作归类，根据它们要解决的问题，我粗浅的分成了6个分支，每个分支都在尝试解决OPD的一个核心问题</blockquote>',
     '<blockquote>Primarily to facilitate categorizing the large volume of existing OPD work. Based on the problems they aim to solve, I have roughly divided them into 6 branches, each attempting to address a core problem in OPD.</blockquote>'),

    ('<blockquote>毕竟OPD很火，论文每天怎么着也得出几篇。<br>写这章的目的，其实就是想让大家在读完任意一篇OPD的论文后，都能根据它核心设计的不同，将其咱们这个有四个正交轴的OPD坐标系中；</blockquote>',
     '<blockquote>After all, OPD is hot — several papers come out every day.<br>The purpose of this chapter is to enable readers, after reading any OPD paper, to place it into our four-axis OPD coordinate system based on its core design differences.</blockquote>'),

    # ── Chapter/outline paragraphs ──
    ('<p><b>综述的全部link见下面：综述的全部link见下面：</b></p>',
     '<p><b>All survey links are below:</b></p>'),

    ('<p>针对26年上半年OPD工作的mini-survey 已经基本上写完了，目前大体分为六个，分别是：</p>',
     '<p>The mini-survey on H1 2026 OPD work is essentially complete. It is broadly divided into six parts:</p>'),

    ('<p><b>第0章：写在前面：OPD 为什么 2026 上半年火的一塌糊涂</b></p>',
     '<p><b>Chapter 0: Preface — Why OPD Exploded in H1 2026</b></p>'),

    ('<p><b>第1章：OPD是什么</b></p>',
     '<p><b>Chapter 1: What Is OPD?</b></p>'),

    ('<p><b>第2章：OPD总谱系图</b></p>',
     '<p><b>Chapter 2: OPD Genealogy Map</b></p>'),

    ('<p><b>第3章：OPD工作的六个分支</b>（可能要分成好几篇来讲了，从第二篇开始讲）</p>',
     '<p><b>Chapter 3: The Six Branches of OPD Work</b> (likely split across multiple posts, starting from Part 2)</p>'),

    ('<p><b>第4章：建立OPD论文的坐标系</b>（准备留到后续再讲）</p>',
     '<p><b>Chapter 4: Building a Coordinate System for OPD Papers</b> (to be covered in a later post)</p>'),

    ('<p><b>第5章：【个人看法】OPD还有的几个gap</b>（准备留到后续再讲）</p>',
     '<p><b>Chapter 5: [Personal View] Remaining Gaps in OPD</b> (to be covered in a later post)</p>'),

    ('<p><b>第6章：总结</b>（准备留到后续再讲）</p>',
     '<p><b>Chapter 6: Conclusion</b> (to be covered in a later post)</p>'),

    ('<p>整个mini-survey的第一版写完后统计了下有三万多字，感觉写成一篇就太冗长了。所以，准备是搞成三至四篇blog。这个算是第一篇吧～</p>',
     '<p>After completing the first draft of this mini-survey, I counted over 30,000 characters — too long for a single post. So I plan to split it into three to four blog posts. This is Part 1.</p>'),

    ('<p>第一篇就先入个门写以下三个章节吧</p>',
     "<p>Let's start with the following three introductory chapters:</p>"),

    ('<li><b>第0章：写在前面：OPD 为什么 2026 上半年火的一塌糊涂</b></li>',
     '<li><b>Chapter 0: Preface — Why OPD Exploded in H1 2026</b></li>'),

    ('<li><b>第1章：OPD是什么</b></li>',
     '<li><b>Chapter 1: What Is OPD?</b></li>'),

    ('<li><b>第2章：OPD总谱系图</b></li>',
     '<li><b>Chapter 2: OPD Genealogy Map</b></li>'),

    # ── Chapter 0: Why OPD Exploded ──
    ('<p>先看一组数字。我在 arXiv 上拉了 2026-01-01 到 2026-05-31 的 OPD / on-policy self-distillation / <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=reverse+KL+distillation&amp;zhida_source=entity" target="_blank">reverse KL distillation<svg',
     '<p>Let\'s look at some numbers. I pulled OPD / on-policy self-distillation / <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=reverse+KL+distillation&amp;zhida_source=entity" target="_blank">reverse KL distillation<svg'),

    (' / rubric distillation 相关论文，去掉一些挂着OPD的名字但明显关系不大的文章外，最终有 43 篇。</p>',
     ' / rubric distillation papers from arXiv between 2026-01-01 and 2026-05-31. After removing papers that mention OPD in name only but are clearly unrelated, the final count is 43.</p>'),

    ('<p>其中，5月单月就18 篇了。<b>OPD 已经从"知识蒸馏的一个变种"被推上了"<span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=LLM+post-training&amp;zhida_source=entity" target="_blank">LLM post-training<svg',
     '<p>Of these, 18 papers appeared in May alone. <b>OPD has been elevated from "a variant of knowledge distillation" to "a mainstream tool for <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=LLM+post-training&amp;zhida_source=entity" target="_blank">LLM post-training<svg'),

    ('的主线工具"位置。</b></p>',
     '."</b></p>'),

    ('<p>腾讯在4 月 1 日（第一版arxiv是这个时间点挂上去的，后续还有几版更新）挂出了第一篇 OPD 专项 survey <a href="https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2604.00626" target="_blank" rel="nofollow noreferrer">[A Survey of On-Policy Distillation for Large Language Models]</a>，70-80 页大部头，覆盖了从 2023 <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=GKD&amp;zhida_source=entity" target="_blank">GKD<svg',
     '<p>Tencent posted the first dedicated OPD survey <a href="https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2604.00626" target="_blank" rel="nofollow noreferrer">[A Survey of On-Policy Distillation for Large Language Models]</a> on April 1 (first arXiv version, with subsequent updates), a 70-80 page tome covering everything from 2023 <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=GKD&amp;zhida_source=entity" target="_blank">GKD<svg'),

    ('/MiniLLM 到 2026 春的全部主线。再加上 <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=Thinking+Machines+Lab&amp;zhida_source=entity" target="_blank">Thinking Machines Lab<svg',
     '/MiniLLM through spring 2026. Combined with <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=Thinking+Machines+Lab&amp;zhida_source=entity" target="_blank">Thinking Machines Lab<svg'),

    (' 2025-10 那篇被广泛转发的工程介绍（也是中文圈很多人接触 OPD 的入门读物，转载于微信 <a href="https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/sE_fUn2P88TCUnUDiIE7dA" target="_blank" rel="nofollow noreferrer">"On-Policy Distillation 深度剖析"</a>），整个领域在 2026 春进入了"定义清晰、工具收敛、应用爆发"的阶段。</p>',
     '\'s widely-shared engineering introduction from 2025-10 (the entry point for many in the Chinese community to OPD, republished on WeChat as <a href="https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/sE_fUn2P88TCUnUDiIE7dA" target="_blank" rel="nofollow noreferrer">"On-Policy Distillation Deep Dive"</a>), the field entered a phase of "clear definitions, converging tools, and exploding applications" by spring 2026.</p>'),

    ('<p><b>这篇 blog 想做的事</b>：</p>',
     '<p><b>What this blog aims to do</b>:</p>'),

    ('<li>把 OPD 是什么用最少的公式 + 一张图讲清楚（不假设你读过 GKD/MiniLLM）。</li>',
     '<li>Explain what OPD is with minimal formulas + one diagram (no prior knowledge of GKD/MiniLLM assumed).</li>'),

    ('<li>把 2026 上半年这 43 篇按"治什么病"切成六个流派，每派挑代表作讲 trick。</li>',
     '<li>Slice the 43 H1 2026 papers into six schools by "what problem they solve," picking representative works from each to explain their tricks.</li>'),

    ('<li>抽出 4 条横贯所有论文的设计轴，画一张大对比表，让你能把任意一篇新 OPD 论文塞进坐标系。</li>',
     '<li>Extract 4 design axes that cut across all papers, draw a large comparison table, so you can place any new OPD paper into this coordinate system.</li>'),

    ('<li>谈一谈这半年没人真正解决的 3 个 gap——如果你在找研究方向，可以从这里下手。</li>',
     '<li>Discuss 3 gaps that no one has truly solved in this half year — if you are looking for a research direction, start here.</li>'),

    ('<p><b>这篇 blog 不想做的事</b>：</p>',
     '<p><b>What this blog does NOT aim to do</b>:</p>'),

    ('<li>堆数字（实验结果只在必要时引用）</li>',
     '<li>Piling up numbers (experimental results cited only when necessary).</li>'),

    ('<li>复述 abstract（每个 trick 都尽量讲"它解决什么、怎么解、为什么这样解"）</li>',
     '<li>Paraphrasing abstracts (each trick is explained as "what it solves, how, and why this approach works").</li>'),

    ('<li>拍马屁夸某篇论文。</li>',
     '<li>Flattering any particular paper.</li>'),

    # ── Chapter 1: What is OPD ──
    ('<h3 id="h_2045918254108095918_3">1.1 <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=SFT&amp;zhida_source=entity" target="_blank">SFT<svg',
     '<h3 id="h_2045918254108095918_3">1.1 <span><a href="https://zhida.zhihu.com/search?content_id=276234398&amp;content_type=Article&amp;match_order=1&amp;q=SFT&amp;zhida_source=entity" target="_blank">SFT<svg'),

    (' / RL / OPD 三者的本质差别</h3>',
     ' / RL / OPD</h3>'),

    ('<h3 id="h_2045918254108095918_4">1.2 Reverse KL vs Forward KL：OPD 的分水岭</h3>',
     '<h3 id="h_2045918254108095918_4">1.2 Reverse KL vs Forward KL: The Watershed of OPD</h3>'),

    ('<h3 id="h_2045918254108095918_5">1.3 一份最简 vanilla OPD 伪代码</h3>',
     '<h3 id="h_2045918254108095918_5">1.3 Minimal Vanilla OPD Pseudocode</h3>'),

    ('<p>LLM post-training 的所有方法，本质上都可以用一个三元组描述，也就是：( 谁来生成训练 trajectory , 谁来打分 , 打分粒度 )；</p>',
     '<p>All LLM post-training methods can essentially be described by a triple: (who generates the training trajectory, who scores it, and at what granularity).</p>'),

    ('<p>把这个三元组填一下：</p>',
     "<p>Let's fill in this triple:</p>"),

    ('<th>方法</th>', '<th>Method</th>'),
    ('<th>生成 trajectory</th>', '<th>Trajectory Generator</th>'),
    ('<th>打分者</th>', '<th>Scorer</th>'),
    ('<th>粒度</th>', '<th>Granularity</th>'),

    ('<td>teacher / 人</td>', '<td>Teacher / Human</td>'),
    ('<td>假定每步都对</td>', '<td>Assumes every step is correct</td>'),
    ('<td>token-level，但每个 token 等权重</td>', '<td>Token-level, equal weight per token</td>'),
    ('<td>RL（如 GRPO）</td>', '<td>RL (e.g., GRPO)</td>'),
    ('<td>student 自己</td>', '<td>Student itself</td>'),

    ('<td>序列级稀疏 reward：整条 rollout 给一个 scalar reward R，通过 advantage 反传到每个 token，但 reward 信号本身只有一个标量</td>',
     '<td>Sequence-level sparse reward: a single scalar reward R for the entire rollout, back-propagated to each token via advantage, but the reward signal itself is just one scalar</td>'),

    ('<td>teacher 模型的 logit 分布</td>',
     "<td>Teacher model's logit distribution</td>"),

    ('<td>token-level dense supervision：每个 token 位置上独立计算 student 和 teacher 分布之间的 KL</td>',
     '<td>Token-level dense supervision: independently compute KL divergence between student and teacher distributions at every token position</td>'),

    ('<p><b>OPD 的关键定义性特征只有两条</b>：</p>',
     '<p><b>OPD has only two key defining characteristics</b>:</p>'),

    ('<li><b>on-policy</b>：训练数据是 student 自己采样生成的 trajectory，不是 teacher 预先生成的（这一条把 OPD 和经典 KD/SFT 区分开）。</li>',
     '<li><b>on-policy</b>: the training data consists of trajectories sampled by the student itself, not pre-generated by the teacher (this separates OPD from classical KD/SFT).</li>'),

    ('<li><b>token-level dense supervision</b>：每个 token 位置上算 student 的概率分布和 teacher 的概率分布之间的散度（这一条把 OPD 和 RL 区分开——RL 只在 trajectory 末尾或稀疏位点给 reward）。</li>',
     '<li><b>token-level dense supervision</b>: at every token position, compute the divergence between the student\'s and teacher\'s probability distributions (this separates OPD from RL — RL only provides rewards at trajectory endpoints or sparse positions).</li>'),

    ('<p>个人理解，满足这两条的训练都叫 OPD，<b>剩下所有东西都是在OPD基础上的变种</b>：</p>',
     '<p>In my understanding, any training that satisfies these two criteria is OPD. <b>Everything else is a variant built on top of OPD</b>:</p>'),

    ('<li><b>teacher</b>可以是固定的、可以是 EMA 的、可以是同一个模型加 prompt 偏置的、可以是黑盒 API、可以是 rubric；</li>',
     '<li>The <b>teacher</b> can be fixed, EMA-based, the same model with prompt bias, a black-box API, or a rubric.</li>'),

    ('<li><b>散度</b>可以是 reverse KL、forward KL、JS、token-level entropy；</li>',
     '<li>The <b>divergence</b> can be reverse KL, forward KL, JS, or token-level entropy.</li>'),

    ('<li><b>监督密度</b>可以是 full rollout、prefix-only、entropy-gated。</li>',
     '<li>The <b>supervision density</b> can be full rollout, prefix-only, or entropy-gated.</li>'),

    # ── 1.2 Reverse KL vs Forward KL ──
    ('<p><b>符号约定（全文统一）</b>：</p>',
     '<p><b>Notation conventions (consistent throughout)</b>:</p>'),

    ('<li>student policy 写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-13-Frame"',
     '<li>student policy is denoted as <span><span style="color: inherit;"></span><span id="MathJax-Element-13-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-13">\\pi_\\theta</script></span></span> （参数 <span><span style="color: inherit;"></span><span id="MathJax-Element-4-Frame"',
     '<script type="math/tex;mode=inline" id="MathJax-Element-13">\\pi_\\theta</script></span></span> (parameter <span><span style="color: inherit;"></span><span id="MathJax-Element-4-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-4">\\theta</script></span></span> ）；</li>',
     '<script type="math/tex;mode=inline" id="MathJax-Element-4">\\theta</script></span></span>);</li>'),

    ('<li>teacher policy 写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-1-Frame"',
     '<li>teacher policy is denoted as <span><span style="color: inherit;"></span><span id="MathJax-Element-1-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-1">\\pi_t</script></span></span> ；</li>',
     '<script type="math/tex;mode=inline" id="MathJax-Element-1">\\pi_t</script></span></span>;</li>'),

    ('<li>prompt 写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-5-Frame"',
     '<li>prompt is denoted as <span><span style="color: inherit;"></span><span id="MathJax-Element-5-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-5">x</script></span></span> ；</li>',
     '<script type="math/tex;mode=inline" id="MathJax-Element-5">x</script></span></span>;</li>'),

    ('<li>student 自己 rollout 出的样本写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-2-Frame"',
     '<li>samples from student rollout are denoted as <span><span style="color: inherit;"></span><span id="MathJax-Element-2-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-2">y^S \\sim \\pi_\\theta(\\cdot \\mid x)</script></span></span> ，teacher rollout 出的样本写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-9-Frame"',
     '<script type="math/tex;mode=inline" id="MathJax-Element-2">y^S \\sim \\pi_\\theta(\\cdot \\mid x)</script></span></span>, and teacher rollout samples as <span><span style="color: inherit;"></span><span id="MathJax-Element-9-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-9">y^T \\sim \\pi_t(\\cdot \\mid x)</script></span></span> ；</li>',
     '<script type="math/tex;mode=inline" id="MathJax-Element-9">y^T \\sim \\pi_t(\\cdot \\mid x)</script></span></span>;</li>'),

    ('<li>token 位置索引写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-6-Frame"',
     '<li>the token position index is denoted as <span><span style="color: inherit;"></span><span id="MathJax-Element-6-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-6">i</script></span></span> ，第 <span><span style="color: inherit;"></span><span id="MathJax-Element-11-Frame"',
     '<script type="math/tex;mode=inline" id="MathJax-Element-6">i</script></span></span>, the <span><span style="color: inherit;"></span><span id="MathJax-Element-11-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-11">i </script></span></span> 个 token 写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-3-Frame"',
     '<script type="math/tex;mode=inline" id="MathJax-Element-11">i</script></span></span>-th token as <span><span style="color: inherit;"></span><span id="MathJax-Element-3-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-3">y_i</script></span></span> ，之前生成的结果（即"state"）写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-8-Frame"',
     '<script type="math/tex;mode=inline" id="MathJax-Element-3">y_i</script></span></span>, and the previously generated result (i.e., the "state") as <span><span style="color: inherit;"></span><span id="MathJax-Element-8-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-8">y_{&lt;i} = (y_1, \\dots, y_{i-1})</script></span></span> 。token 级条件分布写作 <span><span style="color: inherit;"></span><span id="MathJax-Element-12-Frame"',
     '<script type="math/tex;mode=inline" id="MathJax-Element-8">y_{&lt;i} = (y_1, \\dots, y_{i-1})</script></span></span>. The token-level conditional distribution is denoted as <span><span style="color: inherit;"></span><span id="MathJax-Element-12-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-12">\\pi_\\theta(y_i \\mid x, y_{&lt;i})</script></span></span> ，求和指标 <span><span style="color: inherit;"></span><span id="MathJax-Element-10-Frame"',
     '<script type="math/tex;mode=inline" id="MathJax-Element-12">\\pi_\\theta(y_i \\mid x, y_{&lt;i})</script></span></span>, where the summation index <span><span style="color: inherit;"></span><span id="MathJax-Element-10-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-7">\\mathcal{V}</script></span></span> 。</li>',
     '<script type="math/tex;mode=inline" id="MathJax-Element-7">\\mathcal{V}</script></span></span>.</li>'),

    ('<p>OPD 默认用的是 <b>Reverse KL（RKL）</b>：</p>',
     '<p>OPD uses <b>Reverse KL (RKL)</b> by default:</p>'),

    ('<p>注意期望是按 <b>student 自己的分布</b> <span><span style="color: inherit;"></span><span id="MathJax-Element-16-Frame"',
     '<p>Note that the expectation is taken w.r.t. <b>the student\'s own distribution</b> <span><span style="color: inherit;"></span><span id="MathJax-Element-16-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-14">y^S \\sim \\pi_\\theta(\\cdot \\mid x)</script></span></span> ）。</p>',
     '<script type="math/tex;mode=inline" id="MathJax-Element-14">y^S \\sim \\pi_\\theta(\\cdot \\mid x)</script></span></span>).</p>'),

    ('<p>对比 <b>Forward KL（FKL）</b>：</p>',
     '<p>Compare with <b>Forward KL (FKL)</b>:</p>'),

    ('<p>期望按 teacher 的分布 <span><span style="color: inherit;"></span><span id="MathJax-Element-18-Frame"',
     '<p>The expectation is taken w.r.t. the teacher\'s distribution <span><span style="color: inherit;"></span><span id="MathJax-Element-18-Frame"'),

    ('<script type="math/tex;mode=inline" id="MathJax-Element-18">\\pi_t</script></span></span> 取。这是经典 KD 用的散度。</p>',
     '<script type="math/tex;mode=inline" id="MathJax-Element-18">\\pi_t</script></span></span>. This is the divergence used in classical KD.</p>'),

    ('<p><b>两者的本质区别用一句话讲</b>：reverse KL 是 mode-seeking（学生不去管 teacher 那些它根本到不了的小概率分支，专心模仿 teacher 的主峰），forward KL 是 mode-covering（学生被强迫把 teacher 所有可能的输出都覆盖到，哪怕代价是把概率涂得很平）。想看更详细的分析，可以参考这篇blog <a href="https://zhuanlan.zhihu.com/p/2041180570701587116" target="_blank">【概念讲解】Off-Policy + On-Policy 两段式蒸馏</a></p>',
     '<p><b>The essential difference in one sentence</b>: reverse KL is mode-seeking (the student ignores low-probability teacher branches it can never reach, focusing on imitating the teacher\'s main modes), while forward KL is mode-covering (the student is forced to cover all possible teacher outputs, even at the cost of spreading probability mass too thin). For a more detailed analysis, see this blog: <a href="https://zhuanlan.zhihu.com/p/2041180570701587116" target="_blank">[Concept Explainer] Off-Policy + On-Policy Two-Stage Distillation</a></p>'),

    ('<p>在 LLM 大词表 + teacher-student capacity gap 大的场景里，RKL 几乎一边倒赢。这2026年之前的行业公式吧，也是 <a href="https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2604.00223" target="_blank" rel="nofollow noreferrer">[Diversity-Aware RKL]</a> 在 2026-03-31 的 abstract 里再次复述的事实："RKL has recently emerged as the preferred objective for LLM distillation, consistently outperforming FKL"。</p>',
     '<p>In the LLM setting with large vocabularies and a significant teacher-student capacity gap, RKL wins almost unilaterally. This was already the industry consensus before 2026, and <a href="https://link.zhihu.com/?target=https%3A//arxiv.org/abs/2604.00223" target="_blank" rel="nofollow noreferrer">[Diversity-Aware RKL]</a> reiterated this fact in its abstract on 2026-03-31: "RKL has recently emerged as the preferred objective for LLM distillation, consistently outperforming FKL."</p>'),

    ('<p><b>但 RKL 也有自己的病</b>：mode-seeking 推到极致就是 mode collapse，student 学到只输出 teacher 主峰的几条路径，多样性塌掉。这就引出了 2026 上半年第一类高频工作：<b>散度本身的修正</b>（DRKL / EOPD 等，在 §3.1 讲）。</p>',
     '<p><b>But RKL has its own disease</b>: mode-seeking pushed to the extreme becomes mode collapse — the student learns to output only a few paths from the teacher\'s main modes, and diversity collapses. This leads to the first category of high-frequency work in H1 2026: <b>corrections to the divergence itself</b> (DRKL / EOPD, etc., covered in §3.1).</p>'),

    # ── 1.3 Vanilla OPD Pseudocode ──
    ('<p>整段伪代码就这么短。所有 2026 上半年的 OPD 论文，绝大多数改的都是这段代码里的一部分：</p>',
     '<p>The entire pseudocode is this short. The vast majority of OPD papers in H1 2026 modify some part of this code:</p>'),

    ('<li>有的工作是改第 1 步：teacher 怎么生 trajectory。比如：黑盒 / rubric / privileged context / best-of-N rollout selection；</li>',
     '<li>Some works modify Step 1: how to generate teacher trajectory. Examples: black-box / rubric / privileged context / best-of-N rollout selection.</li>'),

    ('<li>有的工作是改第 2 步：teacher 是谁。比如：固定 / EMA / 周期硬拷贝 student / 同模型加 prompt / 另一个领域专家；</li>',
     '<li>Some works modify Step 2: who the teacher is. Examples: fixed / EMA / periodic hard-copy of student / same model with a prompt / another domain expert.</li>'),

    ('<li>有的工作是改第 3 步：散度怎么选。比如：RKL / FKL / 按 entropy gate / DRKL / clipping</li>',
     '<li>Some works modify Step 3: which divergence to use. Examples: RKL / FKL / entropy-gated / DRKL / clipping.</li>'),

    ('<li>最后还有的工作改"哪些 token 算 loss"。比如：full rollout / prefix-only / entropy mask / advantage weighted 这些点；</li>',
     '<li>Finally, some works modify "which tokens contribute to the loss." Examples: full rollout / prefix-only / entropy mask / advantage weighted.</li>'),

    ('<p>这就是 OPD 系列工作的整体格局。</p>',
     '<p>This is the overall landscape of OPD work.</p>'),

    ('<p><b>一句话记住 OPD</b>："student 自己写答案、teacher 在每个 token 位置打分、用打分梯度往 teacher 那边拉。" </p>',
     '<p><b>Remember OPD in one sentence</b>: "The student writes its own answers, the teacher scores at every token position, and the scoring gradients pull the student toward the teacher."</p>'),

    ('<li>如果说，SFT 是别人写答案 student 抄；</li>',
     '<li>If SFT is someone else writing the answer and the student copying it,</li>'),

    ('<li>RL 是 student 写完一篇拿一个总分（reward）；</li>',
     '<li>and RL is the student writing an essay and getting a single total score (reward),</li>'),

    ('<li>那OPD 卡在两者中间，student 写答案 + 每个 token 都打分；<br> </li>',
     '<li>then OPD sits between the two: the student writes the answer + every token gets scored.<br></li>'),

    # ── Chapter 2: OPD Genealogy Map ──
    ('<p>下面这张图是整个mini-survey 的roadmap，后面章节都围着它转。⭐ = 我之前精读过并写过单独笔记的 14 篇，详情见下面的那个专栏；其余 29 篇是粗读后的论文。</p>',
     '<p>The figure below is the roadmap for this entire mini-survey; all subsequent chapters revolve around it. ⭐ = 14 papers I previously read in depth and wrote individual notes on (see the column below for details); the remaining 29 were skimmed for this survey.</p>'),
]

count = 0
for old, new in replacements:
    if old in html:
        html = html.replace(old, new)
        count += 1
    else:
        print(f'WARNING: Not found: {old[:80]}...')

print(f'Applied {count}/{len(replacements)} replacements')

with open('zhihu_article_2045918254108095918_en/article.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done!')
