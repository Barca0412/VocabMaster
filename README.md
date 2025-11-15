# VocabMaster

 ![visitors](https://visitor-badge.laobi.icu/badge?page_id=Barca0412.VocabMaster)

A desktop vocabulary learning application with intelligent spaced repetition and AI-powered personalized learning.


<div align=center>
   <img width="350" height="1000" alt="image" src="https://github.com/user-attachments/assets/2ea5af63-ba84-422a-8224-ae30c61ec349" />

</div>  

## Overview

VocabMaster is a PyQt6-based desktop application designed to enhance English vocabulary acquisition through:

- **Spaced Repetition Algorithm**: Scientifically-proven learning intervals for optimal retention
- **AI-Powered Personalization**: LLM-generated example sentences tailored to your learning goals
- **Comprehensive Tracking**: Detailed learning analytics and progress monitoring
- **Built-in Vocabulary Sets**: Curated CET-4 and CET-6 word lists included
- **Clean, Minimal UI**: Distraction-free learning experience with light/dark themes

## Features

### Core Functionality

**Word Learning**
- Floating desktop widget for persistent visibility
- Automatic word rotation with customizable intervals
- Dictionary integration (Youdao, Merriam-Webster)
- Pronunciation and phonetic transcription
- Context-aware example sentences

**Spaced Repetition System**
- SM-2 algorithm implementation
- Automatic difficulty adjustment based on performance
- Review scheduling optimization
- Learning progress persistence

**Intelligent Testing**
- Quiz mode with 4-option multiple choice
- LLM-generated distractors for realistic difficulty
- Immediate feedback with correct answer display
- Performance tracking and weak word identification

**Learning Analytics**
- Comprehensive learning statistics
- Weak word identification (accuracy < 60%, attempts >= 3)
- Recent mistake review
- Personalized learning recommendations
- Detailed progress reports

### AI Integration

**Personalized Example Sentences**
- Context-aware sentence generation based on learning goals
- Supports various scenarios: TOEFL preparation, business English, technical documentation, daily conversation
- Graceful fallback to dictionary examples when LLM unavailable

**Smart Distractor Generation**
- AI-generated plausible wrong answers for quiz questions
- Difficulty calibration based on word complexity
- Semantic similarity analysis to create challenging options

## Installation

### Prerequisites

- Python 3.10 or higher
- macOS, Linux, or Windows

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Barca0412/VocabMaster.git
cd VocabMaster
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API credentials (optional, for AI features):
```bash
cp .env.example .env
# Edit .env and add your API key
```

5. Run the application:
```bash
python main.py
```

## Configuration

### API Setup

To enable AI-powered features, you need an OpenAI-compatible API key:

1. Register at [SiliconFlow](https://cloud.siliconflow.cn) (or any OpenAI-compatible provider)
2. Obtain your API key
3. Copy `.env.example` to `.env`
4. Add your credentials:

```
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
OPENAI_MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
```

### Learning Goal Configuration

Set your learning objective to receive personalized content:

1. Open Settings window
2. Navigate to "Learning Goal" section
3. Enter your goal (e.g., "Preparing for TOEFL exam", "Improving business English communication")
4. Save settings

Example sentences will be tailored to your specified context.

## Usage

### Basic Workflow

1. **Select Vocabulary List**
   - Open Settings
   - Choose from built-in CET-4/CET-6 lists or import custom wordlist
   - Save configuration

2. **Study Words**
   - Click play button to start automatic word rotation
   - Review word definitions, pronunciations, and examples
   - Use navigation buttons to move between words manually

3. **Test Knowledge**
   - Click "Quiz" button to start assessment
   - Answer 20 multiple-choice questions
   - Review results and weak words

4. **Track Progress**
   - Click "Report" button to view learning analytics
   - Review weak words and recent mistakes
   - Follow personalized recommendations

### Keyboard Shortcuts

- `Space`: Play/Pause word rotation
- `Left Arrow`: Previous word
- `Right Arrow`: Next word
- `Q`: Open quiz window
- `S`: Open settings
- `R`: View report
- `T`: Toggle theme

### Data Management

All user data is stored locally in `~/.word_recite/`:

```
~/.word_recite/
├── config.json          # Application settings
├── data/
│   ├── words/          # Custom word lists
│   ├── cache/          # Dictionary cache
│   ├── reviews/        # Spaced repetition data
│   └── tracker/        # Learning analytics
```

## Architecture

### Project Structure

```
VocabMaster/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                # API configuration template
├── src/
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   ├── word_manager.py     # Vocabulary data handling
│   │   ├── dictionary.py       # Dictionary API integration
│   │   ├── spaced_repetition.py # SM-2 algorithm
│   │   ├── learning_tracker.py  # Progress tracking
│   │   └── llm_generator.py    # AI content generation
│   └── ui/
│       ├── main_window.py      # Primary interface
│       ├── settings_window_new.py # Configuration UI
│       ├── quiz_window.py      # Assessment interface
│       ├── report_window.py    # Analytics display
│       └── themes.py           # Visual styling
├── data/
│   ├── builtin_cet4.txt        # CET-4 vocabulary
│   └── builtin_cet6.txt        # CET-6 vocabulary
└── docs/
    ├── FEATURES_v3.md          # Detailed feature documentation
    ├── LLM_INTEGRATION.md      # AI integration guide
    └── SPACED_REPETITION_DESIGN.md # Algorithm specification
```

### Technology Stack

- **GUI Framework**: PyQt6
- **Dictionary APIs**: Youdao, Merriam-Webster
- **AI Integration**: OpenAI-compatible API (Qwen 2.5 72B)
- **Data Storage**: JSON file-based persistence
- **Algorithm**: SM-2 spaced repetition

## Development

### Running Tests

```bash
python test_app.py
```

### Code Style

The project follows PEP 8 guidelines. Key conventions:

- 4-space indentation
- Maximum line length: 100 characters
- Type hints for function signatures
- Docstrings for all public methods

### Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## Performance Considerations

### Resource Usage

- Memory footprint: ~50MB base, +20MB per 1000 cached words
- Disk space: ~10MB base, +5MB per 1000 words with cache
- CPU: Minimal during idle, spikes during LLM API calls

### Optimization Tips

- Enable dictionary caching to reduce API calls
- Adjust word rotation interval to balance learning pace and resource usage
- Disable AI features on metered connections to save bandwidth

## Troubleshooting

### Common Issues

**Application won't start**
- Verify Python version >= 3.10
- Check all dependencies are installed: `pip list`
- Review error logs in console output

**Dictionary API failures**
- Verify internet connection
- Check API rate limits haven't been exceeded
- Enable offline mode in settings if needed

**LLM features not working**
- Confirm `.env` file exists with valid API key
- Test API connectivity: `curl -H "Authorization: Bearer YOUR_KEY" YOUR_API_URL/models`
- Verify model name is correct and accessible
- Check API provider service status

**Settings window crash**
- Update to latest version (animation issues fixed in v3.0)
- Clear application cache: `rm -rf ~/.word_recite/data/cache`

## Privacy and Security

- All learning data stored locally on your device
- No telemetry or usage tracking
- API keys stored in local `.env` file (never committed to version control)
- Dictionary cache encrypted with user permissions
- No personal data transmitted to third parties

## License

MIT License

Copyright (c) 2025 Barca

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- SM-2 algorithm by Piotr Woźniak
- Dictionary data from Youdao and Merriam-Webster APIs
- CET vocabulary lists curated from public educational resources
- AI capabilities powered by Qwen 2.5 model

## Contact

- GitHub: [@Barca0412](https://github.com/Barca0412)
- Issues: [GitHub Issues](https://github.com/Barca0412/VocabMaster/issues)

## Roadmap

### Planned Features

- Export learning reports to PDF
- Cloud synchronization (optional)
- Audio pronunciation support
- Vocabulary import from external sources (Anki, CSV)
- Gamification elements (streaks, achievements)
- Mobile companion app
- Collaborative learning features

### Version History

**v3.0.0** (Current)
- AI-powered personalized example sentences
- Comprehensive learning analytics and reporting
- Weak word identification system
- UI/UX improvements (Anthropic design language)
- Learning goal configuration

**v2.0.0**
- Spaced repetition algorithm implementation
- Quiz mode with intelligent testing
- LLM-generated quiz distractors
- Built-in CET-4/CET-6 vocabulary

**v1.0.0**
- Initial release
- Basic word browsing
- Dictionary integration
- Theme support
