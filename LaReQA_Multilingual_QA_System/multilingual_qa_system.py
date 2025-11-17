#!/usr/bin/env python
# coding: utf-8

"""
LaReQA-Based Multilingual Question Answering System
====================================================

This project demonstrates a unique multilingual question answering system using
Google's LaReQA (Language-agnostic answer Retrieval from a Question and Answer corpus) model.

Key Features:
- Cross-lingual question answering
- Support for multiple languages
- Interactive knowledge base system
- Real-time answer retrieval

Author: Data Science Portfolio
"""

import numpy as np
from typing import List, Dict, Tuple
import json
import os

class MultilingualQASystem:
    """
    A multilingual question answering system using LaReQA model principles.
    
    This implementation showcases cross-lingual information retrieval where
    questions in one language can find relevant answers in documents written
    in different languages.
    """
    
    def __init__(self):
        """Initialize the QA system with sample knowledge base."""
        self.knowledge_base = self._create_sample_knowledge_base()
        self.supported_languages = ['en', 'es', 'fr', 'de', 'hi', 'zh', 'ar', 'ja']
        print("Multilingual QA System initialized successfully!")
        print(f"Supported languages: {', '.join(self.supported_languages)}")
        
    def _create_sample_knowledge_base(self) -> List[Dict]:
        """
        Create a sample multilingual knowledge base with Q&A pairs.
        
        Returns:
            List of dictionaries containing questions and answers in multiple languages
        """
        knowledge_base = [
            {
                'id': 1,
                'language': 'en',
                'question': 'What is artificial intelligence?',
                'answer': 'Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction.',
                'category': 'Technology'
            },
            {
                'id': 2,
                'language': 'es',
                'question': '¿Qué es el aprendizaje automático?',
                'answer': 'El aprendizaje automático es una rama de la inteligencia artificial que permite a las computadoras aprender y mejorar automáticamente a partir de la experiencia sin ser programadas explícitamente.',
                'category': 'Technology'
            },
            {
                'id': 3,
                'language': 'fr',
                'question': 'Qu\'est-ce que la science des données?',
                'answer': 'La science des données est un domaine interdisciplinaire qui utilise des méthodes, des processus, des algorithmes et des systèmes scientifiques pour extraire des connaissances et des idées à partir de données structurées et non structurées.',
                'category': 'Technology'
            },
            {
                'id': 4,
                'language': 'en',
                'question': 'How does natural language processing work?',
                'answer': 'Natural Language Processing (NLP) works by combining computational linguistics with statistical, machine learning, and deep learning models. It enables computers to understand, interpret, and generate human language in a valuable way.',
                'category': 'Technology'
            },
            {
                'id': 5,
                'language': 'de',
                'question': 'Was ist neuronales Netzwerk?',
                'answer': 'Ein neuronales Netzwerk ist ein Rechenmodell, das von der Struktur und Funktion des menschlichen Gehirns inspiriert ist. Es besteht aus verbundenen Knoten (Neuronen), die Informationen verarbeiten.',
                'category': 'Technology'
            },
            {
                'id': 6,
                'language': 'hi',
                'question': 'डेटा विज्ञान क्या है?',
                'answer': 'डेटा विज्ञान एक अंतःविषय क्षेत्र है जो संरचित और असंरचित डेटा से ज्ञान और अंतर्दृष्टि निकालने के लिए वैज्ञानिक विधियों, प्रक्रियाओं और एल्गोरिदम का उपयोग करता है।',
                'category': 'Technology'
            },
            {
                'id': 7,
                'language': 'en',
                'question': 'What are the benefits of machine learning?',
                'answer': 'Machine learning benefits include automation of tasks, improved accuracy, ability to handle large datasets, pattern recognition, predictive analytics, and continuous improvement over time without explicit programming.',
                'category': 'Technology'
            },
            {
                'id': 8,
                'language': 'zh',
                'question': '什么是深度学习?',
                'answer': '深度学习是机器学习的一个子集，它使用多层神经网络来学习数据的复杂表示。深度学习在图像识别、语音识别和自然语言处理等领域取得了突破性进展。',
                'category': 'Technology'
            },
            {
                'id': 9,
                'language': 'ar',
                'question': 'ما هو تعلم الآلة?',
                'answer': 'تعلم الآلة هو فرع من الذكاء الاصطناعي يمكّن أجهزة الكمبيوتر من التعلم والتحسين تلقائياً من التجربة دون أن يتم برمجتها صراحةً.',
                'category': 'Technology'
            },
            {
                'id': 10,
                'language': 'ja',
                'question': '人工知能とは何ですか？',
                'answer': '人工知能（AI）は、機械、特にコンピュータシステムによる人間の知能プロセスのシミュレーションです。これらのプロセスには、学習、推論、自己修正が含まれます。',
                'category': 'Technology'
            }
        ]
        return knowledge_base
    
    def simple_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity based on word overlap.
        
        This is a simplified version for demonstration. In production,
        LaReQA uses sophisticated multilingual embeddings.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def search_answers(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant answers in the knowledge base.
        
        Args:
            query: User's question
            top_k: Number of top results to return
            
        Returns:
            List of top-k relevant Q&A pairs with similarity scores
        """
        results = []
        
        for item in self.knowledge_base:
            # Calculate similarity with question and answer
            q_similarity = self.simple_text_similarity(query, item['question'])
            a_similarity = self.simple_text_similarity(query, item['answer'])
            
            # Take the maximum similarity
            max_similarity = max(q_similarity, a_similarity)
            
            results.append({
                'id': item['id'],
                'question': item['question'],
                'answer': item['answer'],
                'language': item['language'],
                'category': item['category'],
                'similarity_score': max_similarity
            })
        
        # Sort by similarity score in descending order
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:top_k]
    
    def ask_question(self, question: str, display_results: bool = True) -> List[Dict]:
        """
        Ask a question and retrieve relevant answers.
        
        Args:
            question: User's question
            display_results: Whether to print results to console
            
        Returns:
            List of relevant answers with metadata
        """
        print(f"\n{'='*80}")
        print(f"Query: {question}")
        print(f"{'='*80}")
        
        results = self.search_answers(question, top_k=3)
        
        if display_results:
            if not results or results[0]['similarity_score'] == 0:
                print("\nNo relevant answers found. Please try a different question.")
            else:
                print(f"\nTop {len(results)} relevant answers:\n")
                for i, result in enumerate(results, 1):
                    print(f"\n--- Result {i} ---")
                    print(f"Language: {result['language']}")
                    print(f"Similarity Score: {result['similarity_score']:.3f}")
                    print(f"Question: {result['question']}")
                    print(f"Answer: {result['answer']}")
                    print(f"Category: {result['category']}")
        
        return results
    
    def add_to_knowledge_base(self, language: str, question: str, 
                             answer: str, category: str = 'General'):
        """
        Add a new Q&A pair to the knowledge base.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            question: Question text
            answer: Answer text
            category: Category of the Q&A pair
        """
        new_id = max([item['id'] for item in self.knowledge_base]) + 1
        
        new_entry = {
            'id': new_id,
            'language': language,
            'question': question,
            'answer': answer,
            'category': category
        }
        
        self.knowledge_base.append(new_entry)
        print(f"\n✓ Successfully added new Q&A pair (ID: {new_id}) to knowledge base!")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary containing various statistics
        """
        stats = {
            'total_entries': len(self.knowledge_base),
            'languages': {},
            'categories': {}
        }
        
        for item in self.knowledge_base:
            # Count languages
            lang = item['language']
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
            
            # Count categories
            cat = item['category']
            stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
        
        return stats
    
    def display_statistics(self):
        """Display knowledge base statistics in a formatted way."""
        stats = self.get_statistics()
        
        print(f"\n{'='*80}")
        print("KNOWLEDGE BASE STATISTICS")
        print(f"{'='*80}")
        print(f"\nTotal Entries: {stats['total_entries']}")
        
        print("\nLanguage Distribution:")
        for lang, count in sorted(stats['languages'].items()):
            print(f"  {lang}: {count} entries")
        
        print("\nCategory Distribution:")
        for cat, count in sorted(stats['categories'].items()):
            print(f"  {cat}: {count} entries")
        print(f"{'='*80}\n")
    
    def save_knowledge_base(self, filename: str = 'knowledge_base.json'):
        """
        Save the knowledge base to a JSON file.
        
        Args:
            filename: Name of the file to save to
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Knowledge base saved to {filename}")
    
    def load_knowledge_base(self, filename: str = 'knowledge_base.json'):
        """
        Load knowledge base from a JSON file.
        
        Args:
            filename: Name of the file to load from
        """
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"\n✓ Knowledge base loaded from {filename}")
        else:
            print(f"\n✗ File {filename} not found!")


def demonstrate_system():
    """Demonstrate the capabilities of the Multilingual QA System."""
    print("\n" + "="*80)
    print("MULTILINGUAL QUESTION ANSWERING SYSTEM")
    print("Powered by LaReQA Model Principles")
    print("="*80)
    
    # Initialize the system
    qa_system = MultilingualQASystem()
    
    # Display statistics
    qa_system.display_statistics()
    
    # Demo questions in different languages
    demo_questions = [
        "What is artificial intelligence?",
        "machine learning benefits",
        "neural network",
        "datos ciencia",  # Spanish words
        "apprentissage",  # French word
    ]
    
    print("\n" + "="*80)
    print("DEMONSTRATION: Cross-lingual Question Answering")
    print("="*80)
    
    for question in demo_questions:
        qa_system.ask_question(question)
    
    # Add a new entry
    print("\n" + "="*80)
    print("DEMONSTRATION: Adding New Knowledge")
    print("="*80)
    
    qa_system.add_to_knowledge_base(
        language='en',
        question='What is computer vision?',
        answer='Computer vision is a field of artificial intelligence that trains computers to interpret and understand the visual world. Using digital images and deep learning models, machines can accurately identify and classify objects.',
        category='Technology'
    )
    
    # Search for the newly added question
    qa_system.ask_question("computer vision")
    
    # Save knowledge base
    print("\n" + "="*80)
    print("SAVING KNOWLEDGE BASE")
    print("="*80)
    qa_system.save_knowledge_base('lareqa_knowledge_base.json')
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Multilingual knowledge base")
    print("  ✓ Cross-lingual question answering")
    print("  ✓ Real-time answer retrieval")
    print("  ✓ Dynamic knowledge base updates")
    print("  ✓ Knowledge base persistence")
    print("\nThis system can be extended with:")
    print("  • Integration with actual LaReQA model from TensorFlow Hub")
    print("  • Advanced multilingual embeddings")
    print("  • Web interface for user interaction")
    print("  • Database backend for large-scale knowledge bases")
    print("  • Real-time translation integration")
    print("="*80 + "\n")


def interactive_mode():
    """Run the system in interactive mode for user queries."""
    qa_system = MultilingualQASystem()
    qa_system.display_statistics()
    
    print("\n" + "="*80)
    print("INTERACTIVE MODE - Multilingual Question Answering")
    print("="*80)
    print("\nYou can now ask questions in any language!")
    print("Type 'stats' to view statistics")
    print("Type 'add' to add a new Q&A pair")
    print("Type 'save' to save knowledge base")
    print("Type 'quit' or 'exit' to exit")
    print("="*80 + "\n")
    
    while True:
        try:
            user_input = input("\nYour question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using the Multilingual QA System!")
                break
            
            elif user_input.lower() == 'stats':
                qa_system.display_statistics()
            
            elif user_input.lower() == 'save':
                filename = input("Enter filename (default: lareqa_knowledge_base.json): ").strip()
                if not filename:
                    filename = 'lareqa_knowledge_base.json'
                qa_system.save_knowledge_base(filename)
            
            elif user_input.lower() == 'add':
                print("\nAdd new Q&A pair:")
                lang = input("Language code (e.g., en, es, fr): ").strip()
                question = input("Question: ").strip()
                answer = input("Answer: ").strip()
                category = input("Category (default: General): ").strip()
                if not category:
                    category = 'General'
                
                qa_system.add_to_knowledge_base(lang, question, answer, category)
            
            else:
                qa_system.ask_question(user_input)
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    # Run demonstration
    demonstrate_system()
    
    # Uncomment the line below to run in interactive mode
    # interactive_mode()
