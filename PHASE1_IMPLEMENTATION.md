# 🚀 Phase 1 Implementation Plan - Research Features

## Quick Wins: Build These First (2-3 days)

### Priority 1: RAG Pipeline Visualization ⭐⭐⭐
**Why:** Shows research credibility, transparency, visual appeal
**Effort:** Medium
**Impact:** High

#### Implementation Steps:

1. **Backend: Track RAG stages** (`api/rag_tracker.py`)
```python
class RAGTracker:
    def __init__(self):
        self.stages = []
    
    def track_query_encoding(self, query, embedding):
        self.stages.append({
            "stage": "encoding",
            "query": query,
            "embedding_preview": embedding[:10],  # First 10 dims
            "timestamp": time.time()
        })
    
    def track_retrieval(self, documents, scores):
        self.stages.append({
            "stage": "retrieval",
            "num_docs": len(documents),
            "top_scores": scores[:5],
            "documents": [{"text": d[:100], "score": s} 
                         for d, s in zip(documents[:5], scores[:5])]
        })
    
    def track_generation(self, context, response):
        self.stages.append({
            "stage": "generation",
            "context_length": len(context),
            "response_length": len(response),
            "attribution": self.extract_citations(response)
        })
```

2. **Frontend: RAG Pipeline Viewer** (add to `index.html`)
```html
<div class="rag-pipeline" id="rag-pipeline">
  <div class="stage" data-stage="encoding">
    <div class="stage-icon">🔍</div>
    <div class="stage-title">Query Encoding</div>
    <div class="stage-details">
      <div class="embedding-preview"></div>
    </div>
  </div>
  
  <div class="stage" data-stage="retrieval">
    <div class="stage-icon">📚</div>
    <div class="stage-title">Document Retrieval</div>
    <div class="retrieved-docs"></div>
  </div>
  
  <div class="stage" data-stage="generation">
    <div class="stage-icon">✍️</div>
    <div class="stage-title">Generation</div>
    <div class="citations"></div>
  </div>
</div>
```

3. **Styling: Research Lab Theme**
```css
.rag-pipeline {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Fira Code', monospace;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.stage {
  border-left: 3px solid #007acc;
  padding: 15px;
  margin: 10px 0;
  transition: all 0.3s;
}

.stage.active {
  border-left-color: #4ec9b0;
  background: #2d2d2d;
}

.embedding-preview {
  font-family: 'Courier New', monospace;
  background: #0e0e0e;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
```

---

### Priority 2: Attention Visualization ⭐⭐
**Why:** Shows interpretability, looks impressive, educational
**Effort:** Medium-High
**Impact:** Very High (visually stunning)

#### Implementation:

1. **Mock attention data in demo mode**
```python
def generate_attention_heatmap(query: str, response: str):
    """Generate synthetic attention weights for demo."""
    query_tokens = query.split()
    response_tokens = response.split()[:20]  # First 20 tokens
    
    # Simulate attention: query tokens attend to relevant response tokens
    attention = np.random.rand(len(query_tokens), len(response_tokens))
    
    # Add some structure (diagonal-ish for realistic look)
    for i in range(len(query_tokens)):
        attention[i, i:i+3] *= 2  # Boost nearby tokens
    
    attention = softmax(attention, axis=1)
    
    return {
        "query_tokens": query_tokens,
        "response_tokens": response_tokens,
        "attention_weights": attention.tolist()
    }
```

2. **Interactive heatmap with Plotly or D3.js**
```javascript
function renderAttentionHeatmap(data) {
  const trace = {
    x: data.response_tokens,
    y: data.query_tokens,
    z: data.attention_weights,
    type: 'heatmap',
    colorscale: 'Viridis',
    hoverongaps: false
  };
  
  const layout = {
    title: 'Attention Pattern: Query → Response',
    xaxis: { title: 'Response Tokens' },
    yaxis: { title: 'Query Tokens' },
    paper_bgcolor: '#1e1e1e',
    plot_bgcolor: '#1e1e1e',
    font: { color: '#d4d4d4' }
  };
  
  Plotly.newPlot('attention-heatmap', [trace], layout);
}
```

---

### Priority 3: Paper Citation System ⭐⭐⭐
**Why:** Academic credibility, research positioning
**Effort:** Low
**Impact:** High (perception)

#### Implementation:

1. **Paper database** (`api/papers.py`)
```python
RESEARCH_PAPERS = {
    "attention": {
        "title": "Attention is All You Need",
        "authors": "Vaswani et al.",
        "year": 2017,
        "venue": "NeurIPS",
        "url": "https://arxiv.org/abs/1706.03762",
        "citations": 87000,
        "summary": "Introduced the Transformer architecture using self-attention."
    },
    "rag": {
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "authors": "Lewis et al.",
        "year": 2020,
        "venue": "NeurIPS",
        "url": "https://arxiv.org/abs/2005.11401",
        "citations": 3200,
        "summary": "Combines retrieval with generation for factual QA."
    },
    "tot": {
        "title": "Tree of Thoughts: Deliberate Problem Solving with LLMs",
        "authors": "Yao et al.",
        "year": 2023,
        "venue": "NeurIPS",
        "url": "https://arxiv.org/abs/2305.10601",
        "citations": 450,
        "summary": "Explores multiple reasoning paths like human problem-solving."
    },
    # Add 15+ more papers...
}

def get_relevant_papers(feature: str) -> List[Dict]:
    """Return papers relevant to the current feature."""
    feature_paper_map = {
        "rag": ["rag", "dense_retrieval"],
        "attention": ["attention", "transformers"],
        "reasoning": ["tot", "cot", "self_consistency"],
        # ...
    }
    return [RESEARCH_PAPERS[p] for p in feature_paper_map.get(feature, [])]
```

2. **Citation widget**
```html
<div class="paper-citations">
  <div class="citation-header">
    📚 Research Foundations
  </div>
  <div class="citation-list">
    <div class="citation-item">
      <div class="citation-title">
        "Attention is All You Need"
      </div>
      <div class="citation-meta">
        Vaswani et al., NeurIPS 2017 | 87k citations
      </div>
      <div class="citation-actions">
        <a href="#" class="btn-citation">PDF</a>
        <a href="#" class="btn-citation">Code</a>
        <a href="#" class="btn-citation">Cite</a>
      </div>
    </div>
  </div>
</div>
```

---

### Priority 4: Uncertainty Quantification ⭐⭐
**Why:** Shows sophistication, useful for users
**Effort:** Low-Medium
**Impact:** Medium-High

#### Implementation:

1. **Confidence estimation** (demo mode)
```python
def estimate_confidence(query: str, response: str, mode: str) -> Dict:
    """
    Estimate confidence based on heuristics.
    In production, use actual model logits.
    """
    # Heuristics for demo
    confidence_base = 0.7
    
    # Boost confidence for technical mode (seems more certain)
    if mode == "technical":
        confidence_base += 0.1
    
    # Lower confidence for vague queries
    if len(query.split()) < 5:
        confidence_base -= 0.15
    
    # Add some noise for realism
    confidence = confidence_base + np.random.uniform(-0.1, 0.1)
    confidence = np.clip(confidence, 0.3, 0.95)
    
    # Estimate epistemic vs aleatoric
    epistemic = confidence * 0.6  # Model uncertainty
    aleatoric = confidence * 0.4  # Data ambiguity
    
    return {
        "overall": round(confidence, 2),
        "epistemic": round(epistemic, 2),
        "aleatoric": round(aleatoric, 2),
        "calibration_error": round(abs(confidence - 0.8), 3),
        "interpretation": interpret_confidence(confidence)
    }

def interpret_confidence(conf: float) -> str:
    if conf > 0.85:
        return "High confidence - well-established knowledge"
    elif conf > 0.65:
        return "Moderate confidence - generally accurate"
    else:
        return "Low confidence - consider verifying independently"
```

2. **Confidence gauge widget**
```html
<div class="confidence-gauge">
  <div class="gauge-header">Confidence Analysis</div>
  
  <div class="gauge-visual">
    <svg viewBox="0 0 200 100">
      <!-- Arc background -->
      <path d="M 20,80 A 60,60 0 0,1 180,80" 
            stroke="#333" stroke-width="20" fill="none"/>
      
      <!-- Confidence arc (dynamic) -->
      <path id="confidence-arc" 
            d="M 20,80 A 60,60 0 0,1 180,80" 
            stroke="url(#confidence-gradient)" 
            stroke-width="20" 
            fill="none"
            stroke-dasharray="251.2"
            stroke-dashoffset="125.6"/>
      
      <defs>
        <linearGradient id="confidence-gradient">
          <stop offset="0%" stop-color="#f56565"/>
          <stop offset="50%" stop-color="#f6ad55"/>
          <stop offset="100%" stop-color="#48bb78"/>
        </linearGradient>
      </defs>
    </svg>
    
    <div class="gauge-value">76%</div>
  </div>
  
  <div class="uncertainty-breakdown">
    <div class="uncertainty-item">
      <span class="label">Epistemic (Model)</span>
      <div class="bar" style="width: 60%"></div>
    </div>
    <div class="uncertainty-item">
      <span class="label">Aleatoric (Data)</span>
      <div class="bar" style="width: 85%"></div>
    </div>
  </div>
</div>
```

---

## Integration Plan

### Step 1: Update `api/ask.py`
Add these fields to response:
```python
{
  "result": "...",
  "research_data": {
    "rag_pipeline": {...},  # RAG stages
    "attention": {...},      # Attention weights
    "confidence": {...},     # Uncertainty metrics
    "papers": [...]          # Relevant citations
  }
}
```

### Step 2: Update `public/index.html`
Add new sections:
```html
<div class="research-panel" style="display:none" id="research-panel">
  <div class="panel-tabs">
    <button class="tab active" data-tab="rag">RAG Pipeline</button>
    <button class="tab" data-tab="attention">Attention</button>
    <button class="tab" data-tab="confidence">Confidence</button>
    <button class="tab" data-tab="papers">Papers</button>
  </div>
  
  <div class="panel-content">
    <div id="rag-tab" class="tab-pane active"></div>
    <div id="attention-tab" class="tab-pane"></div>
    <div id="confidence-tab" class="tab-pane"></div>
    <div id="papers-tab" class="tab-pane"></div>
  </div>
</div>

<button id="toggle-research" class="btn-toggle">
  🔬 Show Research Details
</button>
```

### Step 3: Add Dependencies
```bash
# For visualization
npm install plotly.js d3

# Or use CDN in HTML
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
```

---

## Timeline

**Day 1:**
- ✅ Set up paper database
- ✅ Add citation widget
- ✅ Basic confidence estimation
- ✅ Update response structure

**Day 2:**
- ✅ Implement RAG tracker (mock data)
- ✅ Build RAG pipeline UI
- ✅ Style research panel
- ✅ Add confidence gauge

**Day 3:**
- ✅ Generate attention heatmaps
- ✅ Integrate Plotly visualization
- ✅ Polish animations
- ✅ Test & deploy

---

## Success Criteria

✓ Users can toggle "Research Mode"
✓ 4 interactive visualizations working
✓ 10+ papers cited with links
✓ Confidence scores shown per response
✓ Dark theme, monospace aesthetic
✓ Export visualizations as images
✓ Mobile responsive

---

## Next Phase Preview

Once Phase 1 is solid, Phase 2 adds:
- 🌳 Tree-of-Thoughts interactive explorer
- 🕸️ Knowledge graph visualization
- 🧠 Cognitive load real-time monitor
- 📊 A/B testing dashboard

**Ready to start implementing?** Let's begin with the paper citation system (easiest) or RAG pipeline (most visual impact)?
