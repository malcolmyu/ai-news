# Agent Memory 全面调研：6 大派系 × 3 种采集策略

## 背景

Agent 记忆（Memory）是让 LLM Agent 跨越单次对话、具备持久化能力的关键基建。本文系统梳理了当前主流的 Agent Memory 实现方案，从**组织方式**和**采集策略**两个维度展开。

---

## 一、六种记忆组织范式

### 1. Prompt 注入派（Mem0、Mem9）

拦截每次 LLM 调用 → embedding 检索记忆 → 拼进 system prompt。

- **Mem0**：embedding 余弦相似度 + **时间衰减重排序** + 重要性权重。写操作 50ms 内完成靠流式 embedding pool 复用和异步向量写
- **Mem9**：加知识图谱关系推理，做 `(entity A) -[relation]-> (entity B)` 路径检索

本质上是对 RAG 的精细化改造——把文档检索替换为记忆片段检索。

### 2. 状态机派（Letta / MemGPT）

虚拟上下文管理。把 LLM 上下文抽象成「主记忆区 + 归档区」：

- 主记忆区 = 当前上下文窗口
- 归档区 = 外部存储，模型通过 `archival_memory_search()` tool call **主动拉取**
- 好处：token 不浪费，只加载当下需要的记忆
- 代价：模型必须学会「何时主动检索」，失败就会遗忘

### 3. 经验池 / 决策回放

**OpenViking** — 最短的路径是 Agent 版的 cache 系统：
- 完成任务 → 压缩决策路径 → 写回记忆库
- 新任务触发 → 加载相关经验作为参考上下文
- 类似 RL 的 **Experience Replay**，只是经验是自然语言不是 Q-values

**Voyager**（NVIDIA/MineDojo）：
- 技能库 = 代码 + 执行日志，复用已验证的技能函数

**Reflexion**：
- Actor + Evaluator + Memory 三层
- Evaluator 判错误 → 写入记忆 → 下次 Actor 加载 self-reflection
- 让模型从自己的错误中学

### 4. 知识图谱结构化记忆

| 方案 | 核心 | 跨 session |
|---|---|---|
| LangChain Entity Memory | 每次对话提取实体 | ❌ 弱（单次） |
| Microsoft GraphRAG | LLM 图谱 + 社区摘要 + 分层检索 | ✅ |
| Memgraph / Neo4j | 图数据库存记忆 | ✅ |
| CrewAI LTM | 实体 + 关系图，共享给 Crew 内所有 Agent | ✅ |

**关键区别**：向量检索找「相似」，图检索找「关联」。两者正交。

### 5. 专用记忆中间件

- **Zep** — 最成熟独立记忆服务
  - 消息历史自动摘要
  - Session + Summary + Entity Extraction 三层
  - 延迟会话自动摘要（对话结束后异步提炼核心事实写入持久层）
  - 内置知识图谱
- **LangMem**（LangChain）— 记忆 service：store / search / update / consolidate
- **Google Cloud Memorystore for Agent** — 向量 + 关系 + 对话历史统一管理

**本质**：将记忆抽取为独立微服务，Agent 框架只管调用。

### 6. 系统级 / 隐式记忆

- **OpenAI 内置 Memory**（GPTs / ChatGPT）— 全黑箱，`persistent_pointer` 隐式注入
- **Apple Intelligence / Siri Memory** — 端侧 on-device，隐私优先
- **Anthropic Tool Use with Context** — 教模型调用 memory 工具（store / retrieve / forget），不做自动注入

---

## 二、四种记忆采集策略

### 1. 原始缓存 + 异步提炼（Zep、LangMem）

```
原始消息流 → 写入消息队列 → 异步 pipeline 并行处理
├── 文本摘要 → summary 记忆
├── 实体提取 → Entity Knowledge Graph
├── 对话分类 → session type / topic
└── 重要性评分 → 决定保留或丢弃
```

**不阻塞主流程**。Zep 默认延迟 5-10 秒。

### 2. 实时拦截 + 同步处理（Mem0、Mem9）

```
LLM call 被 middleware 拦截
→ 提取当前轮 user + assistant 消息
→ embedding 化
→ 本体抽取（Mem9：实体+关系）
→ 向量库 + 图库同步写入
→ 检索最新记忆注入 prompt
→ 放行 LLM call
```

代价：每次 LLM 调用多 100-300ms。

### 3. 会话结束批量提炼（MemGPT 早期策略、AutoGen）

- 运行时只记 raw 日志
- 对话结束或达到预设长度后一次性批量处理
- 对话中的记忆写入延迟一整个 session

### 4. 失败/成就驱动采集（Reflexion、OpenViking、Voyager）

| 触发条件 | 行为 |
|---|---|
| ❌ 错误/异常 | 记录错误 + 上下文 + 修复决策 |
| 🏆 高置信度成功 | 记录最佳实践 |
| 🔁 重复失败 3 次 | 记录「此路不通」 |
| 🎯 目标完成 | 记录「此路可通」 |

**核心哲学**：99% 的对话是噪声，只存高信息密度的片段。

---

## 三、方案取舍矩阵

| | 方法 | 延迟 | 信息密度 | 实现复杂度 |
|---|---|---|---|---|
| Mem0/Mem9 | 实时 embedding | 低 (50-300ms) | 中 | 中 |
| Zep | 异步队列提炼 | 几乎无感知 | 高 | 高 |
| MemGPT | 会话结束批量 | 高 | 高 | 中 |
| Reflexion/Voyager | 失败/成就驱动 | 不规律 | 极高 | 低 |
| LangChain Entity | 实时提取 | 低 | 低（只存实体） | 低 |

---

## 四、推荐组合

```
粗召回 → RAG（向量 + BM25）
细检索 → GraphRAG / Entity Memory（关系推理）
温热 → 时间衰减（Mem0）/ 摘要合并（Zep）
```

最接近完整方案的工具组合：
- **Zep**：管 session 层（自动摘要、实体提取）+ 时间衰减温热
- **GraphRAG**：管深度关联检索 → 细推理
- **Reflexion**：管自我纠错 → 经验积累

**缺的那块**：目前没有工具能优雅处理「多 session 长尾记忆」而不爆炸 token。MemGPT 最接近但生态不成熟。

---

*调研日期：2026-05-12*
