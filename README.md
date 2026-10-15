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


| Screenshot | Suggested file |
|---|---|
| Dashboard | <img width="1886" height="877" alt="Screenshot (43)" src="https://github.com/user-attachments/assets/101cc234-083e-4876-99f2-cb69436bfbef" /> |
| Crop recommendation | <img width="1887" height="866" alt="Screenshot (44)" src="https://github.com/user-attachments/assets/ed040c9f-190c-4108-a1b4-277732487bab" />|
| SHAP explanation | <img width="1895" height="874" alt="Screenshot (54)" src="https://github.com/user-attachments/assets/1e24cd0c-d56c-4bf5-85a7-9050a716e95e" /> |
| Fertilizer recommendation | <img width="1920" height="855" alt="Screenshot (49)" src="https://github.com/user-attachments/assets/bd2e8640-2fcd-4c7e-a809-6d50f1e7b348" /> |
| AI assistant |<img width="1917" height="853" alt="Screenshot (53)" src="https://github.com/user-attachments/assets/9f3401e6-d50d-460f-8f65-4e192b06a3a0" />
|



## 🔭 Future Enhancements

- Train and validate additional crop-health models.
- Improve dataset documentation and reproducibility.
- Expand weather-aware agricultural analysis.
- Strengthen model evaluation and automated testing.
- Improve multilingual and voice-based assistance.
- Explore IoT sensors and remote-sensing data integration.
- Develop secure, reliable deployment workflows.
- 
**Project repository:** (https://github.com/ukvarma25/AgroFarm-AI-Platform)


---

*AgroFarm AI — towards more transparent, data-driven precision agriculture.*
