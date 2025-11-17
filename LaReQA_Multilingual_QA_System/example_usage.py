#!/usr/bin/env python
# coding: utf-8

"""
Example Usage Script for LaReQA Multilingual QA System
=======================================================

This script demonstrates various ways to use the Multilingual QA System.
Run this script to see the system in action with different examples.
"""

from multilingual_qa_system import MultilingualQASystem
import time

def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def example_basic_usage():
    """Demonstrate basic usage of the QA system."""
    print_section_header("EXAMPLE 1: Basic Usage")
    
    # Initialize the system
    qa_system = MultilingualQASystem()
    
    # Ask a simple question
    print("Asking: 'What is artificial intelligence?'\n")
    qa_system.ask_question("What is artificial intelligence?")
    
    time.sleep(1)

def example_cross_lingual():
    """Demonstrate cross-lingual capabilities."""
    print_section_header("EXAMPLE 2: Cross-lingual Question Answering")
    
    qa_system = MultilingualQASystem()
    
    # Ask using keywords from different languages
    queries = [
        ("English", "machine learning"),
        ("Spanish keywords", "aprendizaje automático"),
        ("French keywords", "science données"),
        ("Mixed", "neural network deep learning")
    ]
    
    for lang, query in queries:
        print(f"\n[{lang}] Query: '{query}'")
        qa_system.ask_question(query, display_results=False)
        results = qa_system.search_answers(query, top_k=1)
        if results and results[0]['similarity_score'] > 0:
            print(f"  → Found answer in {results[0]['language']}")
            print(f"  → Score: {results[0]['similarity_score']:.3f}")
        time.sleep(0.5)

def example_knowledge_management():
    """Demonstrate knowledge base management."""
    print_section_header("EXAMPLE 3: Knowledge Base Management")
    
    qa_system = MultilingualQASystem()
    
    print("Initial statistics:")
    stats = qa_system.get_statistics()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Languages: {list(stats['languages'].keys())}")
    
    # Add new knowledge
    print("\n➕ Adding new Q&A pairs...\n")
    
    qa_system.add_to_knowledge_base(
        language='en',
        question='What is blockchain technology?',
        answer='Blockchain is a distributed ledger technology that maintains a secure and decentralized record of transactions across multiple computers.',
        category='Technology'
    )
    
    qa_system.add_to_knowledge_base(
        language='pt',
        question='O que é inteligência artificial?',
        answer='Inteligência Artificial é a capacidade de máquinas de realizar tarefas que normalmente requerem inteligência humana.',
        category='Technology'
    )
    
    # Show updated statistics
    print("\nUpdated statistics:")
    stats = qa_system.get_statistics()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Languages: {list(stats['languages'].keys())}")

def example_search_and_rank():
    """Demonstrate search and ranking capabilities."""
    print_section_header("EXAMPLE 4: Search and Ranking")
    
    qa_system = MultilingualQASystem()
    
    query = "artificial intelligence machine learning"
    print(f"Query: '{query}'\n")
    
    results = qa_system.search_answers(query, top_k=5)
    
    print("Top 5 Results:")
    for i, result in enumerate(results, 1):
        if result['similarity_score'] > 0:
            print(f"\n{i}. [{result['language'].upper()}] Score: {result['similarity_score']:.3f}")
            print(f"   {result['question'][:60]}...")

def example_persistence():
    """Demonstrate saving and loading knowledge base."""
    print_section_header("EXAMPLE 5: Knowledge Base Persistence")
    
    # Create and populate a knowledge base
    print("Creating new QA system...")
    qa_system = MultilingualQASystem()
    
    # Add custom entries
    qa_system.add_to_knowledge_base(
        language='en',
        question='What is quantum computing?',
        answer='Quantum computing uses quantum-mechanical phenomena to perform operations on data. It has the potential to solve certain problems much faster than classical computers.',
        category='Technology'
    )
    
    # Save to file
    filename = 'example_knowledge_base.json'
    print(f"\n💾 Saving knowledge base to '{filename}'...")
    qa_system.save_knowledge_base(filename)
    
    # Create a new system and load the saved data
    print(f"\n📂 Loading knowledge base from '{filename}'...")
    new_qa_system = MultilingualQASystem()
    new_qa_system.load_knowledge_base(filename)
    
    # Verify the loaded data
    stats = new_qa_system.get_statistics()
    print(f"\n✓ Loaded {stats['total_entries']} entries successfully!")
    
    # Test a query on the loaded system
    print("\nTesting query on loaded system:")
    new_qa_system.ask_question("quantum computing", display_results=False)
    results = new_qa_system.search_answers("quantum computing", top_k=1)
    if results and results[0]['similarity_score'] > 0:
        print(f"  ✓ Found relevant answer with score: {results[0]['similarity_score']:.3f}")

def example_multilingual_comparison():
    """Compare answers across different languages."""
    print_section_header("EXAMPLE 6: Multilingual Answer Comparison")
    
    qa_system = MultilingualQASystem()
    
    # Add questions in multiple languages about the same topic
    qa_system.add_to_knowledge_base(
        language='en',
        question='What is the Internet of Things?',
        answer='IoT refers to the network of physical devices embedded with sensors and software that connect and exchange data over the internet.',
        category='Technology'
    )
    
    qa_system.add_to_knowledge_base(
        language='es',
        question='¿Qué es el Internet de las Cosas?',
        answer='IoT se refiere a la red de dispositivos físicos que están integrados con sensores y software para conectarse e intercambiar datos.',
        category='Technology'
    )
    
    # Query and see results from multiple languages
    query = "Internet Things IoT devices"
    print(f"Query: '{query}'\n")
    results = qa_system.search_answers(query, top_k=2)
    
    for i, result in enumerate(results, 1):
        if result['similarity_score'] > 0:
            print(f"\n--- Answer {i} ({result['language'].upper()}) ---")
            print(f"Score: {result['similarity_score']:.3f}")
            print(f"Q: {result['question']}")
            print(f"A: {result['answer'][:100]}...")

def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("  LaReQA MULTILINGUAL QA SYSTEM - EXAMPLE DEMONSTRATIONS")
    print("="*80)
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Cross-lingual Capabilities", example_cross_lingual),
        ("Knowledge Management", example_knowledge_management),
        ("Search and Ranking", example_search_and_rank),
        ("Persistence", example_persistence),
        ("Multilingual Comparison", example_multilingual_comparison)
    ]
    
    for name, func in examples:
        try:
            func()
            time.sleep(1)
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
    
    print("\n" + "="*80)
    print("  ALL EXAMPLES COMPLETED")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Try the interactive mode: python multilingual_qa_system.py")
    print("  2. Explore the Jupyter notebook: Multilingual_QA_LaReQA.ipynb")
    print("  3. Build your own knowledge base with custom Q&A pairs")
    print("  4. Integrate with TensorFlow Hub's LaReQA model for production use")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
