# 🎨 Lovely Interiors - AI-Powered Paint Consultation System

A sophisticated **multi-agent AI system** built with **Google's Agent Development Kit (ADK)** and **Gemini 2.5 Pro** that provides professional-grade interior paint consultations. Combines computer vision, natural language processing, and advanced color theory algorithms to deliver personalized paint recommendations based on room photos, lighting analysis, and design principles.

## ✨ Core Features

🏠 **Professional Paint Consultation**
- Expert-level color recommendations backed by 15+ years of encoded design knowledge
- Farrow & Ball paint catalog (301+ colors) with extensible architecture for additional brands
- Room-specific recommendations based on function, style, and architectural context

🔍 **Advanced Analysis Capabilities**
- AI-powered photo analysis using vision models for lighting and material assessment
- Sophisticated undertone detection and harmony algorithms
- Material relationship understanding (flooring, cabinetry, countertops)
- LRV (Light Reflectance Value) optimization for room brightness

🎯 **Intelligent Multi-Agent Architecture**
- Built on Google ADK framework with specialized sub-agents
- Natural language color search with semantic matching
- Automated schedule validation and quality assurance
- Professional export formatting for contractors
- Browser automation for paint sample ordering

## 🤖 Browser Automation Integration

**Automated Sample Ordering**: Modern Browser-Use v0.7+ integration for paint sample procurement
- **AI-driven automation**: Adapts to website changes automatically using vision-based navigation
- **Intelligent error recovery**: Multiple fallback strategies ensure reliability  
- **User control**: Stops at cart review for secure purchase completion
- **Performance optimized**: Persistent browser session reduces startup overhead

## 🚀 Quick Start

1. **Navigate to the agent directory:**
   ```bash
   cd paint_palette_agent/
   ```

2. **Set up your environment:**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -e .
   ```

3. **Configure your API keys:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your required API keys
   # GOOGLE_API_KEY=your_actual_api_key_here
   ```

4. **Launch the agent:**
   ```bash
   adk web
   ```

5. **Open your browser** and navigate to the provided URL to start your paint consultation!

## 📁 Project Structure

```
lovely_interiors/
├── README.md                          # This file - project overview
└── paint_palette_agent/               # Main ADK agent application
    ├── README.md                      # Detailed agent documentation
    ├── main.py                        # Application entry point
    ├── pyproject.toml                 # Python project configuration
    ├── color_flow_paint_agent/        # Core agent implementation
    │   ├── agent.py                   # Main agent definition
    │   ├── prompt.py                  # Agent instructions and prompts
    │   ├── requirement_tracker.py     # Requirements tracking system
    │   └── tools/                     # Modular tool system
    │       ├── analysis/              # Photo and lighting analysis
    │       ├── catalog/               # Paint catalog management
    │       ├── export/                # Schedule export functionality
    │       ├── recommendations/       # Color recommendation engine
    │       ├── search/                # Smart color search
    │       └── validation/            # Schedule validation
    └── data/                          # Paint catalogs and knowledge base
        ├── catalogs.json              # Professional paint database (301+ colors)
        ├── knowledge/                 # Color theory and design principles
        ├── catalogs/                  # Brand-specific source data
        └── scripts/                   # Active data processing scripts
```

## 🎯 How It Works

1. **Client Interview**: The agent conducts a professional intake interview covering rooms, style preferences, lighting, and existing finishes

2. **Photo Analysis**: Upload room photos for AI-powered analysis of lighting conditions, architectural features, and existing color schemes

3. **Color Selection**: Advanced algorithms match your requirements with the paint catalog, considering undertones, LRV values, and design principles

4. **Professional Recommendations**: Receive curated color schedules with primary colors, alternates, and detailed explanations

5. **Schedule Export**: Get a comprehensive paint schedule formatted for contractors and DIY projects

6. **Sample Ordering** (Optional): Automated browser automation to order paint samples from Farrow & Ball website

## 🛠 Technology Stack

- **AI Framework**: Google Agent Development Kit (ADK)
- **Language Model**: Gemini 2.5 Pro with vision capabilities
- **Architecture**: Multi-agent system with specialized sub-agents
- **Data**: Farrow & Ball paint catalog (301+ colors) with extensible schema
- **Browser Automation**: Browser-Use v0.7+ for automated sample ordering

## 🎨 Paint Catalog System

- **Current implementation**: Farrow & Ball catalog with 301+ heritage paint colors
- **Extensible architecture**: Designed to support additional brands through CSV/JSON imports
- **Rich metadata**: Each color includes hex values, LRV, undertones, collections, and finish compatibility
- **Import tools**: Built-in utilities for adding new paint brands or color collections

## 🔧 Advanced Features

### Multi-Agent Architecture
- **Root Agent**: Main paint consultant with professional expertise
- **Photo Analysis Agent**: Specialized in visual assessment
- **Color Matching Agent**: Advanced color theory and catalog search
- **Validation Agent**: Quality assurance and schedule verification

### Professional Tools
- `search_colors_smart()` - Natural language color search with semantic matching
- `get_color_recommendations()` - Curated professional suggestions based on design theory
- `analyze_room_photos()` - Comprehensive visual analysis using computer vision
- `validate_schedule()` - Quality assurance and color availability checks
- `export_schedule()` - Generate professional paint schedules for contractors
- `order_paint_samples()` - Automated sample ordering via browser automation
- `ingest_catalog_csv()` - Import new paint brands or collections
- `refresh_catalog_from_urls()` - Update catalogs from remote sources

### Sophisticated Analysis
- Undertone harmony assessment
- LRV (Light Reflectance Value) optimization
- Material relationship analysis
- Lighting condition evaluation

## 🤝 Contributing

This project demonstrates advanced AI agent architecture and domain-specific knowledge encoding. Areas for enhancement:

- Additional paint brand catalog integrations
- Enhanced color theory and harmony algorithms
- Improved computer vision analysis capabilities
- Extended design style recognition and classification
- Performance optimizations for large catalogs
- Multi-language support for international paint brands

## 📄 License

This project is designed for professional interior design consultation. Please review the security guidelines before deployment.

---

**Built with ❤️ using Google ADK and Gemini AI**

*Transform your space with AI-powered color expertise*