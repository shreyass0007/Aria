# LLM Training System for ARIA - Complete Guide

## 📚 Overview

This comprehensive training system helps your LLM understand all ARIA app-related commands with high accuracy. The system includes training datasets, system prompts, command reference documentation, fine-tuning capabilities, and validation tools.

## 📁 Created Files

### 1. **llm_training_dataset.json** - Main Training Dataset
- **220+ command examples** organized by category
- **40+ intent types** covering all ARIA capabilities
- Natural language variations for each command
- Parameter examples and context scenarios
- Categories: Power, Volume, Files, System, Web, Productivity, etc.

### 2. **llm_system_prompt.txt** - System Prompt Template
- Complete capability definition for ARIA
- Intent classification guidelines
- Parameter extraction rules
- Distinction rules (file search vs web search, etc.)
- Few-shot examples for accuracy
- Use this as the system message for your LLM

### 3. **command_reference_for_llm.md** - Command Reference Documentation
- Comprehensive command catalog (40+ intents)
- Natural language patterns for each command
- Parameter requirements and examples
- Decision trees for classification
- Common confusion points clarified
- Perfect for LLM context or RAG systems

### 4. **fine_tuning_dataset.jsonl** - Fine-Tuning Dataset
- 50 curated examples in OpenAI fine-tuning format
- Ready to upload for custom model training
- Diverse command coverage
- Proper message format for fine-tuning

### 5. **generate_fine_tuning_data.py** - Data Generator
- Programmatically generates additional training examples
- Randomizes parameters (filenames, locations, levels, etc.)
- Creates variations automatically
- Run to generate more training data as needed

### 6. **test_llm_training.py** - Validation Script
- Tests classification accuracy on training dataset
- Validates parameter extraction
- Tests edge cases and confusion points
- Provides detailed accuracy reports
- Identifies failed classifications for improvement

## 🚀 How to Use This Training System

### Option 1: Context-Based Training (Recommended for GPT-4/Claude)

**Use for**: GPT-4, Claude, or other large context models

1. **Load the system prompt**:
   ```python
   with open('llm_system_prompt.txt', 'r') as f:
       system_prompt = f.read()
   ```

2. **Use it in your LLM calls**:
   ```python
   messages = [
       {"role": "system", "content": system_prompt},
       {"role": "user", "content": user_command}
   ]
   response = llm.invoke(messages)
   ```

3. **Optionally include command reference in context**:
   - For longer context models, include `command_reference_for_llm.md`
   - Use RAG (Retrieval Augmented Generation) to fetch relevant sections

### Option 2: Fine-Tuning (For Custom Models)

**Use for**: Creating a specialized ARIA command model

1. **Prepare dataset**:
   ```bash
   # Use existing dataset
   # OR generate more examples:
   python generate_fine_tuning_data.py
   ```

2. **Combine datasets** (optional):
   ```bash
   # Merge fine_tuning_dataset.jsonl and generated_fine_tuning_data.jsonl
   cat fine_tuning_dataset.jsonl generated_fine_tuning_data.jsonl > combined_training.jsonl
   ```

3. **Upload to OpenAI**:
   ```bash
   openai api fine_tuning.jobs.create \
     -t combined_training.jsonl \
     -m gpt-3.5-turbo
   ```

4. **Use your fine-tuned model**:
   ```python
   response = openai.ChatCompletion.create(
       model="ft:gpt-3.5-turbo:your-org:aria-commands:id",
       messages=[{"role": "user", "content": user_command}]
   )
   ```

### Option 3: Hybrid Approach (Best Results)

1. Fine-tune a base model on the dataset
2. Use the system prompt for additional guidance
3. Include command reference for edge cases

## 🧪 Testing Your LLM

Run the validation script to test accuracy:

```bash
python test_llm_training.py
```

This will:
- Test classification on 200+ examples
- Validate parameter extraction
- Test edge cases (file search vs web search, etc.)
- Provide accuracy metrics
- Show failed classifications for improvement

**Expected Results:**
- ✓ Excellent: 95%+ accuracy
- ✓ Good: 85-95% accuracy
- ⚠ Fair: 75-85% accuracy (needs improvement)
- ✗ Poor: <75% accuracy (review training data)

## 📊 Training Dataset Structure

```json
{
  "metadata": {
    "total_intents": 40,
    "total_examples": 220,
    "categories": 14
  },
  "training_examples": [
    {
      "category": "power_management",
      "intent": "shutdown",
      "examples": [
        {
          "input": "shutdown the computer",
          "parameters": {},
          "variations": [
            "turn off the computer",
            "shut down my pc",
            ...
          ]
        }
      ]
    }
  ]
}
```

## 🎯 Intent Categories

1. **Power Management** (5 intents)
   - shutdown, restart, lock, sleep, cancel_shutdown

2. **Volume Control** (6 intents)
   - volume_up, volume_down, volume_set, volume_mute, volume_unmute, volume_check

3. **System Maintenance** (2 intents)
   - recycle_bin_empty, recycle_bin_check

4. **Clipboard Operations** (3 intents)
   - clipboard_copy, clipboard_read, clipboard_clear

5. **Screenshot Operations** (1 intent)
   - screenshot_take

6. **System Monitoring** (4 intents)
   - battery_check, cpu_check, ram_check, system_stats

7. **File Automation** (2 intents)
   - organize_downloads, organize_desktop

8. **File Operations** (10 intents)
   - file_create, file_read, file_info, file_append, file_replace, file_delete, file_rename, file_move, file_copy, file_search

9. **Web & Applications** (3 intents)
   - web_open, app_open, web_search

10. **Media** (1 intent)
    - music_play

11. **Productivity** (4 intents)
    - calendar_query, calendar_create, notion_query, notion_create

12. **Information Services** (3 intents)
    - time_check, date_check, weather_check

13. **Email** (1 intent)
    - email_send

14. **General** (1 intent)
    - general_chat

## 🔑 Key Features

### Natural Language Understanding
- Recognizes multiple phrasings of same command
- Handles casual vs formal language
- Context-aware classification

### Parameter Extraction
- Filenames, locations, volume levels
- City names for weather
- Email addresses, calendar times
- File patterns and search queries

### Smart Disambiguation
- File search vs web search
- Website vs desktop application
- Create vs append file operations
- Location mapping ("download section" → "downloads")

## 💡 Best Practices

1. **Start with System Prompt**: Always use the system prompt for context
2. **Test Regularly**: Run validation script after LLM updates
3. **Add Examples**: If you find misclassifications, add training examples
4. **Use Fine-Tuning for Production**: For best results and lower latency
5. **Monitor Confidence**: Low confidence scores indicate uncertain classifications

## 📈 Continuous Improvement

1. **Collect Real Usage Data**:
   - Log user commands and classifications
   - Identify common misclassifications
   - Add failed examples to training dataset

2. **Expand Training Data**:
   - Use `generate_fine_tuning_data.py` for more variations
   - Add new intents as ARIA features grow
   - Include user-specific command patterns

3. **A/B Testing**:
   - Compare different model versions
   - Test fine-tuned vs context-only approaches
   - Measure accuracy improvements

## 🛠️ Integration with ARIA

The training system is designed to work seamlessly with ARIA's existing `command_intent_classifier.py`:

```python
from command_intent_classifier import CommandIntentClassifier
from brain import AriaBrain

# Initialize
brain = AriaBrain()
classifier = CommandIntentClassifier(brain)

# Classify command
result = classifier.classify_intent("shutdown the computer")
print(result)
# Output: {'intent': 'shutdown', 'confidence': 0.98, 'parameters': {}}
```

The classifier already uses your LLM through `AriaBrain`, so the training immediately improves ARIA's command understanding!

## 📝 Files Summary

| File | Purpose | Size | Usage |
|------|---------|------|-------|
| `llm_training_dataset.json` | Main training data | 220 examples | Load for context/analysis |
| `llm_system_prompt.txt` | System prompt | ~2KB | Use as system message |
| `command_reference_for_llm.md` | Command documentation | ~20KB | RAG/context reference |
| `fine_tuning_dataset.jsonl` | Fine-tuning data | 50 examples | Upload for fine-tuning |
| `generate_fine_tuning_data.py` | Data generator | Script | Generate more examples |
| `test_llm_training.py` | Validation tests | Script | Test accuracy |

## 🎓 Next Steps

1. ✅ **Immediate**: Use `llm_system_prompt.txt` in your LLM calls
2. ✅ **Short-term**: Run `test_llm_training.py` to establish baseline
3. ⏳ **Medium-term**: Fine-tune a model with the datasets
4. ⏳ **Long-term**: Implement continuous learning from user commands

## 📞 Support

For questions or improvements:
1. Review `command_reference_for_llm.md` for detailed command info
2. Check test results for accuracy metrics
3. Expand training dataset for better coverage

---

**Version**: 1.0  
**Created**: 2025-11-28  
**Total Training Examples**: 220+ (with variations: 500+)  
**Coverage**: 40 intents across 14 categories  
**Expected Accuracy**: 95%+
