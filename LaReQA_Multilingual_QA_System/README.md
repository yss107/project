# LaReQA-Based Multilingual Question Answering System 🌍🤖

## Overview

This project implements an innovative **Multilingual Question Answering System** inspired by Google's **LaReQA (Language-agnostic answer Retrieval from a Question and Answer corpus)** model. The system enables cross-lingual information retrieval, allowing users to ask questions in one language and retrieve relevant answers from documents written in different languages.

## 🌟 What Makes This Project Unique

1. **Cross-Lingual Retrieval**: Ask questions in any supported language and get answers from a multilingual knowledge base
2. **Language-Agnostic Architecture**: Based on LaReQA principles for effective multilingual understanding
3. **Interactive Knowledge Base**: Dynamically add, update, and manage Q&A pairs across multiple languages
4. **Real-Time Answer Retrieval**: Instant search and ranking of relevant answers
5. **Extensible Design**: Easy to integrate with TensorFlow Hub's LaReQA model for production use

## 📋 Features

- ✅ Support for multiple languages (English, Spanish, French, German, Hindi, Chinese, Arabic, Japanese)
- ✅ Cross-lingual question answering
- ✅ Similarity-based answer ranking
- ✅ **Interactive web interface**
- ✅ Interactive command-line interface
- ✅ Knowledge base management (add, save, load)
- ✅ Statistical analysis of the knowledge base
- ✅ JSON-based knowledge persistence
- ✅ Modular and extensible architecture

## 🎯 Use Cases

1. **Multilingual Customer Support**: Answer customer queries regardless of language
2. **Cross-Cultural Research**: Find information across language barriers
3. **Education**: Learn concepts explained in different languages
4. **International Business**: Access knowledge from global documentation
5. **Content Discovery**: Find relevant content in multiple languages

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.7 or higher
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yss107/project.git
cd project/LaReQA_Multilingual_QA_System
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Basic Usage

#### Option 1: Web Interface (Recommended)

The easiest way to use the system is through the web interface:

```bash
python web_interface.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

The web interface provides:
- 🔍 Question search with real-time results
- ➕ Add new Q&A pairs to the knowledge base
- 📊 Live statistics dashboard
- 🎨 Modern, responsive design
- 🌐 Support for all 8+ languages

#### Option 2: Command-Line Demonstration

```python
python multilingual_qa_system.py
```

This will:
- Initialize the multilingual QA system
- Display knowledge base statistics
- Demonstrate cross-lingual question answering
- Show how to add new knowledge
- Save the knowledge base to a JSON file

#### Option 3: Interactive Mode

To use the system interactively, uncomment the last line in `multilingual_qa_system.py`:

```python
if __name__ == "__main__":
    demonstrate_system()
    interactive_mode()  # Uncomment this line
```

Then run:
```bash
python multilingual_qa_system.py
```

## 💡 Example Usage

### Python Script

```python
from multilingual_qa_system import MultilingualQASystem

# Initialize the system
qa_system = MultilingualQASystem()

# Ask a question in English
results = qa_system.ask_question("What is artificial intelligence?")

# Ask a question using Spanish keywords
results = qa_system.ask_question("aprendizaje automático")

# Ask a question using French keywords
results = qa_system.ask_question("science des données")

# Add a new Q&A pair
qa_system.add_to_knowledge_base(
    language='en',
    question='What is blockchain?',
    answer='Blockchain is a distributed ledger technology that maintains a secure and decentralized record of transactions.',
    category='Technology'
)

# View statistics
qa_system.display_statistics()

# Save knowledge base
qa_system.save_knowledge_base('my_knowledge_base.json')
```

### Sample Queries

```
Query: "What is artificial intelligence?"
→ Returns answers about AI from the knowledge base

Query: "machine learning benefits"
→ Returns information about ML advantages

Query: "neural network" (English keywords)
→ Can find answers in German ("neuronales Netzwerk")

Query: "datos ciencia" (Spanish keywords)
→ Can find answers about data science in multiple languages
```

## 🏗️ Architecture

The system consists of several key components:

1. **MultilingualQASystem Class**: Main class managing the QA system
2. **Knowledge Base**: Collection of multilingual Q&A pairs
3. **Similarity Calculator**: Measures relevance between queries and answers
4. **Search Engine**: Retrieves and ranks relevant answers
5. **Knowledge Manager**: Handles adding, saving, and loading Q&A pairs

### System Flow

```
User Query → Text Preprocessing → Similarity Calculation → 
Answer Ranking → Top-K Results → Display to User
```

## 📊 Knowledge Base Structure

Each entry in the knowledge base contains:

```json
{
  "id": 1,
  "language": "en",
  "question": "What is artificial intelligence?",
  "answer": "AI is the simulation of human intelligence...",
  "category": "Technology"
}
```

## 🔧 Advanced Configuration

### Extending with Real LaReQA Model

To integrate with Google's actual LaReQA model from TensorFlow Hub:

```python
import tensorflow_hub as hub

# Load LaReQA model
model_url = "https://tfhub.dev/google/lareqa/question_encoder/1"
question_encoder = hub.load(model_url)

# Use for embeddings
question_embeddings = question_encoder(["What is AI?"])
```

### Supported Languages

- **English (en)**: Primary language
- **Spanish (es)**: español
- **French (fr)**: français
- **German (de)**: Deutsch
- **Hindi (hi)**: हिन्दी
- **Chinese (zh)**: 中文
- **Arabic (ar)**: العربية
- **Japanese (ja)**: 日本語

## 📈 Performance Considerations

- **Current Implementation**: Uses simple text similarity (Jaccard coefficient)
- **Production Ready**: Integrate with LaReQA embeddings for better accuracy
- **Scalability**: Use vector databases (Pinecone, Weaviate) for large-scale deployment
- **Optimization**: Implement caching for frequently asked questions

## 🛣️ Roadmap

- [ ] Integration with TensorFlow Hub LaReQA model
- [ ] Web-based user interface
- [ ] Database backend (PostgreSQL/MongoDB)
- [ ] REST API development
- [ ] Advanced language detection
- [ ] Real-time translation integration
- [ ] Fine-tuning on domain-specific data
- [ ] Performance benchmarking suite

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. Enhanced similarity algorithms
2. Additional language support
3. Web interface development
4. Performance optimizations
5. Documentation improvements

## 📚 References

- [Google LaReQA Model on Kaggle](https://www.kaggle.com/models/google/lareqa)
- [TensorFlow Hub - LaReQA](https://tfhub.dev/google/collections/lareqa/1)
- [Cross-lingual Question Answering Research](https://ai.googleblog.com/2020/11/teaching-machines-to-answer-questions.html)

## 📝 License

This project is part of an open-source data science portfolio. Feel free to use and modify as needed.

## 👨‍💻 Author

Created as part of a comprehensive data science and machine learning project portfolio.

## 🙏 Acknowledgments

- Google Research for the LaReQA model
- TensorFlow Hub for model hosting
- The multilingual NLP community

---

**Note**: This is a demonstration project showcasing the concepts of cross-lingual question answering. For production use, integrate with the actual LaReQA model from TensorFlow Hub for improved accuracy and performance.
