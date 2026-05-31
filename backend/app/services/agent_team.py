"""
EduNova.AI Agent Team Engine
============================
Implements a cooperative multi-agent system consisting of:
- OrchestratorAgent (Coordinator/Router)
- ProfessorAgent (Academic Content Specialist)
- ExaminerAgent (Assessment & Quiz Specialist)
- AcademicPlannerAgent (Study Planner & Exam Strategy Specialist)
- VisualizerAgent (Diagram & Schema Specialist)
"""

import random
from typing import List, Dict, Any, Optional
from app.services.smart_engine import search_knowledge, get_best_match

class BaseAgent:
    def __init__(self, name: str, role: str, icon: str, description: str):
        self.name = name
        self.role = role
        self.icon = icon
        self.description = description

class ProfessorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Professor Agent",
            role="Academic Content Specialist",
            icon="🎓",
            description="Explains complex concepts, definitions, and analogies in detail."
        )

    def generate(self, query: str, subject_name: str, topic_name: str, match: Optional[dict] = None) -> str:
        if not match:
            # Generate a structured academic fallback response
            return (
                f"### Academic Analysis: {topic_name or query}\n\n"
                f"To understand **{topic_name or query}** in {subject_name or 'Engineering'}, let's break down the fundamental principles:\n\n"
                f"1. **Core Definition**: This topic concerns key architectural and logical structures in the curriculum.\n"
                f"2. **Real-world Analogy**: Think of this concept like components working in a modular machine, where each part has specific input and output constraints.\n"
                f"3. **Key Architectural Pillars**: Review the underlying variables, bounds, and standard design principles to avoid edge-case failures in practice."
            )
        
        # Build professor response using the detailed notes from knowledge base
        title = match.get('title', topic_name)
        defn = match.get('definition', '')
        concepts = match.get('key_concepts', [])
        notes = match.get('detailed_notes', '')
        
        response_parts = [
            f"### 🎓 Professor's Lecture: {title}\n",
            f"**Formal Academic Definition:** {defn}\n",
            "#### Conceptual Breakdown:"
        ]
        
        for i, c in enumerate(concepts[:4], 1):
            response_parts.append(f"{i}. **{c}**: A core pillar defining this topic's behavior and application.")
            
        if notes:
            response_parts.append(f"\n#### Deep-Dive Lecture Notes:\n{notes}")
            
        return "\n".join(response_parts)

class ExaminerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Examiner Agent",
            role="Assessment & Quiz Specialist",
            icon="📝",
            description="Generates practice questions, exams, and evaluates student understanding."
        )

    def generate(self, query: str, subject_name: str, topic_name: str, match: Optional[dict] = None) -> str:
        response_parts = [f"### 📝 Examiner's Assessment & Practice Board Quiz\n"]
        
        if match and match.get('questions'):
            questions = match['questions']
            response_parts.append(f"Here are targeted exam questions for **{match.get('title', topic_name)}**:")
            for i, q in enumerate(questions[:3], 1):
                q_type = q.get('type', 'descriptive').upper()
                marks = q.get('marks', 10)
                response_parts.append(f"\n**Q{i}. [{marks} Marks] [{q_type}]**\n{q.get('q')}")
                if q.get('options'):
                    response_parts.append(f"*Options:* {', '.join(q['options'])}")
                response_parts.append(f"\n> **Model Answer/Explanation:** {q.get('a')}")
        else:
            # Fallback quiz generation
            topic_str = topic_name or query or "your syllabus"
            response_parts.append(
                f"Let's test your understanding of **{topic_str}**.\n\n"
                f"**Question 1: [8 Marks] [Descriptive]**\n"
                f"Define the key requirements and constraints when implementing **{topic_str}** and list its main limitations.\n"
                f"> **Model Answer Guidelines**: Your answer should list a formal definition, sketch the structural blocks, and highlight at least 3 pros/cons.\n\n"
                f"**Question 2: [2 Marks] [MCQ]**\n"
                f"Which of the following is the primary objective of studying {topic_str}?\n"
                f"A) Eliminating complexity\n"
                f"B) Optimizing resources & correct operation\n"
                f"C) Purely academic interest\n"
                f"D) Standardizing filenames\n"
                f"*Correct Answer:* B. Optimization and correctness are the main goals."
            )
            
        return "\n".join(response_parts)

class AcademicPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Academic Planner",
            role="Exam Strategy Specialist",
            icon="📅",
            description="Provides exam strategy, time allocation, and university study guidelines."
        )

    def generate(self, query: str, subject_name: str, topic_name: str, match: Optional[dict] = None) -> str:
        response_parts = [f"### 📅 Academic Planner & Exam Strategy"]
        
        # Add schedule strategy
        response_parts.append(
            f"\nTo prepare for **{topic_name or query}** within your study plan:\n"
            f"- **Target Weightage**: Typically carries 8-10 marks in semester examinations.\n"
            f"- **Time Allocation**: Spend approximately 60-90 minutes mastering the theoretical definitions and at least 30 minutes tracing numericals or code examples.\n"
            f"- **Study Technique**: Active recall using syllabus topics and immediate practice of past paper questions."
        )
        
        if match and match.get('exam_tips'):
            response_parts.append(f"\n#### 🎯 Exam Day Tips for Maharashtra University Paper:\n> [!IMPORTANT]\n> {match['exam_tips']}")
            
        if match and match.get('formulas'):
            response_parts.append("\n#### 🔢 Key Formula Cheat Sheet to Memorize:")
            for f in match['formulas']:
                response_parts.append(f"- {f}")
                
        return "\n".join(response_parts)

class VisualizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Visualizer Agent",
            role="Diagram & Schema Specialist",
            icon="📊",
            description="Creates structural maps, ASCII charts, and comparisons."
        )

    def generate(self, query: str, subject_name: str, topic_name: str, match: Optional[dict] = None) -> str:
        title = match.get('title', topic_name) if match else (topic_name or query)
        concepts = match.get('key_concepts', []) if match else ["Introduction", "Analysis", "Implementation", "Mastery"]
        
        # Create an ASCII structure representation
        ascii_box = (
            f"```text\n"
            f"       +--------------------------------------------+\n"
            f"       |             TOPIC: {title[:30]:<30} |\n"
            f"       +---------------------+----------------------+\n"
            f"                             |\n"
            f"              +--------------+--------------+\n"
            f"              |                             |\n"
            f"      +-------v-------+             +-------v-------+\n"
            f"      |   Concept A   |             |   Concept B   |\n"
            f"      | {concepts[0][:13]:<13} |             | {concepts[1][:13]:<13} |\n"
            f"      +---------------+             +---------------+\n"
            f"```"
        )
        
        response_parts = [
            f"### 📊 Visual Schema: {title}\n",
            "Here is the conceptual flow for this topic:",
            ascii_box,
            "\n#### Core Relationships:"
        ]
        
        for c in concepts[:3]:
            response_parts.append(f"- **{c}** is structurally connected to the main parameters of {title}.")
            
        return "\n".join(response_parts)

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Coordinator Agent",
            role="Multi-Agent Orchestrator",
            icon="🤖",
            description="Coordinates specialized agents, tracks thoughts, and synthesizes unified responses."
        )
        self.professor = ProfessorAgent()
        self.examiner = ExaminerAgent()
        self.planner = AcademicPlannerAgent()
        self.visualizer = VisualizerAgent()

    def generate_orchestrated(self, query: str, subject_name: str, topic_name: str, match: Optional[dict] = None) -> str:
        # 1. Generate the agent thoughts trace
        target_name = match.get('title', topic_name) if match else (topic_name or "General Topic")
        
        thoughts = [
            "[AGENT_THOUGHTS]",
            f"*   **Coordinator Agent**: Received user query about \"{query}\" under subject \"{subject_name}\" (resolved topic: \"{target_name}\"). Delegating to agent specialists...",
            f"*   **Professor Agent**: Preparing detailed academic explanation and referencing underlying concepts in the knowledge base.",
            f"*   **Examiner Agent**: Sourcing relevant test questions and MCQs for student self-assessment.",
            f"*   **Academic Planner**: Formulating university exam strategies and planning priority weightage."
        ]
        if match and match.get('key_concepts'):
            thoughts.append(f"*   **Visualizer Agent**: Constructing structural mental schema for key concepts: {', '.join(match['key_concepts'][:2])}.")
        thoughts.append("[/AGENT_THOUGHTS]\n")
        
        thoughts_str = "\n".join(thoughts)
        
        # 2. Get content from agents
        prof_content = self.professor.generate(query, subject_name, topic_name, match)
        exam_content = self.examiner.generate(query, subject_name, topic_name, match)
        plan_content = self.planner.generate(query, subject_name, topic_name, match)
        
        # Build unified final answer
        final_answer = (
            f"{prof_content}\n\n"
            f"---\n\n"
            f"{plan_content}\n\n"
            f"---\n\n"
            f"{exam_content}\n\n"
            f"*Self-assess using the questions above to lock in your understanding!*"
        )
        
        return thoughts_str + final_answer
