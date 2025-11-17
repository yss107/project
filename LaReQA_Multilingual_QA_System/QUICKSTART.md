# Quick Start Guide - LaReQA Multilingual QA System

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `numpy` - Core numerical operations
- `flask` - Web framework for the interface

### Step 2: Start the Web Interface

```bash
python web_interface.py
```

### Step 3: Open Your Browser

Navigate to: **http://localhost:5000**

---

## 📖 Using the Web Interface

### Ask Questions
1. Enter your question in any supported language in the search box
2. Click "Search Answers"
3. View results ranked by similarity score

**Example queries:**
- "What is artificial intelligence?"
- "aprendizaje automático" (Spanish)
- "science données" (French)
- "neural network deep learning"

### Add Knowledge
1. Select the language from the dropdown
2. Enter your question
3. Enter the answer
4. Optionally specify a category
5. Click "Add to Knowledge Base"

The system will save your additions automatically!

### View Statistics
Scroll down to see:
- Total entries in the knowledge base
- Number of languages
- Number of categories

---

## 🌐 Supported Languages

- 🇬🇧 English (en)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇮🇳 Hindi (hi)
- 🇨🇳 Chinese (zh)
- 🇸🇦 Arabic (ar)
- 🇯🇵 Japanese (ja)

---

## 💡 Alternative Usage Methods

### Command-Line Demo
```bash
python multilingual_qa_system.py
```

### Example Scripts
```bash
python example_usage.py
```

### Jupyter Notebook
```bash
jupyter notebook Multilingual_QA_LaReQA.ipynb
```

---

## 🎯 Key Features

✅ **Cross-lingual search** - Ask in one language, find answers in others
✅ **Real-time results** - Instant answer retrieval with similarity scores
✅ **Dynamic knowledge base** - Add Q&A pairs on the fly
✅ **Modern web UI** - Beautiful, responsive interface
✅ **Easy to use** - No configuration needed
✅ **Persistent storage** - Knowledge base saved automatically

---

## 🆘 Troubleshooting

**Problem:** ModuleNotFoundError
**Solution:** Run `pip install -r requirements.txt`

**Problem:** Port 5000 already in use
**Solution:** Change the port in `web_interface.py` (last line)

**Problem:** No results found
**Solution:** Try different keywords or add more Q&A pairs

---

## 📚 Learn More

- **README.md** - Full documentation
- **About page** - Technical details (http://localhost:5000/about)
- [LaReQA on Kaggle](https://www.kaggle.com/models/google/lareqa)

---

**Enjoy using the LaReQA Multilingual QA System!** 🌍🤖
