# Agent Architecture Flow

## ✅ Yes! The System Follows: Perception → Memory → Decision → Action

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT EXECUTION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

USER QUERY
    ↓
    
┌────────────────────────────────────────────────────────────────┐
│  1️⃣  PERCEPTION (Perception.py)                                │
│  ───────────────────────────────────────────────────────────  │
│  ✓ process_user_input()                                        │
│    • Classify query type                                       │
│    • Extract key concepts                                      │
│    • Detect visualization needs                                │
│    • Apply RAG context (if BBC/Paint query)                    │
│    • Extract prompt facts                                      │
│                                                                 │
│  OUTPUT: perception_data {                                     │
│    query_type, key_concepts, requires_visualization,          │
│    rag_context, rag_recommendations, prompt_facts             │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
    ↓
    
┌────────────────────────────────────────────────────────────────┐
│  2️⃣  MEMORY (Memory.py)                                        │
│  ───────────────────────────────────────────────────────────  │
│  ✓ store_input() - User query                                 │
│  ✓ store_prompt_facts() - System instructions                 │
│  ✓ store_context_fact() - RAG context (if applicable)         │
│                                                                 │
│  ✓ Retrieves:                                                  │
│    • iteration_history                                         │
│    • performance_metrics                                       │
│    • function_usage                                            │
│    • context_facts                                             │
│                                                                 │
│  OUTPUT: memory_data {                                         │
│    iteration_history, iteration_summary, last_response,       │
│    performance_metrics, function_usage, context_facts         │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
    ↓
    
┌────────────────────────────────────────────────────────────────┐
│  3️⃣  DECISION (Decision_Making.py)                            │
│  ───────────────────────────────────────────────────────────  │
│  ✓ generate_decision()                                         │
│    • Analyze perception_data                                   │
│    • Analyze memory_data                                       │
│    • Inject RAG context into LLM prompt                        │
│    • Generate decision using Gemini AI                         │
│    • Parse response                                            │
│                                                                 │
│  OUTPUT: (decision_type, decision_data) {                     │
│    decision_type: "function_call" or "final_answer"           │
│    decision_data: {                                            │
│      function_name, arguments                                  │
│    }                                                           │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
    ↓
    
┌────────────────────────────────────────────────────────────────┐
│  4️⃣  ACTION (Action.py)                                        │
│  ───────────────────────────────────────────────────────────  │
│  ✓ execute_decision()                                          │
│    • execute_function_call() or handle_final_answer()         │
│    • Call MCP tools via session                                │
│    • Track execution in memory                                 │
│    • Store results                                             │
│    • Handle visualization if needed                            │
│                                                                 │
│  OUTPUT: (success, result, vis_config) {                      │
│    success: True/False                                         │
│    result: Tool output or answer                              │
│    vis_config: Visualization config (if needed)               │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
    ↓
    
    BACK TO MEMORY (store_iteration, store_tool_call)
    ↓
    
    REPEAT LOOP (if more iterations needed)
    ↓
    
    FINAL ANSWER

```

---

## 📋 Code Flow Example (BBC Headlines)

### main.py (Lines 120-190)

```python
# 1️⃣ PERCEPTION
perception_data = await self.perception.process_user_input(user_query)

# Store in memory
self.memory.store_input(user_query, source="user")
self.memory.store_prompt_facts(perception_data.get("prompt_facts", {}))

# Get memory data for decision making
memory_data = {
    "iteration_history": self.memory.state["iteration_history"],
    "iteration_summary": self.memory.get_iteration_summary(),
    "last_response": self.memory.get_last_response(),
    "performance_metrics": self.memory.get_performance_metrics(),
    "function_usage": dict(self.memory.data_store.get("function_usage", {})),
    "context_facts": self.memory.data_store.get("context_facts", [])
}

# 3️⃣ DECISION
decision_type, decision_data = await self.decision_making.generate_decision(
    perception_data=perception_data,
    memory_data=memory_data,
    available_tools=tools
)

# 4️⃣ ACTION
success, result, visualization_config = await self.action.execute_decision(
    decision_type,
    decision_data,
    visualization_needed=perception_data.get("requires_visualization", False),
    memory_instance=self.memory  # ← Memory instance passed for tracking
)

# Store iteration back in memory
self.memory.store_iteration(
    current_iter,
    user_query,
    decision_data,
    result
)
```

### test_rag_bbc_agent.py (Lines 84-139)

```python
# 1️⃣ PERCEPTION
print("🔍 Step 1: Perception Processing...")
perception_data = await perception.process_user_input(user_query)

# Store in memory
memory.store_input(user_query, source="user")
memory.store_prompt_facts(perception_data.get("prompt_facts", {}))

# 2️⃣ MEMORY
memory_data = {
    "iteration_history": memory.state["iteration_history"],
    "iteration_summary": memory.get_iteration_summary(),
    "last_response": memory.get_last_response(),
    "performance_metrics": memory.get_performance_metrics(),
    "function_usage": dict(memory.data_store.get("function_usage", {})),
    "context_facts": memory.data_store.get("context_facts", [])
}

# 3️⃣ DECISION
print("🧠 Step 2: Decision Making (with RAG context)...")
decision_type, decision_data = await decision_making.generate_decision(
    perception_data=perception_data,
    memory_data=memory_data,
    available_tools=tools
)

# 4️⃣ ACTION
print("⚡ Step 3: Action Execution...")
success, result, vis_config = await action.execute_decision(
    decision_type=decision_type,
    decision_data=decision_data,
    visualization_needed=perception_data.get('requires_visualization', False),
    memory_instance=memory
)

# Store iteration in memory
memory.store_iteration(
    iteration=1,
    query=user_query,
    response=f"{decision_type}: {decision_data}",
    result=result
)
```

---

## 🔍 RAG Integration in Flow

### How RAG Fits In

```
PERCEPTION → RAG → MEMORY → DECISION → ACTION
     ↓         ↓               ↓
     
1️⃣ Perception.process_user_input():
   • Detects BBC/Paint keywords
   • Calls RAG.enhance_context()
   • Gets relevant documents
   • Gets function recommendations
   • Returns rag_context in perception_data

2️⃣ Memory.store_context_fact():
   • Stores RAG context for later reference

3️⃣ Decision_Making._build_enhanced_context_query():
   • Injects rag_context into LLM prompt
   • Provides contextual knowledge
   • Guides decision-making

4️⃣ Action.execute_decision():
   • Uses rag_recommendations to select tools
   • Tracks execution in memory
```

---

## 📊 Data Flow Between Modules

```
┌────────────────┐
│   Perception   │ → perception_data
└────────────────┘
       ↓
┌────────────────┐
│    Memory      │ ← Store data
│                │ → memory_data
└────────────────┘
       ↓
┌────────────────┐
│   Decision     │ → (decision_type, decision_data)
└────────────────┘
       ↓
┌────────────────┐
│     Action     │ ← Execute
│                │ → (success, result, vis_config)
└────────────────┘
       ↓
┌────────────────┐
│    Memory      │ ← Store results
└────────────────┘
       ↓
   [Loop back]
```

---

## ✅ Verification Checklist

| Step | Module | Function Called | Status |
|------|--------|-----------------|--------|
| 1 | Perception | `process_user_input()` | ✅ |
| 2 | Memory | `store_input()` | ✅ |
| 3 | Memory | `store_prompt_facts()` | ✅ |
| 4 | Memory | Get `memory_data` | ✅ |
| 5 | Decision | `generate_decision()` | ✅ |
| 6 | Action | `execute_decision()` | ✅ |
| 7 | Memory | `store_iteration()` | ✅ |
| 8 | Memory | `store_tool_call()` | ✅ |

---

## 🎯 Key Points

1. ✅ **Strict Sequential Flow**: Perception → Memory → Decision → Action
2. ✅ **Memory Integration**: Every step stores/retrieves from Memory
3. ✅ **RAG Enhancement**: Applied in Perception, used in Decision
4. ✅ **Iterative Loop**: Can repeat for multi-step tasks
5. ✅ **Complete Tracking**: All data flows through Memory
6. ✅ **Clean Separation**: Each module has distinct responsibility

---

## 📝 Summary

**YES!** The system strictly follows the **Perception → Memory → Decision → Action** pattern with:
- ✅ RAG integrated in Perception and Decision
- ✅ Memory tracking all steps
- ✅ Clean data flow between modules
- ✅ Iterative execution for complex tasks
- ✅ Complete implementation in both main.py and tests

**The architecture is production-ready and follows best practices!** 🎉

