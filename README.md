# 🌱 AgroFarm AI

### An Intelligent Multimodal Explainable AI Platform for Smart Precision Agriculture

**Smarter agricultural decisions through Machine Learning, Computer Vision, and Explainable AI.**

AgroFarm AI is an academic AI-powered precision agriculture project designed to bring agricultural data analysis, crop recommendation, and interpretable machine learning into a unified web application.

The project explores how machine learning, deep learning, weather intelligence, and Explainable AI can help farmers and agricultural stakeholders make more informed decisions.

[**View Repository**](https://github.com/ukvarma25/Agri)

---

## 📌 About the Project

Agriculture faces challenges such as crop diseases, nutrient deficiencies, unpredictable weather, inefficient resource utilization, and limited access to timely agricultural guidance.

Traditional approaches often address these problems separately. AgroFarm AI explores an integrated approach that brings multiple agricultural workflows together and makes supported machine-learning predictions easier to interpret.

### 🎯 Project Objectives

- Develop a data-driven crop recommendation system.
- Integrate agricultural data processing and machine learning into a web application.
- Use Explainable AI to improve the interpretability of supported predictions.
- Explore crop-health analysis, fertilizer recommendations, yield prediction, and agricultural risk assessment.
- Provide a foundation for multilingual agricultural assistance and consolidated farm reports.

## ✨ Key Features

### 🌾 Crop Recommendation
Use agricultural input features to generate crop recommendations through the supported machine-learning pipeline.

### 🧠 Explainable AI
Use SHAP-based feature-contribution explanations to help users understand the supported crop recommendation model's outputs.

### 🌿 Agricultural Analysis
The application includes or is designed to support workflows for soil analysis, fertilizer recommendations, crop health, and farm information.

### 🌦️ Weather and Risk Intelligence
The project design incorporates weather information and agricultural risk assessment to support more context-aware decisions, subject to available integrations.

### 🔬 Crop Health and Computer Vision
Disease, pest, weed, and nutrient-deficiency analysis are part of the broader project scope. These capabilities require their corresponding trained models and validated inference pipelines.

### 📊 Analytics and Reports
The platform is designed to organize prediction outputs, evaluation information, and agricultural insights through a unified interface.

### 💬 AI-Assisted Agricultural Guidance
The project explores an agricultural assistant to help users interact with farming information. Its functionality depends on the configured AI service and available application context.

---

## 🏗️ System Architecture

AgroFarm AI separates the web interface, backend application logic, data processing, and machine-learning components.

<img width="2300" height="1742" alt="system architecture" src="https://github.com/user-attachments/assets/32f4c79d-5d58-47c1-973e-78ce91511f9b" />


*This is a conceptual architecture. Refer to the current source code and service configuration for the exact implementation.*

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, JavaScript, Vite |
| Backend | Python, FastAPI |
| Machine Learning | XGBoost and Python data-science libraries |
| Explainable AI | SHAP |
| Data Processing | Pandas, NumPy |
| Data Sources | Agricultural datasets and CSV files |
| Development | Git, GitHub, Visual Studio Code |

*The actual installed dependencies and integrated services are defined by the repository's code and configuration files.*

---

## 🤖 Machine Learning and Explainability

### Crop Recommendation

The crop recommendation component uses a trained XGBoost multiclass classification model in the audited development setup.

The workflow consists of:

1. Receiving agricultural input features.
2. Preparing the input for the model.
3. Generating a crop prediction.
4. Producing SHAP-based feature-contribution information.
5. Presenting the output through the application.

### Explainable AI with SHAP

SHAP (SHapley Additive exPlanations) helps explain how input features contribute to a model's output.

This is important in agricultural decision support because users need more than a prediction: they also need to understand which input factors influenced it.

Explanations are meaningful only for a supported model and its actual inference pipeline.

### Model Evaluation

Classification models can be evaluated using accuracy, precision, recall, F1-score, and confusion matrices. Regression models can be evaluated using MAE, RMSE, and R².

Performance results should be published only when they can be traced to the corresponding dataset, model version, and evaluation procedure.

---

## 📊 Model and Feature Status

AgroFarm AI is an evolving academic prototype. Not every planned feature currently has a trained and validated model.

| Module | Status |
|---|---|
| Crop recommendation | Trained model available in the audited development setup |
| SHAP crop explanation | Integrated for the supported model |
| Plant disease detection | Training required unless valid trained weights are supplied |
| Nutrient-deficiency detection | Training required unless valid trained weights are supplied |
| Pest detection | Training required unless valid trained weights are supplied |
| Weed detection | Training required unless valid trained weights are supplied |
| Yield prediction | Training required unless a valid trained model is supplied |
| Smart irrigation | Rule-based or simulation workflow where implemented |
| Weather and AI assistant | Depends on configuration and available integrations |

**Important:** A visible interface or sample visualization does not establish that an underlying model is trained. Unavailable modules should report their status clearly rather than generate fabricated predictions.

---

## 📂 Project Structure

The repository contains frontend, backend, and machine-learning components. The exact directory layout may vary by revision.

```text
AgroFarm-AI/
├── backend/
│   └── app/
├── web/
│   └── src/
├── ml/
│   └── saved_models/
├── datasets/
├── requirements.txt
├── .gitignore
└── README.md
```

Large model artifacts, local databases, generated evaluation files, and virtual environments may be excluded from version control.

Check the actual repository tree before assuming every listed directory is present.

---

## 🚀 Getting Started

### Prerequisites

- Python compatible with the project dependencies
- Node.js and npm
- Git
- Visual Studio Code (recommended)

### 1. Clone the repository

```powershell
git clone https://github.com/ukvarma25/Agri.git
cd Agri
```

If the project is stored inside a nested `Agri` directory, enter that directory before continuing.

### 2. Create the Python environment

Run the following commands from the directory containing the relevant `requirements.txt`:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure the backend

If the example file exists and you do not already have a local configuration:

```powershell
Copy-Item backend\.env.example backend\.env
```

Do not overwrite an existing `.env` file without checking its contents.

### 4. Start the backend

From the appropriate project root:

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

If your checkout uses a different application entry point, follow its actual backend configuration.

### 5. Start the frontend

Open a second terminal:

```powershell
cd web
npm install
npm run dev
```

Open the local URL printed by Vite.

### 6. Verify the application

- Confirm that the backend starts successfully.
- Confirm that the frontend loads.
- Test the crop recommendation workflow.
- Verify the corresponding SHAP explanation.
- Check that unavailable models display an appropriate status.

These are setup instructions to validate against the current checkout, not a guarantee that every installation or feature has been tested.

---

## 🔐 Security

- Keep API keys and passwords in local environment files.
- Never commit real secrets or production credentials.
- Keep virtual environments and unnecessary generated artifacts out of Git.
- Use secure secret keys for deployed environments.
- Review the repository's current files and Git history before making it public.

Adding a file to `.gitignore` does not remove a secret that was committed previously.

## 📷 Screenshots and Demo

Add genuine screenshots from the running application to `docs/images/` and link them here.

| Screenshot | Suggested file |
|---|---|
| Dashboard | `docs/images/dashboard.png` |
| Crop recommendation | `docs/images/crop-recommendation.png` |
| SHAP explanation | `docs/images/shap-explanation.png` |
| Fertilizer recommendation | `docs/images/fertilizer.png` |
| AI assistant | `docs/images/assistant.png` |

Replace these placeholders with real screenshots before presenting the README as complete.

## 🔭 Future Enhancements

- Train and validate additional crop-health models.
- Improve dataset documentation and reproducibility.
- Expand weather-aware agricultural analysis.
- Strengthen model evaluation and automated testing.
- Improve multilingual and voice-based assistance.
- Explore IoT sensors and remote-sensing data integration.
- Develop secure, reliable deployment workflows.
- 
**Project repository:** [github.com/ukvarma25/Agri](https://github.com/ukvarma25/Agri)


---

*AgroFarm AI — towards more transparent, data-driven precision agriculture.*
