# 🌱 AgroFarm AI
### An Intelligent Multimodal Explainable AI Platform for Smart Precision Agriculture

**Making agricultural decisions smarter, more transparent, and data-driven with Artificial Intelligence.**

AgroFarm AI is an AI-powered precision agriculture platform designed to assist farmers with crop selection, agricultural data analysis, farming recommendations, and intelligent decision support. The platform combines machine learning, web technologies, and explainable AI to make agricultural predictions more understandable.

<!-- Replace this placeholder with a genuine screenshot of your application -->
<!-- ![AgroFarm AI Dashboard](docs/images/dashboard.png) -->

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Machine Learning and Explainable AI](#-machine-learning-and-explainable-ai)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Configuration](#-environment-configuration)
- [Running the Application](#-running-the-application)
- [Model Status](#-model-status)
- [Datasets](#-datasets)
- [Security](#-security)
- [Limitations](#-limitations)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌾 Overview

Agriculture depends on several factors, including soil characteristics, climate, crop selection, and market conditions. Making informed decisions from these factors can be challenging when data and analytical tools are scattered across different sources.

AgroFarm AI aims to bring these capabilities together in a unified platform.

The project combines a web-based user interface, backend APIs, agricultural datasets, and machine learning components to support data-driven agricultural decisions.

### 🎯 Project Objectives

- Support crop selection using machine learning.
- Provide interpretable predictions through Explainable AI.
- Organize agricultural information through an integrated dashboard.
- Explore crop health, pest, weed, yield, and market-related prediction capabilities.
- Provide a modular foundation for future precision agriculture applications.

---

## ✨ Key Features

### 🌱 1. Crop Recommendation
- Machine-learning-based crop prediction.
- Agricultural feature input and prediction workflows.
- Data-driven assistance for crop selection.

### 🧠 2. Explainable AI
- SHAP-based interpretation for supported machine learning predictions.
- Feature-contribution insights to help users understand model outputs.
- An emphasis on model transparency rather than predictions alone.

### 🌿 3. Agricultural Analysis
The project includes data and application components for exploring:

- Soil and agricultural information.
- Fertilizer-related recommendations.
- Crop yield analysis.
- Market price analysis.
- Weather information and agricultural assistance.

The availability of individual features depends on their current implementation and configuration.

### 🔬 4. Crop Health and Field Analysis

The project includes datasets and supporting components for exploring:

- Plant disease classification.
- Pest identification.
- Weed classification.
- Crop image analysis.

These capabilities require the appropriate trained models and validated inference pipelines before they can be considered production-ready.

### 📊 5. Analytics and Evaluation
- Model evaluation scripts.
- Performance visualization support.
- Dataset-driven experimentation.
- A foundation for comparing machine learning approaches.

### 💻 6. Web Application
- React-based user interface.
- Backend API integration.
- Modular application pages.
- A structure designed to support further feature development.

---

## 🏗️ System Architecture

AgroFarm AI follows a modular architecture that separates the user interface, backend logic, data, and machine learning components.

```text
                  ┌──────────────────────────┐
                  │        User              │
                  └────────────┬─────────────┘
                               │
                  ┌────────────▼─────────────┐
                  │     React Frontend       │
                  │     Vite Development     │
                  └────────────┬─────────────┘
                               │ HTTP / REST API
                  ┌────────────▼─────────────┐
                  │       FastAPI Backend    │
                  │ Authentication and APIs  │
                  └────────────┬─────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
       ┌────────▼──────┐ ┌─────▼──────┐ ┌────▼────────┐
       │ ML Inference  │ │ Database   │ │ External    │
       │ and Prediction│ │ and Data   │ │ APIs        │
       └────────┬──────┘ └────────────┘ └─────────────┘
                │
       ┌────────▼────────┐
       │ ML Models and   │
       │ Explainability  │
       └─────────────────┘
```

*This is a conceptual overview. Update the diagram if the implemented request flow or deployment architecture differs.*

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Frontend | React, JavaScript, Vite |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn, XGBoost, Pandas, NumPy |
| Explainable AI | SHAP |
| Data Storage | SQLite configuration and agricultural CSV datasets |
| API Integration | REST APIs |
| Development Tools | Git, GitHub, Visual Studio Code |

*The table describes the project's intended technology areas. Retain only packages and services confirmed in the final implementation and dependency files.*

---

## 🤖 Machine Learning and Explainable AI

Machine learning is a central component of AgroFarm AI.

The project contains datasets, training scripts, inference-related code, and saved model artifacts for agricultural prediction tasks.

### Crop Recommendation

The crop recommendation workflow is designed to use agricultural input features to predict a suitable crop using a trained machine learning model.

The prediction pipeline can be evaluated using classification metrics such as:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

### Explainable AI with SHAP

SHAP (SHapley Additive exPlanations) can help explain how input features contribute to a supported model prediction.

The goal is to improve transparency and help users understand the factors influencing an output.

### Model Evaluation

Model performance should be reported only after evaluation on an appropriate held-out dataset. Training results alone should not be presented as evidence of real-world agricultural accuracy.

---

## 📂 Project Structure

The repository contains the following major project components:

```text
AgroFarm-AI/
├── app/                    # Application entry points and schemas
├── backend/                # FastAPI backend
│   └── app/
│       ├── core/            # Core configuration and security
│       ├── ml/              # ML-related components
│       ├── models/          # Data models
│       ├── routers/         # API routes
│       └── utils/           # Utility modules
├── datasets/                # Agricultural datasets
│   └── vision/              # Image datasets
├── frontend/                # Frontend-related assets
├── ml/                      # ML evaluation artifacts
├── saved_models/            # Local model artifacts, if present
├── web/                     # React frontend
│   └── src/
├── crop_inference.py        # Crop inference-related code
├── evaluation.py            # Evaluation utilities
├── fertilizer_rules.py      # Fertilizer-related logic
├── train_models.py          # Model training script
├── train_publication.py     # Additional training/evaluation script
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

*Directory contents may vary between local and GitHub copies. Model artifacts and generated evaluation files may be intentionally excluded from version control.*

---

## 🚀 Getting Started

### Prerequisites

Install the following tools before running the project:

- Python compatible with the project's dependencies.
- Node.js and npm.
- Git.
- Visual Studio Code (recommended).

### 1. Clone the Repository

```bash
git clone https://github.com/ukvarma25/Agri.git
cd Agri
```

If the source files are located inside a nested `Agri/` directory in the repository, enter that directory before continuing.

### 2. Set Up the Python Environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

If the backend has a separate dependency file, install those dependencies as well:

```powershell
pip install -r backend/requirements.txt
```

Only run the second installation if that file exists and is required by your setup.

### 3. Configure Environment Variables

Create a local environment file using the example configuration:

```powershell
Copy-Item backend\.env.example backend\.env
```

If `backend\.env` already exists, do not overwrite it blindly.

Update the local configuration with the credentials and settings required by your environment.

### 4. Start the Backend

From the project root, run:

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

If the application entry point or import path differs in your checked-out version, use the startup command documented for that version.

When available, backend API documentation can usually be accessed at:

`http://127.0.0.1:8000/docs`

### 5. Start the Frontend

Open a second terminal and navigate to the frontend directory:

```powershell
cd web
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal.

**Important:** The commands above are a setup guide, not a claim that every environment has been verified. Confirm the correct entry points, scripts, dependency files, and API configuration against your current code before publishing these instructions as tested.

---

## ⚙️ Environment Configuration

The backend example configuration may include variables such as:

```dotenv
DATABASE_URL=sqlite:///./agrofarm.db
SECRET_KEY=replace-with-a-secure-random-value
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

OPENWEATHER_API_KEY=
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
GROQ_BASE_URL=https://api.groq.com/openai/v1

CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

Configure only the integrations required by your version of the application.

Never commit real API keys, production credentials, or personal secrets.

---

## 📈 Model Status

Model availability must be reported separately from application UI availability.

| Component | Status |
|---|---|
| Crop recommendation | Verify model availability and inference locally |
| SHAP explanations | Verify against the actual supported model |
| Disease detection | Requires verified trained weights and inference testing |
| Pest detection | Requires verified trained weights and inference testing |
| Weed detection | Requires verified trained weights and inference testing |
| Yield prediction | Requires a verified trained model and evaluation |
| Market price prediction | Requires a verified trained model and evaluation |
| Fertilizer recommendations | Verify implementation and input validation |

Update this table with evidence from the current codebase and successful tests before presenting the project as complete.

---

## 📚 Datasets

The project contains agricultural tabular datasets and sample image data organized for machine learning experiments.

Dataset documentation should include:

- Dataset name and source.
- License and permitted usage.
- Features and target labels.
- Number of records or images.
- Preprocessing steps.
- Training, validation, and test split methodology.

Do not redistribute datasets unless their licenses permit it. Include source references and attribution where required.

---

## 🔐 Security

Security practices for this project include:

- Keeping local `.env` files out of version control.
- Using environment variables for credentials.
- Excluding virtual environments and generated files from Git.
- Using secure secret keys for deployed environments.
- Validating user input and protecting authenticated API routes.

Before making the repository public, review the complete Git history and current files for accidentally committed credentials.

---

## ⚠️ Limitations

AgroFarm AI is a development and research project. Its outputs should not automatically be treated as validated agronomic advice.

- Model predictions depend on the quality and representativeness of the training data.
- Real-world performance may differ from offline evaluation results.
- Untrained or unavailable models cannot provide validated predictions.
- External integrations may require valid credentials and network access.
- Agricultural decisions should consider local conditions and qualified expert guidance.

---

## 🔮 Future Enhancements

Potential future improvements include:

- Validated plant disease classification.
- Pest and weed detection using object detection models.
- Explainability visualizations for supported predictions.
- Weather-aware crop recommendations.
- District-level yield prediction.
- Agricultural market price forecasting.
- Improved dataset provenance and model versioning.
- Automated testing and continuous integration.
- Deployment with secure configuration and monitoring.

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Commit with a descriptive message.
5. Open a pull request explaining the changes.

Please do not include private credentials or datasets that you are not authorized to redistribute.

---

## 📄 License

A license has not yet been specified for this repository.

Before adding an open-source license, choose one that matches your intended usage and any third-party dataset or code restrictions. Until a license is added, others generally should not assume they have permission to reuse or redistribute the project.

---

## 👨‍💻 Author

**Uday Kumar Varma**

B.Tech — Computer Science and Engineering (Data Science)

GitHub: [@ukvarma25](https://github.com/ukvarma25)

---

*AgroFarm AI — Exploring the future of intelligent and explainable precision agriculture.*
