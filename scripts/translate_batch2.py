# -*- coding: utf-8 -*-
"""Replace Chinese text in article about OPD from tech reports."""
import re

with open('zhihu_article_2031101471563962191_en/article.html', 'r', encoding='utf-8') as f:
    html = f.read()

replacements = [
    # ── Lang ──
    ('<html lang="zh-CN">', '<html lang="en">'),

    # ── Title & meta ──
    ('<title>从技术报告看On-Policy Distillation的崛起: 大模型后训练新范式</title>',
     '<title>The Rise of On-Policy Distillation from Tech Reports: A New Post-Training Paradigm for LLMs</title>'),

    ('<h1>从技术报告看On-Policy Distillation的崛起: 大模型后训练新范式</h1>',
     '<h1>The Rise of On-Policy Distillation from Tech Reports: A New Post-Training Paradigm for LLMs</h1>'),

    ('作者: <strong>潜龙勿用​</strong>',
     'Author: <strong>Qian Long Wu Yong</strong>'),

    ('原文: <a href=', 'Source: <a href='),
    ('>知乎链接</a>', '>Zhihu Link</a>'),

    # ── Section h2 ──
    ('<h2>一、什么是 On-Policy Distillation？</h2>',
     '<h2>1. What Is On-Policy Distillation?</h2>'),

    ('<h2>二、OPD 的变种：各家实现的技术分歧</h2>',
     '<h2>2. OPD Variants: Technical Divergences Across Implementations</h2>'),

    ('<h2>三、各家的动机、实现与效果</h2>',
     '<h2>3. Motivations, Implementations, and Results Across Teams</h2>'),

    ('<h2>四、未来展望</h2>',
     '<h2>4. Future Outlook</h2>'),

    # ── Section h3 ──
    ('<h3>三种路线的对比</h3>',
     '<h3>Comparison of Three Approaches</h3>'),

    ('<h3>Reverse KL 的 Mode-Seeking 性质</h3>',
     '<h3>The Mode-Seeking Nature of Reverse KL</h3>'),

    ('<h3>工程实现极简</h3>',
     '<h3>Minimal Engineering Implementation</h3>'),

    ('<h3>实验验证效率优势</h3>',
     '<h3>Experimental Validation of Efficiency Advantages</h3>'),

    ('<h3>2.1 KL 计算粒度：Token-Level vs Full-Vocabulary</h3>',
     '<h3>2.1 KL Computation Granularity: Token-Level vs Full-Vocabulary</h3>'),

    ('<h3>2.2 额外奖励信号：纯蒸馏 vs OPD + ORM</h3>',
     '<h3>2.2 Additional Reward Signals: Pure Distillation vs OPD + ORM</h3>'),

    ('<h3>2.3 教师选取策略：同架构 checkpoint vs 异构多专家</h3>',
     '<h3>2.3 Teacher Selection Strategy: Same-Architecture Checkpoint vs Heterogeneous Multi-Expert</h3>'),

    ('<h3>2.4 OPD 在 Pipeline 中的位置</h3>',
     '<h3>2.4 OPD Position in the Pipeline</h3>'),

    ('<h3>3.1 Qwen3：效率革命，OPD 最早的系统性应用（2025 年 5 月）</h3>',
     '<h3>3.1 Qwen3: Efficiency Revolution — The Earliest Systematic Application of OPD (May 2025)</h3>'),

    ('<h3>3.2 GLM-5：修复多阶段 RL 的灾难性遗忘</h3>',
     '<h3>3.2 GLM-5: Fixing Catastrophic Forgetting in Multi-Stage RL</h3>'),

    ('<h3>3.3 MiMo-V2-Flash：能力不平衡的系统性解法</h3>',
     '<h3>3.3 MiMo-V2-Flash: A Systematic Solution to Capability Imbalance</h3>'),

    ('<h3>3.4 DeepSeek V4：万亿参数专家知识的 Logit-Space 压缩</h3>',
     '<h3>3.4 DeepSeek V4: Logit-Space Compression of Trillion-Parameter Expert Knowledge</h3>'),

    ('<h3>4.1 Full-Vocabulary KL 将成为标配，工程门槛持续下降</h3>',
     '<h3>4.1 Full-Vocabulary KL Will Become Standard, Engineering Barriers Continue to Fall</h3>'),

    ('<h3>4.2 OPD + PRM：从结果监督到过程监督</h3>',
     '<h3>4.2 OPD + PRM: From Outcome Supervision to Process Supervision</h3>'),

    ('<h3>4.3 Iterative Co-Evolution：自强化的师生螺旋</h3>',
     '<h3>4.3 Iterative Co-Evolution: A Self-Reinforcing Teacher-Student Spiral</h3>'),

    ('<h3>4.4 OPD 与百万 Token 长上下文的张力</h3>',
     '<h3>4.4 The Tension Between OPD and Million-Token Long Contexts</h3>'),

    ('<h3>4.5 Inference-Time Distillation：推理时的动态教师</h3>',
     '<h3>4.5 Inference-Time Distillation: Dynamic Teachers at Inference Time</h3>'),

    ('<h3>4.6 范式总结：从参数空间整合到 Logit 空间整合</h3>',
     '<h3>4.6 Paradigm Summary: From Parameter-Space Integration to Logit-Space Integration</h3>'),

    # ── Section 1 paragraphs ──
    ('<p>过去一年，大模型后训练路线出现了一个清晰变化：<b>On-Policy Distillation 正在成为事实上的后训练新范式</b>。从 <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=Qwen3&amp;zhida_source=entity" target="_blank">Qwen3<svg',
     '<p>Over the past year, a clear shift has emerged in LLM post-training: <b>On-Policy Distillation is becoming the de facto new post-training paradigm</b>. From <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=Qwen3&amp;zhida_source=entity" target="_blank">Qwen3<svg'),

    (' 用 OPD 高效训练轻量模型，到 GLM-5 用它修复多阶段 RL 后的能力遗忘；从小米 <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=MiMo-V2&amp;zhida_source=entity" target="_blank">MiMo-V2<svg',
     ' using OPD to efficiently train lightweight models, to GLM-5 using it to repair capability forgetting after multi-stage RL; from Xiaomi\'s <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=MiMo-V2&amp;zhida_source=entity" target="_blank">MiMo-V2<svg'),

    (' 通过多教师 OPD 整合数学、代码、搜索等专家能力，再到 DeepSeek-V4（<a href="https://zhuanlan.zhihu.com/p/2030982954617414764" target="_blank">DeepSeek-V4技术报告解读: 从架构到 Infra 的全栈重构</a>） 直接以 OPD 替代 mixed RL，各家技术报告都指向同一个趋势：后训练不再只是依赖昂贵的 RL 探索，而是越来越重视如何稳定、高效地把已有强模型的能力迁移到目标模型中。</p>',
     ' using multi-teacher OPD to integrate expert capabilities in math, code, and search, to DeepSeek-V4 (<a href="https://zhuanlan.zhihu.com/p/2030982954617414764" target="_blank">DeepSeek-V4 Tech Report: Full-Stack Refactoring from Architecture to Infra</a>) directly replacing mixed RL with OPD — tech reports from all teams point to the same trend: post-training is no longer just about expensive RL exploration, but increasingly about how to stably and efficiently transfer capabilities from existing strong models to target models.</p>'),

    ('<p>25年12月，我曾发表过OPD解读：<a href="https://zhuanlan.zhihu.com/p/1988199307237680586" target="_blank">On-Policy Distillation</a></p>',
     '<p>In December 2025, I published an OPD explainer: <a href="https://zhuanlan.zhihu.com/p/1988199307237680586" target="_blank">On-Policy Distillation</a></p>'),

    ('<p>OPD 的吸引力在于它同时继承了 RL 和蒸馏的优点：学生从自身分布中采样，避免了 <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=off-policy+%E8%92%B8%E9%A6%8F&amp;zhida_source=entity" target="_blank">off-policy 蒸馏<svg',
     '<p>The appeal of OPD lies in inheriting the strengths of both RL and distillation: the student samples from its own distribution, avoiding the distribution mismatch of <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=off-policy+%E8%92%B8%E9%A6%8F&amp;zhida_source=entity" target="_blank">off-policy distillation<svg'),

    ('的分布错位；教师则对每个 token 提供密集反馈，显著提升了训练信号密度。更关键的是，OPD 把能力整合从参数空间转移到 <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=logit+%E7%A9%BA%E9%97%B4&amp;zhida_source=entity" target="_blank">logit 空间<svg',
     '; the teacher provides dense per-token feedback, significantly increasing training signal density. More critically, OPD shifts capability integration from parameter space to <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=logit+%E7%A9%BA%E9%97%B4&amp;zhida_source=entity" target="_blank">logit space<svg'),

    ('，绕开了 weight merge 和 mixed RL 中常见的能力干扰问题。因此，理解 OPD 的原理与各家实现差异，已经成为理解新一代大模型后训练方法的关键入口</p>',
     ', bypassing the capability interference problems common in weight merge and mixed RL. Therefore, understanding the principles of OPD and the implementation differences across teams has become the key entry point for understanding the new generation of LLM post-training methods.</p>'),

    ('<p>小米 MiMo-V2 后训练流程图：</p>',
     '<p>Xiaomi MiMo-V2 post-training pipeline:</p>'),

    ('<p>要理解它为什么重要，需要先清楚它解决了什么问题</p>',
     '<p>To understand why it matters, we need to first be clear about what problems it solves.</p>'),

    ('<p>训练一个强大的语言模型，后训练阶段通常面临三条路：</p>',
     '<p>When training a powerful language model, the post-training phase typically faces three paths:</p>'),

    ('<p><b>纯 RL（<span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=Reinforcement+Learning&amp;zhida_source=entity" target="_blank">Reinforcement Learning<svg',
     '<p><b>Pure RL (<span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=Reinforcement+Learning&amp;zhida_source=entity" target="_blank">Reinforcement Learning<svg'),

    ('）</b>：让模型自己生成轨迹，对完整序列打一个结果奖励（sparse reward），用 PPO 或 GRPO 更新参数。这条路有效，DeepSeek-R1 和 Qwen3 旗舰都走过它。但问题在于信号密度极低——无论一条轨迹有多少 token，总共就得到一个 reward 信号。<span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=thinkingmachines.ai&amp;zhida_source=entity" target="_blank">thinkingmachines.ai<svg',
     ')</b>: Let the model generate its own trajectories, assign a single outcome reward (sparse reward) to the entire sequence, and update parameters using PPO or GRPO. This path works — DeepSeek-R1 and Qwen3 flagship models have walked it. But the problem is extremely low signal density — no matter how many tokens a trajectory has, you only get one reward signal in total. <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=thinkingmachines.ai&amp;zhida_source=entity" target="_blank">thinkingmachines.ai<svg'),

    (' 的分析估计，OPD 的信号密度约为纯 RL 的 50-100 倍。</p>',
     ' estimates that OPD\'s signal density is approximately 50-100x that of pure RL.</p>'),

    ('<p><b>Off-Policy 蒸馏（静态数据集蒸馏）</b>：用一个强教师模型生成高质量轨迹，收集成静态数据集，对学生做 SFT 或 logit 对齐。这是 DeepSeek-R1-Distill 系列的路线。问题是经典的 exposure bias：学生在测试时生成的 token 序列与训练时接受监督的教师轨迹分布是错位的。一旦学生偏离教师轨迹，后续 token 的监督信号就失真了，泛化能力因此受限。</p>',
     '<p><b>Off-Policy Distillation (static dataset distillation)</b>: Use a strong teacher model to generate high-quality trajectories, collect them into a static dataset, and perform SFT or logit alignment on the student. This is the DeepSeek-R1-Distill approach. The problem is the classic exposure bias: the token sequences the student generates at test time are distributionally mismatched with the teacher trajectories used for supervision during training. Once the student deviates from the teacher trajectory, the supervision signal for subsequent tokens becomes distorted, limiting generalization ability.</p>'),

    ('<p><b>On-Policy Distillation</b>：两者取长补短——像 RL 一样，让学生从<b>自己当前的分布</b>采样轨迹（on-policy）；像蒸馏一样，由教师模型对每一个采样 token 给出 per-token 的 dense 反馈，具体形式是教师在该 token 上的 log 概率。学生通过最小化与教师之间的 <b><span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=reverse+KL&amp;zhida_source=entity" target="_blank">reverse KL<svg',
     '<p><b>On-Policy Distillation</b>: Combines the best of both — like RL, it lets the student sample trajectories from <b>its own current distribution</b> (on-policy); like distillation, the teacher model provides dense per-token feedback for every sampled token, specifically in the form of the teacher\'s log probability at that token. The student updates by minimizing the <b><span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=reverse+KL&amp;zhida_source=entity" target="_blank">reverse KL<svg'),

    (' 散度</b>来更新：</p>',
     ' divergence</b>:</p>'),

    ('<p>这个公式的梯度方向，是让学生在自己已经采样出的 token 上，向教师的概率靠近。因为轨迹来自学生自身，不存在 distribution shift；因为教师给出 per-token 信号，每次更新的信息量远超稀疏 RL。</p>',
     '<p>The gradient direction of this formula pushes the student, on the tokens it has already sampled, closer to the teacher\'s probabilities. Because the trajectories come from the student itself, there is no distribution shift; because the teacher provides per-token signals, each update carries far more information than sparse RL.</p>'),

    ('<p>选择 reverse KL 而非 forward KL 不是随意的。Reverse KL 具有 <b>mode-seeking</b> 性质：当<span>学生概率为零的地方，KL 项也为零</span>，梯度消失；因此学生会集中学习教师的某一个高概率 " 模式 "，而不是平均覆盖教师所有可能的输出。</p>',
     '<p>The choice of reverse KL over forward KL is not arbitrary. Reverse KL has a <b>mode-seeking</b> property: where the student assigns zero probability, the KL term is also zero, and the gradient vanishes; thus the student concentrates on learning one high-probability "mode" of the teacher, rather than uniformly covering all possible teacher outputs.</p>'),

    ('<p>这对推理任务恰恰合适。数学推理题有正确解题路径，不需要模型均匀地模仿所有可能的推导风格。Mode-seeking 的 OPD 让学生 " 找到一条教师认可的路并坚定地走下去 "，比 forward KL（试图覆盖教师所有输出）的效果更好。</p>',
     '<p>This is precisely appropriate for reasoning tasks. Math problems have correct solution paths — there is no need for the model to uniformly imitate all possible derivation styles. Mode-seeking OPD lets the student "find a path the teacher approves of and follow it confidently," which works better than forward KL (which tries to cover all teacher outputs).</p>'),

    ('<p>此外，thinkingmachines.ai 博客指出 OPD 天然 <b>unhackable</b>：低 KL 总是对应着学生在模仿教师的好行为，不像 RL 的 reward function 可以被模型找到捷径绕过。</p>',
     '<p>Furthermore, the thinkingmachines.ai blog points out that OPD is inherently <b>unhackable</b>: low KL always corresponds to the student imitating the teacher\'s good behavior, unlike RL reward functions that can be shortcut by the model.</p>'),

    ('<p>在已有 RL 训练框架（如 GRPO）之上接入 OPD，改动极小：只需把原来的 group-normalized advantage 替换为教师与学生的 log ratio：',
     '<p>Integrating OPD on top of existing RL training frameworks (such as GRPO) requires minimal changes: simply replace the original group-normalized advantage with the log ratio between teacher and student:'),

    ('<p>其中 <code>sg</code> 是 stop-gradient 算子，防止梯度流回教师分布。博客将其描述为 "a one-line change on top of RL implementations"。GLM-5 和 MiMo 的论文都可以印证这一说法，二者都显式复用了自己的 RL 优化框架。</p>',
     '<p>Where <code>sg</code> is the stop-gradient operator, preventing gradients from flowing back to the teacher distribution. The blog describes it as "a one-line change on top of RL implementations." Both the GLM-5 and MiMo papers confirm this claim, as both explicitly reuse their own RL optimization frameworks.</p>'),

    ('<p>thinkingmachines.ai 博客给出了迄今最清晰的对比数据（AIME\'24 数学推理基准，从同一个 off-policy 蒸馏 checkpoint 出发）：</p>',
     '<p>The thinkingmachines.ai blog provides the clearest comparison data to date (AIME\'24 math reasoning benchmark, starting from the same off-policy distillation checkpoint):</p>'),

    ('<th>方法</th><th>得分</th><th>相对计算量</th>',
     '<th>Method</th><th>Score</th><th>Relative Compute</th>'),

    ('<td>Off-policy 蒸馏（基线）</td>',
     '<td>Off-policy Distillation (baseline)</td>'),

    ('<td>纯 RL</td>', '<td>Pure RL</td>'),

    ('<td>On-Policy 蒸馏</td>', '<td>On-Policy Distillation</td>'),

    ('<p>OPD 以远低于纯 RL 的算力，实现了远超 off-policy 蒸馏、且优于纯 RL 的效果。Qwen3 在旗舰模型层面印证了这一结论，并将效率优势定量为 " 仅需完整 4 阶段 RL 训练的 1/10 GPU 时间 "。</p>',
     '<p>OPD achieves results far exceeding off-policy distillation and surpassing pure RL, at a fraction of the compute. Qwen3 confirmed this conclusion at the flagship model level, quantifying the efficiency advantage as "requiring only 1/10 of the GPU time of full 4-stage RL training."</p>'),

    # ── Section 2 ──
    ('<p>Qwen3（2025 年 5 月）是主要头部实验室中最早在技术报告中系统阐述 OPD 的。随后数月内，GLM-5（2026 年 2 月）、MiMo-V2-Flash（2026 年 1 月）、<span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=DeepSeek+V4&amp;zhida_source=entity" target="_blank">DeepSeek V4<svg',
     '<p>Qwen3 (May 2025) was the first among major labs to systematically describe OPD in a tech report. In the following months, GLM-5 (February 2026), MiMo-V2-Flash (January 2026), and <span><a href="https://zhida.zhihu.com/search?content_id=273730841&amp;content_type=Article&amp;match_order=1&amp;q=DeepSeek+V4&amp;zhida_source=entity" target="_blank">DeepSeek V4<svg'),

    (' 相继跟进。但四家的实现在关键技术维度上存在显著分歧，形成了事实上的 "OPD 变种谱系 "。</p>',
     ' followed suit. However, the four teams\' implementations diverge significantly across key technical dimensions, forming a de facto "OPD variant spectrum."</p>'),

    # 2.1 Token-Level vs Full-Vocab
    ('<p>这是最根本的技术分歧。</p>',
     '<p>This is the most fundamental technical divergence.</p>'),

    ('<p><b>Token-level KL（多数团队）</b>：只计算教师在实际被采样的那个 token 上的概率，即 <code>log π_teacher(y_t|x, y_{&lt;t})</code>。这是对真实 KL 散度的蒙特卡洛近似——完整的 KL 需要对整个词表求积分，但近似版只需要教师在单个 token 上的 forward pass，计算量和显存需求极小。</p>',
     '<p><b>Token-level KL (most teams)</b>: Only compute the teacher\'s probability on the actually sampled token, i.e., <code>log π_teacher(y_t|x, y_{&lt;t})</code>. This is a Monte Carlo approximation of the true KL divergence — the full KL requires integrating over the entire vocabulary, but the approximate version only needs a single forward pass of the teacher on a single token, with minimal computation and memory requirements.</p>'),

    ('<p>GLM-5（Section 3.5，Eq. 2）、MiMo（Section 4.4，Eq. 5-8）和 Qwen3（Section 4.5）都采用这一方案。区别在于细节：</p>',
     '<p>GLM-5 (Section 3.5, Eq. 2), MiMo (Section 4.4, Eq. 5-8), and Qwen3 (Section 4.5) all adopt this approach. The differences lie in the details:</p>'),

    ('<li><b>GLM-5</b> 将 GRPO 的 group size 从 32 降至 1，因为教师 log ratio 直接充当 advantage，不再需要组内对比来估计基线</li>',
     '<li><b>GLM-5</b> reduces GRPO\'s group size from 32 to 1, because the teacher log ratio directly serves as the advantage, eliminating the need for within-group comparisons to estimate baselines.</li>'),

    ('<li><b>MiMo</b> 额外引入重要性采样截断权重 <span><span style="color: inherit;"></span><span id="MathJax-Element-4-Frame"',
     '<li><b>MiMo</b> additionally introduces importance sampling clipping weights <span><span style="color: inherit;"></span><span id="MathJax-Element-4-Frame"'),

    ('，当训练策略和推理策略的比值超出 <span><span style="color: inherit;"></span><span id="MathJax-Element-3-Frame"',
     ', which discards a token when the ratio between training and inference policies exceeds <span><span style="color: inherit;"></span><span id="MathJax-Element-3-Frame"'),

    (' 时丢弃该 token，增强训练稳定性</li>',
     ', enhancing training stability.</li>'),

    ('<p><b>Full-Vocabulary Logit Distillation（DeepSeek V4，Section 5.1.2）</b>：保留完整词表上的 KL，即',
     '<p><b>Full-Vocabulary Logit Distillation (DeepSeek V4, Section 5.1.2)</b>: Retains KL over the full vocabulary, i.e.,'),

    ('<p>DeepSeek V4 原文明确批评 token-level 近似："prior works typically simplify the full-vocabulary KL loss into token-level KL estimates... this approach leads to <b>high variance in gradient estimation</b> and often causes <b>training instability</b>"。全词表 KL 给出每一步的精确梯度，训练更稳定，但代价是巨大的工程挑战：词表尺寸 × 序列长度 × 专家数 的显存消耗。</p>',
     '<p>The DeepSeek V4 paper explicitly criticizes token-level approximation: "prior works typically simplify the full-vocabulary KL loss into token-level KL estimates... this approach leads to <b>high variance in gradient estimation</b> and often causes <b>training instability</b>." Full-vocabulary KL provides exact gradients at each step and more stable training, but at the cost of a massive engineering challenge: vocabulary size × sequence length × number of experts in memory consumption.</p>'),

    ('<p>DeepSeek V4 为此专门开发了三层工程解决方案：</p>',
     '<p>DeepSeek V4 developed a three-layer engineering solution for this:</p>'),

    ('<li><b>Teacher weight scheduling</b>：教师权重卸载到分布式存储，ZeRO-like 参数共享，按需加载，不长驻显存</li>',
     '<li><b>Teacher weight scheduling</b>: Teacher weights are offloaded to distributed storage with ZeRO-like parameter sharing, loaded on demand, not resident in GPU memory.</li>'),

    ('<li><b>Cached hidden states</b>：只缓存教师最后一层的 hidden state（而非词表维度的完整 logits），需要 logit 时临时经过 prediction head 重建，从根本上消除词表维度的显存瓶颈</li>',
     '<li><b>Cached hidden states</b>: Only cache the teacher\'s last-layer hidden state (rather than full logits at vocabulary dimension), reconstructing logits on-the-fly through the prediction head when needed, fundamentally eliminating the vocabulary-dimension memory bottleneck.</li>'),

    ('<li><b>专用 TileLang kernel</b>：加速精确 KL 计算并压制动态内存分配</li>',
     '<li><b>Dedicated TileLang kernel</b>: Accelerates exact KL computation and suppresses dynamic memory allocation.</li>'),

    # 2.2 Pure vs OPD + ORM
    ('<p><b>纯蒸馏路线</b>（GLM-5、DeepSeek V4）：OPD 阶段只使用 KL 散度作为信号，完全不叠加 outcome reward。</p>',
     '<p><b>Pure distillation path</b> (GLM-5, DeepSeek V4): The OPD stage uses only KL divergence as the signal, with no outcome reward overlay at all.</p>'),

    ('<p>GLM-5 的逻辑是：OPD 是最终收尾阶段，目标纯粹是 " 恢复能力 "，不需要再探索新的行为空间，只需高效对齐前序 RL checkpoint。DeepSeek V4 则是用 OPD 完全替代了 V3.2 中的 mixed RL 阶段，整个统一化过程只有 KL 信号驱动。</p>',
     '<p>GLM-5\'s logic: OPD is the final wrap-up stage, with the pure goal of "capability recovery" — no need to explore new behavior spaces, just efficiently align to prior RL checkpoints. DeepSeek V4 completely replaced the mixed RL stage from V3.2 with OPD, with the entire unification process driven solely by KL signals.</p>'),

    ('<p><b>OPD + ORM 混合路线</b>（MiMo MOPD，Section 4.4，Eq. 9）：</p>',
     '<p><b>OPD + ORM hybrid path</b> (MiMo MOPD, Section 4.4, Eq. 9):</p>'),

    ('<p>KL 项提供 token 级别的 dense 局部信号，ORM（Outcome Reward Model）项提供序列级别的 sparse 全局信号，二者通过系数 α 调和。</p>',
     '<p>The KL term provides token-level dense local signals, while the ORM (Outcome Reward Model) term provides sequence-level sparse global signals, reconciled through coefficient α.</p>'),

    ('<p>MiMo 的 ablation（Figure 6）给出了清晰的层级关系：纯 ORM RL &lt; MOPD w/o ORM &lt; <b>MOPD（ORM + KL）</b>。KL 信号显著加速收敛，ORM 信号则保持与可验证结果的对齐，缺一不可。</p>',
     '<p>MiMo\'s ablation (Figure 6) shows a clear hierarchy: pure ORM RL &lt; MOPD w/o ORM &lt; <b>MOPD (ORM + KL)</b>. KL signals significantly accelerate convergence, while ORM signals maintain alignment with verifiable results — both are indispensable.</p>'),

    # 2.3 Teacher Selection
    ('<p><b>同架构前序 checkpoint（GLM-5）</b>：教师是同一个模型在 Reasoning RL 和 General RL 两个前序阶段训练完毕的 checkpoint。教师与学生共享完全相同的架构和词表，logit 空间天然对齐，实现最简单，信号质量最有保障。代价是教师的多样性受限——只有两个来自不同 RL 阶段的版本。</p>',
     '<p><b>Same-architecture prior checkpoint (GLM-5)</b>: The teachers are checkpoints of the same model after completing two prior stages: Reasoning RL and General RL. Teacher and student share identical architecture and vocabulary, with naturally aligned logit spaces — the simplest implementation and most reliable signal quality. The cost is limited teacher diversity — only two versions from different RL stages.</p>'),

    ('<p><b>多领域专家混合路由（MiMo）</b>：教师集合包括各领域 RL 专家（代码、数学、搜索、通用等）、SFT 模型，以及学生模型自身（用于 self-distillation，防止现有能力退化）。哪个任务路由到哪个教师由任务域标签决定。论文特别强调这种 "decoupled design enables easy integration of new teachers without restructuring the entire pipeline"——教师集合可以随时增减，无需重训流水线。</p>',
     '<p><b>Multi-domain expert mixed routing (MiMo)</b>: The teacher set includes domain-specific RL experts (code, math, search, general, etc.), SFT models, and the student model itself (for self-distillation to prevent capability degradation). Which task routes to which teacher is determined by task domain labels. The paper emphasizes that this "decoupled design enables easy integration of new teachers without restructuring the entire pipeline" — the teacher set can be expanded or reduced at any time without retraining the pipeline.</p>'),

    ('<p><b>10+ 万亿参数异构专家（DeepSeek V4）</b>：规模最大的多教师方案，独立训练 10 个以上专家模型，每个覆盖一个领域（数学、代码、Agent、指令跟随），每个领域还有三种推理强度变体（Non-think / Think High / Think Max）。各专家以 per-expert 权重 <span><span style="color: inherit;"></span><span id="MathJax-Element-8-Frame"',
     '<p><b>10+ trillion-parameter heterogeneous experts (DeepSeek V4)</b>: The largest multi-teacher scheme, independently training over 10 expert models, each covering one domain (math, code, Agent, instruction following), with each domain having three reasoning intensity variants (Non-think / Think High / Think Max). Each expert contributes with per-expert weight <span><span style="color: inherit;"></span><span id="MathJax-Element-8-Frame"'),

    (' 加权贡献：</p>',
     ' weighted contribution:</p>'),

    ('<p>系统在任何给定提示上，自动路由到对应领域的专家获取监督信号。</p>',
     '<p>The system automatically routes to the corresponding domain expert for supervision signals on any given prompt.</p>'),

    ('<p><b>大→小跨尺度蒸馏（Qwen3）</b>：教师固定为旗舰模型（Qwen3-235B-A22B 或 Qwen3-32B），学生是 0.6B 到 30B 的 6 个轻量模型。这是四家中尺度跨度最大的 OPD 应用，旨在将旗舰模型的 thinking/non-thinking 双模式能力整体迁移到边缘侧模型。</p>',
     '<p><b>Large→small cross-scale distillation (Qwen3)</b>: The teacher is fixed as the flagship model (Qwen3-235B-A22B or Qwen3-32B), with students being 6 lightweight models from 0.6B to 30B. This is the widest scale-spanning OPD application among the four, aiming to transfer the flagship model\'s dual thinking/non-thinking mode capabilities entirely to edge-side models.</p>'),

    # 2.4 Position in Pipeline - Table
    ('<th>模型</th><th>OPD 在 pipeline 中的位置</th><th>核心功能定位</th>',
     '<th>Model</th><th>OPD Position in Pipeline</th><th>Core Function</th>'),

    ('<td>Qwen3</td><td>轻量模型独立子流水线</td><td>替代完整 RL，效率优先</td>',
     '<td>Qwen3</td><td>Independent sub-pipeline for lightweight models</td><td>Replaces full RL, efficiency-first</td>'),

    ('<td>GLM-5</td><td>最终收尾阶段</td><td>防灾难性遗忘，能力恢复</td>',
     '<td>GLM-5</td><td>Final wrap-up stage</td><td>Prevents catastrophic forgetting, capability recovery</td>'),

    ('<td>MiMo</td><td>主体第三阶段</td><td>多专家能力整合</td>',
     '<td>MiMo</td><td>Main third stage</td><td>Multi-expert capability integration</td>'),

    ('<td>DeepSeek V4</td><td>统一化阶段（替代 mixed RL）</td><td>10+ 专家知识压缩入单模型</td>',
     '<td>DeepSeek V4</td><td>Unification stage (replaces mixed RL)</td><td>Compresses 10+ expert knowledge into a single model</td>'),

    # ── Section 3.1 Qwen3 ──
    ('<p>Qwen3 是这轮 OPD 浪潮的先行者，但其使用场景颇为务实：旗舰模型（Qwen3-235B-A22B 和 Qwen3-32B）走完了完整的四阶段 RL 流水线（Long-CoT Cold Start → Reasoning RL → Thinking Mode Fusion → General RL），OPD 专门用于降低<b>轻量模型</b>的训练成本。</p>',
     '<p>Qwen3 is the pioneer of this OPD wave, though its use case is pragmatic: the flagship models (Qwen3-235B-A22B and Qwen3-32B) went through the complete four-stage RL pipeline (Long-CoT Cold Start → Reasoning RL → Thinking Mode Fusion → General RL), while OPD was specifically used to reduce the training cost of <b>lightweight models</b>.</p>'),

    ('<p>Qwen3 的 Strong-to-Weak Distillation 分两步走。第一步是 off-policy 蒸馏：收集教师（旗舰模型）在 <code>/think</code> 和 <code>/no_think</code> 两种模式下的输出，做标准 SFT，让学生建立基础的双模式切换能力。第二步才是 on-policy 蒸馏：学生从自身分布采样轨迹，对齐教师 logit，最小化 KL 散度。两阶段串行设计的思路是：off-policy 先为学生 " 打好底 "，避免 on-policy 阶段一开始因为学生输出质量太差导致教师信号噪声过大。</p>',
     '<p>Qwen3\'s Strong-to-Weak Distillation proceeds in two steps. The first step is off-policy distillation: collect teacher (flagship model) outputs in <code>/think</code> and <code>/no_think</code> modes, perform standard SFT, and give the student basic dual-mode switching capability. The second step is on-policy distillation: the student samples trajectories from its own distribution, aligns to teacher logits, and minimizes KL divergence. The rationale for this two-stage serial design: off-policy first "lays the foundation" for the student, preventing excessive noise in the teacher signal during the early on-policy stage due to poor student output quality.</p>'),

    ('<p>效果是戏剧性的。Qwen3-30B-A3B（总参数 30B，激活 3B）通过 OPD 获得的推理能力，可以与 QwQ-32B（32B 全激活）相当；Qwen3-0.6B 也明显超越 Qwen2.5-1.5B 同规模对手。整个轻量模型系列的训练只需要旗舰四阶段 RL 的 <b>1/10 GPU 时间</b>。</p>',
     '<p>The results are dramatic. Qwen3-30B-A3B (30B total parameters, 3B active) achieved reasoning capabilities through OPD comparable to QwQ-32B (32B fully active); Qwen3-0.6B also clearly surpassed Qwen2.5-1.5B and other same-scale competitors. The entire lightweight model series required only <b>1/10 of the GPU time</b> of flagship four-stage RL training.</p>'),

    ('<p>这个数字值得停下来想一想：为 6 个不同规模的轻量模型做完整 RL，本来需要 6 倍的旗舰训练成本；通过 OPD，总代价压缩到旗舰成本的 1/10。这是量产强推理小模型的关键使能技术。</p>',
     '<p>This number is worth pausing to consider: doing full RL for 6 lightweight models at different scales would require 6x the flagship training cost; through OPD, the total cost is compressed to 1/10 of flagship cost. This is the key enabling technology for mass-producing strong reasoning small models.</p>'),

    # 3.2 GLM-5
    ('<p>GLM-5（智谱 AI &amp; 清华大学）的后训练设计了一条雄心勃勃的四阶段 RL 流水线：Overall SFT → Reasoning RL → Agentic RL → General RL。每个阶段针对不同的能力维度：Reasoning RL 覆盖数学、科学、代码、工具集成推理（TIR）四个领域；Agentic RL 覆盖 SWE、终端任务、多步搜索；General RL 针对教学正确性、情感智能、任务专项质量三个维度。</p>',
     '<p>GLM-5 (Zhipu AI &amp; Tsinghua University) designed an ambitious four-stage RL pipeline for post-training: Overall SFT → Reasoning RL → Agentic RL → General RL. Each stage targets different capability dimensions: Reasoning RL covers math, science, code, and tool-integrated reasoning (TIR); Agentic RL covers SWE, terminal tasks, and multi-step search; General RL targets instructional correctness, emotional intelligence, and task-specific quality.</p>'),

    ('<p>问题随之而来：顺序优化多个目标，天然存在<b>灾难性遗忘（catastrophic forgetting）</b>。General RL 阶段的偏好对齐训练会侵蚀 Reasoning RL 积累的推理能力；Agentic RL 对长轨迹的强化会改变模型的输出风格，影响 General RL 后来想建立的自然语言质量。</p>',
     '<p>The problem follows naturally: sequentially optimizing multiple objectives inherently suffers from <b>catastrophic forgetting</b>. Preference alignment training in the General RL stage erodes the reasoning capabilities accumulated during Reasoning RL; Agentic RL\'s reinforcement of long trajectories changes the model\'s output style, affecting the natural language quality that General RL later tries to establish.</p>'),

    ('<p>GLM-5 的解法是将 OPD 作为<b>最终收尾阶段</b>（Section 3.5，"On-Policy Cross-Stage Distillation"）：把 Reasoning RL 和 General RL 两个阶段的最终 checkpoint 同时作为教师，学生从自身分布采样，优化 reverse KL。由于教师就是同一个模型的前序版本，架构和词表完全对齐，logit 信号直接可用。</p>',
     '<p>GLM-5\'s solution is to use OPD as the <b>final wrap-up stage</b> (Section 3.5, "On-Policy Cross-Stage Distillation"): simultaneously use the final checkpoints from both the Reasoning RL and General RL stages as teachers, with the student sampling from its own distribution and optimizing reverse KL. Since the teachers are prior versions of the same model, architecture and vocabulary are perfectly aligned, making logit signals directly usable.</p>'),

    ('<p>一个精巧的实现细节：GRPO 在 RL 训练时，group size 通常设置为 32，目的是通过组内对比来估计 advantage 的基线。但在 OPD 阶段，advantage 直接由教师 log ratio 给出，无需组内对比，因此 group size 可以降至 <b>1</b>，batch size 则从 32 扩大到 1024，大幅提升数据吞吐。</p>',
     '<p>An elegant implementation detail: during RL training, GRPO typically sets group size to 32 to estimate advantage baselines through within-group comparison. But in the OPD stage, the advantage is directly given by the teacher log ratio, eliminating the need for within-group comparison, so group size can be reduced to <b>1</b>, while batch size expands from 32 to 1024, dramatically increasing data throughput.</p>'),

    ('<p>OPD 让 GLM-5 在最终评测上实现了各项能力的同时在线：在 LMArena 中文本和代码双排行榜登顶，Humanity\'s Last Exam 达 50.4，SWE-bench Verified 77.8，Terminal-Bench 2.0 56.2，均优于或持平 Claude Opus 4.5。</p>',
     '<p>OPD enabled GLM-5 to achieve simultaneous online capability across all metrics in the final evaluation: topping both text and code leaderboards on LMArena, reaching 50.4 on Humanity\'s Last Exam, 77.8 on SWE-bench Verified, and 56.2 on Terminal-Bench 2.0 — all matching or exceeding Claude Opus 4.5.</p>'),

    # 3.3 MiMo
    ('<p>小米 MiMo-V2-Flash 将 OPD（以 MOPD，Multi-Teacher On-Policy Distillation 命名）放在了后训练流水线的<b>核心位置</b>，而非收尾步骤。</p>',
     '<p>Xiaomi MiMo-V2-Flash placed OPD (named MOPD, Multi-Teacher On-Policy Distillation) at the <b>core</b> of the post-training pipeline, rather than as a finishing step.</p>'),

    ('<p>背景问题是 AI 后训练中普遍存在的 <b>see-saw effect</b>：同时提升数学推理会压制代码能力，提升代码能力又会损害通用对话质量。这是因为在一个统一参数空间内对多个目标同时做 RL，各目标的梯度方向会互相干扰。Weight merge（参数平均）是一种常见逃法，但实验一再证明会导致可观的性能损耗。</p>',
     '<p>The background problem is the <b>see-saw effect</b> prevalent in AI post-training: simultaneously improving math reasoning suppresses code capability, and improving code capability harms general conversation quality. This is because doing RL on multiple objectives simultaneously within a unified parameter space causes gradient directions to interfere with each other. Weight merge (parameter averaging) is a common escape route, but experiments repeatedly show it leads to substantial performance degradation.</p>'),

    ('<p>MiMo 的三阶段方案：Stage 1 是通用 SFT 建立基础；Stage 2 是独立的领域专家 RL 训练（代码 Agent、搜索 Agent、数学、通用推理、安全对齐各自独立优化，互不干扰）；Stage 3 是 MOPD，用各领域专家的 logit 分布作为学生的学习信号，在 logit 空间而非参数空间完成能力整合。</p>',
     '<p>MiMo\'s three-stage approach: Stage 1 is general SFT to establish a foundation; Stage 2 is independent domain-expert RL training (code Agent, search Agent, math, general reasoning, and safety alignment each optimized independently without interference); Stage 3 is MOPD, using the logit distributions of each domain expert as learning signals for the student, completing capability integration in logit space rather than parameter space.</p>'),

    ('<p>技术上最有特色的是 MOPD 的 advantage 公式（Eq. 9）：</p>',
     '<p>The most technically distinctive aspect is MOPD\'s advantage formula (Eq. 9):</p>'),

    # π_domain_x part
    ('<script type="math/tex;mode=inline">\\pi_{\\text{domain}_x}</script></span></span> 是根据提示所属领域动态选取的教师策略。KL 项给出 dense 的 per-token 方向信号，ORM 项保留与可验证结果的端到端对齐，两者以系数 α 权衡。</p>',
     '<script type="math/tex;mode=inline">\\pi_{\\text{domain}_x}</script></span></span> is the teacher policy dynamically selected based on the prompt\'s domain. The KL term provides dense per-token directional signals, while the ORM term maintains end-to-end alignment with verifiable results, balanced by coefficient α.</p>'),

    ('<p>另一个创新是 <b>Rollout Routing Replay（R3）</b>：MoE 模型在推理时（rollout）和训练时（update）的 expert routing 可能不一致，这会引入梯度噪声。R3 通过缓存 rollout 时的 routing 决策并在训练时复现，保证两阶段 routing 一致，使 RL 训练更稳定。</p>',
     '<p>Another innovation is <b>Rollout Routing Replay (R3)</b>: MoE models may have inconsistent expert routing between inference time (rollout) and training time (update), which introduces gradient noise. R3 caches routing decisions during rollout and replays them during training, ensuring consistent routing across both stages and making RL training more stable.</p>'),

    ('<p>效果上，MOPD 在多个指标上让学生超越最强教师（Table 7）：AIME 2025 +0.2，HMMT Feb 2025 +1.8，LiveCodeBench +0.6，HLE +0.9。同时 SWE-Bench Verified 73.4% 登顶开源排行，SWE-Bench Multilingual 71.7%。</p>',
     '<p>In terms of results, MOPD enabled the student to surpass the strongest teacher on multiple metrics (Table 7): AIME 2025 +0.2, HMMT Feb 2025 +1.8, LiveCodeBench +0.6, HLE +0.9. Additionally, SWE-Bench Verified reached 73.4% topping open-source rankings, and SWE-Bench Multilingual 71.7%.</p>'),

    # 3.4 DeepSeek V4
    ('<p>DeepSeek V4 的后训练场景是这四家中最复杂的：需要整合 10 个以上独立训练的专家模型，每个专家针对一个领域，还有三种推理强度变体（Non-think / Think High / Think Max），对应不同的 length penalty 和 context window 设置。</p>',
     '<p>DeepSeek V4\'s post-training scenario is the most complex among the four: it needs to integrate over 10 independently trained expert models, each targeting one domain, with three reasoning intensity variants (Non-think / Think High / Think Max), corresponding to different length penalty and context window settings.</p>'),

    ('<p>传统方案的失败已有先例：参数合并（weight merge）导致各专家的尖锐能力在参数空间里 " 稀释 "；Mixed RL（同时对多领域做联合强化）则是 MiMo 所描述的 see-saw effect。DeepSeek V4 的选择是完全放弃 Mixed RL，将 OPD 设定为整个后训练的统一化终点。原文表述直接："the mixed Reinforcement Learning (RL) stage was entirely replaced by On-Policy Distillation (OPD)"。</p>',
     '<p>The failure of traditional approaches has precedent: weight merge causes the sharp capabilities of each expert to be "diluted" in parameter space; Mixed RL (joint reinforcement across multiple domains simultaneously) suffers from the see-saw effect described by MiMo. DeepSeek V4\'s choice was to completely abandon Mixed RL, setting OPD as the unified endpoint of the entire post-training pipeline. The original text states it directly: "the mixed Reinforcement Learning (RL) stage was entirely replaced by On-Policy Distillation (OPD)."</p>'),

    ('<p>DeepSeek V4 OPD 最显著的技术贡献是 <b>full-vocabulary logit distillation</b>，以及配套的工程基础设施。逻辑链条很清晰：既然用 10 个以上的万亿参数教师，就必须精确地从每个教师的完整分布中学习，token-level 近似的高方差会掩盖各专家的细微差异，导致统一化质量下降。</p>',
     '<p>DeepSeek V4 OPD\'s most significant technical contribution is <b>full-vocabulary logit distillation</b>, along with the supporting engineering infrastructure. The logic chain is clear: with over 10 trillion-parameter teachers, you must precisely learn from each teacher\'s complete distribution — the high variance of token-level approximation would mask subtle differences between experts, degrading unification quality.</p>'),

    ('<p>三层工程支持使得大规模全词表 OPD 成为现实：</p>',
     '<p>Three layers of engineering support make large-scale full-vocabulary OPD a reality:</p>'),

    ('<li><b>教师权重调度</b>（Teacher Weight Scheduling）：10 个以上万亿参数的教师权重无法常驻显存，系统将它们卸载到分布式存储，用 ZeRO-like 共享机制按需加载，每次 mini-batch 每个教师 head 只加载一次</li>',
     '<li><b>Teacher Weight Scheduling</b>: With over 10 trillion-parameter teachers, weights cannot reside in GPU memory. The system offloads them to distributed storage, using a ZeRO-like sharing mechanism to load on demand, loading each teacher head only once per mini-batch.</li>'),

    ('<li><b>Hidden State 缓存</b>：教师 forward pass 只缓存最后一层 hidden state，需要 logit 时实时经过 prediction head 重建，彻底消除词表维度的显存瓶颈</li>',
     '<li><b>Hidden State Caching</b>: The teacher forward pass only caches the last-layer hidden state, reconstructing logits on-the-fly through the prediction head when needed, completely eliminating the vocabulary-dimension memory bottleneck.</li>'),

    ('<li><b>TileLang 专用 kernel</b>：精确计算两个完整分布之间的 KL，加速运算并压制动态内存分配</li>',
     '<li><b>Dedicated TileLang Kernel</b>: Precisely computes KL between two full distributions, accelerating computation and suppressing dynamic memory allocation.</li>'),

    ('<p>结果是 DeepSeek-V4-Pro-Max 在知识密集型任务（HLE、Terminal Bench 2.0）上显著超越 GPT-5.2 和 Gemini-3.0-Pro，在 Agent 任务上持平甚至超越 Kimi-K2.6 和 GLM-5.1。</p>',
     '<p>The result: DeepSeek-V4-Pro-Max significantly surpasses GPT-5.2 and Gemini-3.0-Pro on knowledge-intensive tasks (HLE, Terminal Bench 2.0), and matches or exceeds Kimi-K2.6 and GLM-5.1 on Agent tasks.</p>'),

    # ── Section 4 Future Outlook ──
    ('<p>OPD 在不到一年内从边缘技术变为主流范式，接下来的演化方向已经初现轮廓。</p>',
     '<p>OPD has gone from a marginal technique to a mainstream paradigm in less than a year, and the contours of its next evolutionary directions are already visible.</p>'),

    ('<p>DeepSeek V4 已经证明全词表 KL 在理论和实践上都优于 token-level 近似。随着 hidden state 缓存和专用 kernel 的开源化（DeepSeek V4 已开源 TileLang），其他团队复制这套工程方案的成本将大幅降低。可以预期，未来 12-18 个月内，主要实验室的 OPD 实现会向全词表方向收敛。</p>',
     '<p>DeepSeek V4 has already proven that full-vocabulary KL is superior to token-level approximation in both theory and practice. As hidden state caching and dedicated kernels are open-sourced (DeepSeek V4 has open-sourced TileLang), the cost for other teams to replicate this engineering solution will drop significantly. It can be expected that within the next 12-18 months, major lab OPD implementations will converge toward full-vocabulary approaches.</p>'),

    ('<p>MiMo 的 MOPD 证明 KL + ORM（序列级结果奖励）的组合优于单独的任一方案。下一步自然演化是将 ORM 替换为 <b>Process Reward Model（PRM）</b>——对每个推理步骤而非最终答案打分。PRM 可以在轨迹中途识别 " 推理失误的关键 fork point"，与 OPD 的 per-token 信号在粒度上高度匹配。两者结合，可能是目前最密集的训练信号配置：教师 logit（全局方向）+ PRM（步骤正确性）+ ORM（最终结果）三重叠加。</p>',
     '<p>MiMo\'s MOPD proves that the combination of KL + ORM (sequence-level outcome reward) outperforms either component alone. The next natural evolution is to replace ORM with a <b>Process Reward Model (PRM)</b> — scoring each reasoning step rather than just the final answer. PRM can identify "critical fork points where reasoning goes wrong" mid-trajectory, matching the granularity of OPD\'s per-token signals perfectly. Combined, this could be the densest training signal configuration to date: teacher logit (global direction) + PRM (step correctness) + ORM (final outcome) — a triple overlay.</p>'),

    ('<p>MiMo 在论文中明确提出了一个前瞻性路线图：蒸馏产生的学生模型可以重新进入专家 RL 训练阶段，成为更强的下一代教师，再反哺下一代学生——形成自强化循环。这与 AlphaZero 的 self-play 范式在结构上高度相似，区别在于 OPD 框架让 " 教师 - 学生 " 角色的切换更加显式和可控。</p>',
     '<p>MiMo explicitly proposes a forward-looking roadmap in its paper: distillation-produced student models can re-enter the expert RL training stage, becoming stronger next-generation teachers, which in turn feed back into next-generation students — forming a self-reinforcing cycle. This is structurally highly similar to AlphaZero\'s self-play paradigm, with the difference that the OPD framework makes the "teacher-student" role switch more explicit and controllable.</p>'),

    ('<p>如果这个循环被验证有效，它意味着 OPD 不只是一次性的知识压缩操作，而是一种<b>持续改进机制</b>。每一代模型都可以在前一代的基础上自动提升，无需持续引入新的外部数据或人工标注。</p>',
     '<p>If this cycle is validated, it means OPD is not just a one-shot knowledge compression operation, but a <b>continuous improvement mechanism</b>. Each generation of models can automatically improve upon the previous generation without continuously introducing new external data or human annotations.</p>'),

    ('<p>DeepSeek V4 和 MiMo 都将百万 token 长上下文作为核心能力目标。但 OPD 面临一个显著的工程困难：在百万 token 长轨迹上做 on-policy 采样，推理成本极高；而计算完整轨迹每个 token 上的教师 logit，显存需求随序列长度线性增长。</p>',
     '<p>Both DeepSeek V4 and MiMo have made million-token long context a core capability goal. However, OPD faces a significant engineering difficulty: on-policy sampling on million-token long trajectories incurs extremely high inference cost; and computing teacher logits on every token of the full trajectory has memory requirements that grow linearly with sequence length.</p>'),

    ('<p>这个矛盾目前靠 " 分段采样 " 和 " 轨迹截断 " 缓解，但理论上并不完美。如何在超长上下文中设计高效的 OPD 采样策略（例如只在关键决策点做 OPD 更新，其余位置用 RL），是下一个值得攻关的工程问题。</p>',
     '<p>This contradiction is currently mitigated through "segmented sampling" and "trajectory truncation," but is not theoretically perfect. How to design efficient OPD sampling strategies in ultra-long contexts (e.g., only doing OPD updates at key decision points, using RL elsewhere) is the next engineering problem worth tackling.</p>'),

    ('<p>目前的 OPD 全部发生在训练阶段。一个更激进的方向是 <b>inference-time distillation</b>：在模型推理时，对于识别出的关键 "forking token"（决定推理路径走向的关键节点），实时查询教师模型的分布，在 beam search 或 sampling 过程中加入教师引导。</p>',
     '<p>Currently, all OPD happens during the training stage. A more radical direction is <b>inference-time distillation</b>: during model inference, for identified critical "forking tokens" (key nodes that determine reasoning path direction), query the teacher model\'s distribution in real-time, adding teacher guidance during beam search or sampling.</p>'),

    ('<p>这本质上是将 OPD 的信号从训练时延伸到推理时，让学生在每次推理中都能实时 " 请教 " 教师，而不是只在训练阶段学习一次就固化。thinkingmachines.ai 博客在实验中自然发现了 forking token 的存在——这些 token 上 OPD 的惩罚信号特别大，说明它们正是学生偏离教师正确路径的关键节点。将这种识别能力迁移到推理时，是一条逻辑上连贯的演化路径。</p>',
     '<p>This essentially extends OPD signals from training time to inference time, allowing the student to "consult" the teacher in real-time during every inference, rather than learning only once during training and freezing. The thinkingmachines.ai blog naturally discovered the existence of forking tokens in experiments — these tokens receive particularly large OPD penalty signals, indicating they are exactly the critical nodes where the student deviates from the teacher\'s correct path. Transferring this identification capability to inference time is a logically coherent evolutionary path.</p>'),

    ('<p>OPD 的核心贡献不仅在于训练效率，更在于它提供了一种<b>在 logit 空间而非参数空间整合知识</b>的方法论。</p>',
     '<p>OPD\'s core contribution lies not only in training efficiency, but more importantly in providing a methodology for <b>integrating knowledge in logit space rather than parameter space</b>.</p>'),

    ('<p>传统的知识整合方案（weight merge、adapter 叠加、混合 RL）都在参数空间操作，各专家能力的 " 干涉 " 不可避免。OPD 则绕开了这个问题：专家模型独立存在，它们的知识以 logit 分布的形式流入学生，而学生的参数在自身生成的轨迹上学习，两个空间的操作互不干扰。</p>',
     '<p>Traditional knowledge integration approaches (weight merge, adapter stacking, mixed RL) all operate in parameter space, where "interference" between expert capabilities is inevitable. OPD bypasses this problem: expert models exist independently, their knowledge flows into the student in the form of logit distributions, while the student\'s parameters learn on self-generated trajectories — operations in the two spaces do not interfere with each other.</p>'),

    ('<p>这一洞察被四家团队从不同角度独立发现，并相继写入各自的技术报告，说明它触及了某种更深层的结构性真理：<b>语言模型的能力，在 logit 空间比在参数空间更容易合并、迁移和保留。</b></p>',
     '<p>This insight was independently discovered by four teams from different angles and successively written into their tech reports, suggesting it touches on a deeper structural truth: <b>the capabilities of language models are easier to merge, transfer, and preserve in logit space than in parameter space.</b></p>'),

    ('<p>随着专家模型的规模和数量持续扩大，OPD 作为 " 能力压缩与整合 " 的核心工具，其重要性将只增不减。</p>',
     '<p>As the scale and number of expert models continue to grow, OPD\'s importance as the core tool for "capability compression and integration" will only increase.</p>'),

    ('<p><i>参考文献：Qwen3 Technical Report (2505.09388)；GLM-5: from Vibe Coding to Agentic Engineering (2602.15763)；MiMo-V2-Flash Technical Report (2601.02780)；DeepSeek-V4 Technical Report；On-Policy Distillation, thinkingmachines.ai</i></p>',
     '<p><i>References: Qwen3 Technical Report (2505.09388); GLM-5: from Vibe Coding to Agentic Engineering (2602.15763); MiMo-V2-Flash Technical Report (2601.02780); DeepSeek-V4 Technical Report; On-Policy Distillation, thinkingmachines.ai</i></p>'),
]

count = 0
for old, new in replacements:
    if old in html:
        html = html.replace(old, new)
        count += 1
    else:
        print(f'WARNING: Not found: {old[:80]}...')

print(f'Applied {count}/{len(replacements)} replacements')

with open('zhihu_article_2031101471563962191_en/article.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done!')
