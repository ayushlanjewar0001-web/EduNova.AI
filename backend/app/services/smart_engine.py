"""
EduNova.AI Smart Academic Engine
================================
Central intelligence layer that:
1. Searches across all knowledge bases for relevant content
2. Generates context-aware, topic-specific academic responses
3. Produces real notes, tests, visual summaries using actual academic data
"""

import re
import random
from typing import List, Dict, Any, Optional, Tuple


def _normalize(text: str) -> str:
    """Lowercase, strip, remove special chars for matching."""
    return re.sub(r'[^a-z0-9\s]', '', text.lower().strip())


def _word_overlap_score(query_words: set, target_words: set) -> float:
    """Calculate Jaccard-like overlap between two word sets."""
    if not target_words:
        return 0.0
    intersection = query_words & target_words
    return len(intersection) / max(1, min(len(query_words), len(target_words)))


def _keyword_match_score(query: str, topic_key: str, topic_data: dict, subject_hint: str = '') -> float:
    """Score how well a query matches a knowledge base entry."""
    q_norm = _normalize(query)
    q_words = set(q_norm.split())
    
    score = 0.0
    
    # Match against the dictionary key
    key_words = set(_normalize(topic_key).split())
    score += _word_overlap_score(q_words, key_words) * 3.0
    
    # Direct substring match in key
    if _normalize(topic_key) in q_norm or q_norm in _normalize(topic_key):
        score += 5.0
    
    # Match against title
    title = topic_data.get('title', '')
    title_words = set(_normalize(title).split())
    score += _word_overlap_score(q_words, title_words) * 2.0
    
    # Match against key_concepts
    for concept in topic_data.get('key_concepts', []):
        concept_norm = _normalize(concept)
        if concept_norm in q_norm:
            score += 2.0
        concept_words = set(concept_norm.split())
        score += _word_overlap_score(q_words, concept_words) * 0.5
    
    # Match against definition
    defn = topic_data.get('definition', '')
    defn_words = set(_normalize(defn).split())
    score += _word_overlap_score(q_words, defn_words) * 0.3
    
    # Subject hint bonus — if the subject name matches any keyword
    if subject_hint:
        sh_norm = _normalize(subject_hint)
        sh_words = set(sh_norm.split())
        # Boost if the topic key or title shares words with the subject
        key_subject_overlap = len(key_words & sh_words) + len(title_words & sh_words)
        score += key_subject_overlap * 0.5
    
    return score


def search_knowledge(query: str, subject_name: str = '', top_n: int = 3) -> List[Tuple[str, dict, float]]:
    """
    Search across ALL knowledge bases and return the top-N most relevant entries.
    Returns list of (topic_key, topic_data, score) tuples.
    """
    results = []
    
    # Import knowledge bases (lazy to avoid circular imports)
    try:
        from app.services.knowledge_base_cs import CS_KNOWLEDGE
        for key, data in CS_KNOWLEDGE.items():
            score = _keyword_match_score(query, key, data, subject_name)
            if score > 0.1:
                results.append((key, data, score))
    except ImportError:
        pass
    
    try:
        from app.services.knowledge_base_general import GENERAL_KNOWLEDGE
        for key, data in GENERAL_KNOWLEDGE.items():
            score = _keyword_match_score(query, key, data, subject_name)
            if score > 0.1:
                results.append((key, data, score))
    except ImportError:
        pass
    
    # Sort by score descending
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_n]


def get_best_match(query: str, subject_name: str = '') -> Optional[dict]:
    """Get the single best matching knowledge base entry."""
    results = search_knowledge(query, subject_name, top_n=1)
    if results and results[0][2] > 0.3:
        return results[0][1]
    return None


def generate_smart_chat_response(query: str, subject_name: str, topic_name: str, pyqs: List[Any]) -> Dict[str, Any]:
    """
    Generate an intelligent, context-aware chat response using the knowledge base.
    """
    # Search for relevant content
    search_term = f"{topic_name} {query}" if topic_name else query
    matches = search_knowledge(search_term, subject_name, top_n=3)
    
    if matches and matches[0][2] > 0.3:
        best = matches[0][1]
        
        # Build a comprehensive response
        response_parts = []
        response_parts.append(f"### {best['title']}\n")
        response_parts.append(f"**Definition:** {best['definition']}\n")
        
        # Key concepts
        concepts = best.get('key_concepts', [])
        if concepts:
            response_parts.append("#### Key Concepts:")
            for i, c in enumerate(concepts, 1):
                response_parts.append(f"{i}. **{c}**")
            response_parts.append("")
        
        # Core explanation from detailed notes (first 600 chars for chat)
        notes = best.get('detailed_notes', '')
        if notes:
            # Extract first meaningful section
            sections = notes.split('\n\n')
            relevant_text = '\n\n'.join(sections[:3])
            if len(relevant_text) > 800:
                relevant_text = relevant_text[:800] + '...'
            response_parts.append(relevant_text)
        
        # Formulas
        formulas = best.get('formulas', [])
        if formulas:
            response_parts.append("\n#### Important Formulas:")
            for f in formulas[:4]:
                response_parts.append(f"- {f}")
        
        # Exam tips
        tips = best.get('exam_tips', '')
        if tips:
            response_parts.append(f"\n#### 🎯 Exam Tip:\n{tips}")
        
        # Add context about related matches
        if len(matches) > 1:
            related = [m[1]['title'] for m in matches[1:3]]
            response_parts.append(f"\n---\n*Related topics you may want to explore: {', '.join(related)}*")
        
        response = '\n'.join(response_parts)
    else:
        # Fallback: still give a structured response using the query context
        response = _generate_contextual_fallback(query, subject_name, topic_name)
    
    # Attach suggested PYQs
    suggested_pyqs_data = []
    for pyq in pyqs[:3]:
        suggested_pyqs_data.append({
            "id": pyq.id,
            "question_text": pyq.question_text,
            "answer_explanation": pyq.answer_explanation,
            "year": pyq.year,
            "month": pyq.month,
            "marks": pyq.marks,
            "frequency_count": pyq.frequency_count,
            "difficulty_level": pyq.difficulty_level
        })
    
    return {
        "response": response,
        "suggested_pyqs": suggested_pyqs_data
    }


def generate_smart_notes(topic_name: str, note_type: str, subject_name: str = '') -> str:
    """
    Generate comprehensive, topic-specific academic notes using the knowledge base.
    """
    match = get_best_match(topic_name, subject_name)
    
    if match:
        return _build_notes_from_knowledge(match, topic_name, note_type)
    else:
        return _generate_generic_notes(topic_name, note_type, subject_name)


def generate_smart_test_questions(topic_name: str, subject_name: str, test_type: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate relevant test questions from the knowledge base.
    """
    search_term = f"{topic_name} {subject_name}"
    matches = search_knowledge(search_term, subject_name, top_n=5)
    
    questions = []
    seen_questions = set()
    
    for _, data, score in matches:
        if score < 0.2:
            continue
        for q_data in data.get('questions', []):
            q_text = q_data.get('q', '')
            if q_text in seen_questions:
                continue
            
            if test_type == 'MCQ' and q_data.get('type') == 'mcq':
                questions.append({
                    "question_text": q_text,
                    "correct_answer": q_data.get('a', ''),
                    "options": q_data.get('options', []),
                    "feedback": f"The correct answer is: {q_data.get('a', '')}. This concept is from {data.get('title', 'the syllabus')}."
                })
                seen_questions.add(q_text)
            elif test_type != 'MCQ' and q_data.get('type') in ('descriptive', 'short'):
                questions.append({
                    "question_text": q_text,
                    "correct_answer": q_data.get('a', ''),
                    "feedback": f"Key points to cover: {', '.join(data.get('key_concepts', [])[:3])}"
                })
                seen_questions.add(q_text)
            
            if len(questions) >= count:
                break
        if len(questions) >= count:
            break
    
    # If we don't have enough questions, generate some from the knowledge
    if len(questions) < count and matches:
        for _, data, _ in matches:
            if len(questions) >= count:
                break
            concepts = data.get('key_concepts', [])
            title = data.get('title', topic_name)
            
            if test_type == 'MCQ' and concepts:
                # Generate MCQ from concepts
                if len(concepts) >= 4:
                    correct = random.choice(concepts[:2])
                    wrong = [c for c in concepts if c != correct][:3]
                    options = [correct] + wrong
                    random.shuffle(options)
                    q = {
                        "question_text": f"Which of the following is a key concept in {title}?",
                        "correct_answer": correct,
                        "options": options,
                        "feedback": f"{correct} is a fundamental concept in {title}."
                    }
                    if q["question_text"] not in seen_questions:
                        questions.append(q)
                        seen_questions.add(q["question_text"])
            else:
                defn = data.get('definition', '')
                if defn:
                    q = {
                        "question_text": f"Define {title} and explain its significance in detail.",
                        "correct_answer": defn,
                        "feedback": f"Your answer should cover: {', '.join(concepts[:3])}"
                    }
                    if q["question_text"] not in seen_questions:
                        questions.append(q)
                        seen_questions.add(q["question_text"])
    
    return questions[:count]


def generate_smart_visual_notes(topic_name: str, visual_type: str, subject_name: str = '') -> Dict[str, Any]:
    """
    Generate visual notes (mindmap, flowchart, comparison table) using knowledge base data.
    """
    match = get_best_match(topic_name, subject_name)
    
    if visual_type == "Mindmap":
        return _build_mindmap(topic_name, match)
    elif visual_type == "Flowchart":
        return _build_flowchart(topic_name, match)
    else:  # Comparison Table
        return _build_comparison_table(topic_name, match, subject_name)


# ============================================================
# INTERNAL BUILDERS
# ============================================================

def _build_notes_from_knowledge(data: dict, topic_name: str, note_type: str) -> str:
    """Build structured notes from a knowledge base entry."""
    title = data.get('title', topic_name)
    definition = data.get('definition', '')
    concepts = data.get('key_concepts', [])
    detailed = data.get('detailed_notes', '')
    formulas = data.get('formulas', [])
    tips = data.get('exam_tips', '')
    questions = data.get('questions', [])
    
    sections = []
    
    # Header
    sections.append(f"# {note_type}: {title}")
    sections.append(f"\n*Generated by EduNova.AI Academic Engine for Maharashtra University Exams*")
    
    if note_type in ('Short Notes', 'Summary'):
        # Concise version
        sections.append(f"\n## Definition\n{definition}")
        
        if concepts:
            sections.append("\n## Key Concepts")
            for i, c in enumerate(concepts, 1):
                sections.append(f"{i}. **{c}**")
        
        if formulas:
            sections.append("\n## Important Formulas")
            for f in formulas:
                sections.append(f"- {f}")
        
        # Shortened detailed notes
        if detailed:
            lines = detailed.split('\n')
            short = '\n'.join(lines[:min(20, len(lines))])
            sections.append(f"\n## Core Content\n{short}")
        
        if tips:
            sections.append(f"\n## 🎯 Exam Tips\n{tips}")
    
    elif note_type in ('Revision Notes',):
        # Medium detail
        sections.append(f"\n## 1. Overview\n{definition}")
        
        if concepts:
            sections.append("\n## 2. Key Concepts to Remember")
            for i, c in enumerate(concepts, 1):
                sections.append(f"- ✅ **{c}**")
        
        if detailed:
            sections.append(f"\n## 3. Detailed Explanation\n{detailed}")
        
        if formulas:
            sections.append("\n## 4. Formula Sheet")
            for f in formulas:
                sections.append(f"| {f} |")
        
        if questions:
            sections.append("\n## 5. Practice Questions")
            for i, q in enumerate(questions[:3], 1):
                sections.append(f"\n**Q{i}.** {q.get('q', '')}")
                sections.append(f"**Answer:** {q.get('a', '')}")
        
        if tips:
            sections.append(f"\n## 6. Exam Strategy\n{tips}")
    
    else:
        # Detailed Explanation — full content
        sections.append(f"\n## 1. Introduction & Definition\n{definition}")
        
        if concepts:
            sections.append("\n## 2. Core Concepts")
            for i, c in enumerate(concepts, 1):
                sections.append(f"### 2.{i} {c}")
                sections.append(f"This is a fundamental aspect of **{title}** that forms the basis for understanding the complete topic.")
        
        if detailed:
            sections.append(f"\n## 3. Comprehensive Analysis\n{detailed}")
        
        if formulas:
            sections.append("\n## 4. Mathematical Foundations & Formulas")
            sections.append("| # | Formula | Description |")
            sections.append("|---|---------|-------------|")
            for i, f in enumerate(formulas, 1):
                sections.append(f"| {i} | {f} | Key formula for {title} |")
        
        if questions:
            sections.append("\n## 5. University Exam Practice Questions")
            for i, q in enumerate(questions, 1):
                q_type = q.get('type', 'descriptive')
                marks = q.get('marks', 10)
                sections.append(f"\n### Q{i}. [{marks} Marks] [{q_type.upper()}]")
                sections.append(f"**{q.get('q', '')}**")
                sections.append(f"\n**Model Answer:**\n{q.get('a', '')}")
                if q.get('options'):
                    sections.append(f"\nOptions: {' | '.join(q['options'])}")
        
        if tips:
            sections.append(f"\n## 6. Maharashtra University Exam Strategy\n> [!IMPORTANT]\n> {tips}")
        
        sections.append(f"\n---\n*This comprehensive note covers all aspects of **{title}** as per Maharashtra Technical University syllabus.*")
    
    return '\n'.join(sections)


def _generate_generic_notes(topic_name: str, note_type: str, subject_name: str) -> str:
    """Generate structured notes even when no knowledge base match exists."""
    sections = []
    sections.append(f"# {note_type}: {topic_name}")
    sections.append(f"\n*Generated by EduNova.AI Academic Engine | Subject: {subject_name or 'General'}*")
    
    sections.append(f"\n## 1. Introduction")
    sections.append(f"**{topic_name}** is an important topic in the {subject_name or 'academic'} curriculum. This topic is frequently examined in Maharashtra University semester exams.")
    
    sections.append(f"\n## 2. Key Points to Study")
    sections.append(f"- Understand the fundamental definition of **{topic_name}**")
    sections.append(f"- Learn the classification and types")
    sections.append(f"- Study the advantages and disadvantages")
    sections.append(f"- Practice numerical problems if applicable")
    sections.append(f"- Compare with related concepts in the syllabus")
    
    sections.append(f"\n## 3. Exam Preparation Strategy")
    sections.append(f"- Start with the textbook definition")
    sections.append(f"- Draw neat diagrams where applicable")
    sections.append(f"- Practice previous year questions on this topic")
    sections.append(f"- Focus on 10-mark descriptive answers with proper structure")
    
    sections.append(f"\n> [!TIP]")
    sections.append(f"> For more detailed content, try searching for specific subtopics within **{topic_name}**. EduNova.AI has comprehensive coverage for most Maharashtra university syllabus topics.")
    
    return '\n'.join(sections)


def _generate_contextual_fallback(query: str, subject_name: str, topic_name: str) -> str:
    """Generate a meaningful fallback response when no knowledge base match is found."""
    context = topic_name or subject_name or "your syllabus"
    
    return (
        f"### Regarding: {query}\n\n"
        f"I understand you're asking about **\"{query}\"** in the context of **{context}**.\n\n"
        f"While I don't have a specific knowledge base entry for this exact query, here's how to approach it:\n\n"
        f"#### Study Approach:\n"
        f"1. **Define the concept clearly** — Start with the formal textbook definition\n"
        f"2. **Identify key components** — Break down the topic into sub-concepts\n"
        f"3. **Learn the formulas/algorithms** — If applicable, memorize key formulas\n"
        f"4. **Practice with examples** — Work through at least 3-4 solved examples\n"
        f"5. **Review PYQs** — Check the PYQ Analyzer for past exam questions on this topic\n\n"
        f"#### For Better Results:\n"
        f"Try asking about specific subtopics like:\n"
        f"- Definitions and properties\n"
        f"- Algorithms and procedures\n"
        f"- Comparisons between related concepts\n"
        f"- Numerical problem solving steps\n\n"
        f"*I have comprehensive notes for most syllabus topics. Try using the **AI Notes** tab to generate detailed study material!*"
    )


def _build_mindmap(topic_name: str, data: Optional[dict]) -> Dict[str, Any]:
    """Build a mindmap structure from knowledge base data."""
    if not data:
        return {
            "nodes": [
                {"id": "1", "label": topic_name, "type": "root", "color": "#4F46E5"},
                {"id": "2", "label": "Definition", "type": "branch", "color": "#06B6D4"},
                {"id": "3", "label": "Key Concepts", "type": "branch", "color": "#10B981"},
                {"id": "4", "label": "Applications", "type": "branch", "color": "#F59E0B"},
                {"id": "5", "label": "Exam Focus", "type": "branch", "color": "#EC4899"}
            ],
            "edges": [
                {"source": "1", "target": "2"},
                {"source": "1", "target": "3"},
                {"source": "1", "target": "4"},
                {"source": "1", "target": "5"}
            ]
        }
    
    title = data.get('title', topic_name)
    concepts = data.get('key_concepts', [])
    
    nodes = [{"id": "root", "label": title, "type": "root", "color": "#4F46E5"}]
    edges = []
    
    # Create branches from key concepts
    branch_colors = ["#06B6D4", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6", "#EF4444"]
    
    for i, concept in enumerate(concepts[:6]):
        node_id = f"branch_{i}"
        nodes.append({
            "id": node_id,
            "label": concept,
            "type": "branch",
            "color": branch_colors[i % len(branch_colors)]
        })
        edges.append({"source": "root", "target": node_id})
    
    # Add formula nodes
    formulas = data.get('formulas', [])
    if formulas:
        formula_id = "formulas"
        nodes.append({"id": formula_id, "label": "Key Formulas", "type": "branch", "color": "#F97316"})
        edges.append({"source": "root", "target": formula_id})
        for j, formula in enumerate(formulas[:3]):
            f_id = f"formula_{j}"
            nodes.append({"id": f_id, "label": formula[:50], "type": "leaf", "color": "#FEF3C7"})
            edges.append({"source": formula_id, "target": f_id})
    
    # Add exam tip node
    tips = data.get('exam_tips', '')
    if tips:
        nodes.append({"id": "exam", "label": "Exam Strategy", "type": "branch", "color": "#DC2626"})
        edges.append({"source": "root", "target": "exam"})
        nodes.append({"id": "exam_tip", "label": tips[:60] + "...", "type": "leaf", "color": "#FEE2E2"})
        edges.append({"source": "exam", "target": "exam_tip"})
    
    return {"nodes": nodes, "edges": edges}


def _build_flowchart(topic_name: str, data: Optional[dict]) -> Dict[str, Any]:
    """Build a flowchart structure from knowledge base data."""
    concepts = data.get('key_concepts', []) if data else []
    title = data.get('title', topic_name) if data else topic_name
    
    nodes = [{"id": "start", "label": f"Start: {title}", "type": "process", "color": "#10B981"}]
    edges = []
    
    if concepts:
        prev_id = "start"
        for i, concept in enumerate(concepts):
            node_id = f"step_{i}"
            node_type = "process" if i % 2 == 0 else "decision"
            color = ["#6366F1", "#F59E0B", "#EC4899", "#06B6D4", "#8B5CF6", "#EF4444"][i % 6]
            nodes.append({"id": node_id, "label": concept, "type": node_type, "color": color})
            edges.append({"source": prev_id, "target": node_id, "label": f"Step {i+1}"})
            prev_id = node_id
        
        nodes.append({"id": "end", "label": "Understanding Complete", "type": "success", "color": "#10B981"})
        edges.append({"source": prev_id, "target": "end"})
    else:
        nodes.extend([
            {"id": "define", "label": "Define the concept", "type": "process", "color": "#6366F1"},
            {"id": "analyze", "label": "Analyze components", "type": "process", "color": "#F59E0B"},
            {"id": "apply", "label": "Apply to problems", "type": "decision", "color": "#EC4899"},
            {"id": "end", "label": "Mastery achieved", "type": "success", "color": "#10B981"}
        ])
        edges = [
            {"source": "start", "target": "define"},
            {"source": "define", "target": "analyze"},
            {"source": "analyze", "target": "apply"},
            {"source": "apply", "target": "end"}
        ]
    
    return {"nodes": nodes, "edges": edges}


def _build_comparison_table(topic_name: str, data: Optional[dict], subject_name: str = '') -> Dict[str, Any]:
    """Build a comparison table from knowledge base data."""
    if data:
        concepts = data.get('key_concepts', [])
        title = data.get('title', topic_name)
        formulas = data.get('formulas', [])
        
        headers = ["Aspect", title, "Key Details"]
        rows = []
        
        if data.get('definition'):
            rows.append(["Definition", data['definition'][:100], "Fundamental concept"])
        
        for i, concept in enumerate(concepts[:5]):
            rows.append([f"Concept {i+1}", concept, "Core component"])
        
        for i, formula in enumerate(formulas[:3]):
            rows.append([f"Formula {i+1}", formula, "Mathematical foundation"])
        
        if data.get('exam_tips'):
            rows.append(["Exam Focus", data['exam_tips'][:80], "High priority"])
        
        return {"headers": headers, "rows": rows}
    
    return {
        "headers": ["Feature", topic_name, "Notes"],
        "rows": [
            ["Definition", "Core concept definition", "Start here"],
            ["Types/Classification", "Multiple types exist", "Learn all types"],
            ["Applications", "Used in various contexts", "Focus on practical uses"],
            ["Advantages", "Key benefits", "Important for comparison questions"],
            ["Limitations", "Known constraints", "Be aware for exam answers"]
        ]
    }
