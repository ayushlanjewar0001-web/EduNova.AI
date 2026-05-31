"""
EduNova.AI Service Layer
=========================
Routes all AI features through the Smart Academic Engine for real, 
topic-specific responses powered by comprehensive knowledge bases.
"""

import json
import random
from datetime import date, timedelta
from typing import List, Dict, Any
from app.schemas import TopicFrequencyItem, PYQResponse
from app.services.smart_engine import (
    generate_smart_chat_response,
    generate_smart_notes,
    generate_smart_test_questions,
    generate_smart_visual_notes,
    search_knowledge,
    get_best_match
)


class AIService:
    @staticmethod
    def generate_chat_response(query: str, subject_name: str, topic_name: str, pyqs: List[Any], agent_role: str = "orchestrator") -> Dict[str, Any]:
        """
        Generate an intelligent, multi-agent powered chat response.
        """
        from app.services.agent_team import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        
        match = get_best_match(topic_name or query, subject_name)
        
        if agent_role == "professor":
            response = orchestrator.professor.generate(query, subject_name, topic_name, match)
        elif agent_role == "examiner":
            response = orchestrator.examiner.generate(query, subject_name, topic_name, match)
        elif agent_role == "planner":
            response = orchestrator.planner.generate(query, subject_name, topic_name, match)
        elif agent_role == "visualizer":
            response = orchestrator.visualizer.generate(query, subject_name, topic_name, match)
        else: # orchestrator
            response = orchestrator.generate_orchestrated(query, subject_name, topic_name, match)

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

    @staticmethod
    def generate_notes(topic_name: str, note_type: str, subject_name: str = '') -> str:
        """
        Generate comprehensive, topic-specific academic notes.
        """
        return generate_smart_notes(topic_name, note_type, subject_name)

    @staticmethod
    def generate_visual_notes(topic_name: str, visual_type: str, subject_name: str = '') -> Dict[str, Any]:
        """
        Generate visual study aids (mindmaps, flowcharts, comparison tables).
        """
        return generate_smart_visual_notes(topic_name, visual_type, subject_name)

    @staticmethod
    def generate_study_plan(student_id: int, subject_name: str, exam_date: date, daily_hours: float, topics: List[Any]) -> List[Dict[str, Any]]:
        """
        Generate an intelligent study plan that prioritizes topics based on
        knowledge base relevance and distributes study time evenly.
        """
        today = date.today()
        days_until_exam = (exam_date - today).days
        
        if days_until_exam <= 0:
            days_until_exam = 30
            
        plans = []
        topic_count = len(topics)
        if topic_count == 0:
            return []
        
        # Score topics by importance using the knowledge base
        topic_scores = []
        for topic in topics:
            match = get_best_match(topic.name, subject_name)
            score = 1.0
            if match:
                # Topics with more questions/formulas are more important
                score += len(match.get('questions', [])) * 0.5
                score += len(match.get('formulas', [])) * 0.3
                score += len(match.get('key_concepts', [])) * 0.2
            topic_scores.append((topic, score))
        
        # Sort by importance (higher score = more study time)
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        total_score = sum(s for _, s in topic_scores)
        
        # Phase 1: Important topics first (first 60% of days)
        # Phase 2: Review all topics (next 30% of days)
        # Phase 3: Revision of hardest topics (final 10% of days)
        
        phase1_days = int(days_until_exam * 0.6)
        phase2_days = int(days_until_exam * 0.3)
        phase3_days = days_until_exam - phase1_days - phase2_days
        
        day_idx = 0
        
        # Phase 1: Deep study of each topic, proportional to importance
        for topic, score in topic_scores:
            topic_days = max(1, int((score / total_score) * phase1_days))
            for d in range(topic_days):
                if day_idx >= phase1_days:
                    break
                current_date = today + timedelta(days=day_idx)
                plans.append({
                    "student_id": student_id,
                    "subject_name": subject_name,
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "scheduled_date": current_date,
                    "duration_minutes": int(daily_hours * 60),
                    "status": "Pending"
                })
                day_idx += 1
        
        # Phase 2: Cycle through all topics for review
        for i in range(phase2_days):
            if day_idx >= phase1_days + phase2_days:
                break
            current_date = today + timedelta(days=day_idx)
            topic = topic_scores[i % topic_count][0]
            plans.append({
                "student_id": student_id,
                "subject_name": subject_name,
                "topic_id": topic.id,
                "topic_name": topic.name,
                "scheduled_date": current_date,
                "duration_minutes": int(daily_hours * 60),
                "status": "Pending"
            })
            day_idx += 1
        
        # Phase 3: Focus on top 3 most important topics
        top_topics = [t for t, _ in topic_scores[:min(3, topic_count)]]
        for i in range(phase3_days):
            current_date = today + timedelta(days=day_idx)
            topic = top_topics[i % len(top_topics)]
            plans.append({
                "student_id": student_id,
                "subject_name": subject_name,
                "topic_id": topic.id,
                "topic_name": topic.name,
                "scheduled_date": current_date,
                "duration_minutes": int(daily_hours * 60),
                "status": "Pending"
            })
            day_idx += 1
            
        return plans

    @staticmethod
    def generate_test_questions(subject_id: int, test_type: str, topics: List[Any], count: int) -> List[Dict[str, Any]]:
        """
        Generate relevant, topic-specific test questions from the knowledge base.
        """
        all_questions = []
        
        for topic in topics:
            topic_questions = generate_smart_test_questions(
                topic_name=topic.name,
                subject_name="",
                test_type=test_type,
                count=max(2, count // max(1, len(topics)))
            )
            all_questions.extend(topic_questions)
        
        # Shuffle and limit to requested count
        random.shuffle(all_questions)
        return all_questions[:count]
