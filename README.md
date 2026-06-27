# 🛡️ DermaScan: AI-Powered Skin Health Analyzer

DermaScan is a full-stack, educational web application designed to raise awareness about skin health. It utilizes a deep learning model to classify images of skin lesions into seven distinct categories, providing users with immediate educational feedback, risk assessments, and guidance on seeking professional medical advice.

## ✨ Key Features

* **🧠 AI-Powered Classification:** Upload a skin lesion image, and the Convolutional Neural Network (CNN) predicts the most likely condition among 7 classes.
* **📊 Detailed Health Insights:** Results include an expandable accordion detailing a description, common symptoms, risk factors, and a treatment overview for the predicted condition.
* **🚦 Risk Assessment:** Automatically categorizes the prediction into High, Medium, or Low risk, accompanied by color-coded alerts.
* **📄 Downloadable PDF Reports:** Users can generate and download a personalized, cleanly formatted PDF report of their analysis to share with a medical professional.
* **🏥 Find a Dermatologist:** A built-in search tool that integrates with Google Maps to help users locate a certified dermatologist in their city.
* **🔐 Secure User System:** Full user authentication (registration, login, profile management) with secure password hashing.
* **💡 Dynamic Dashboard:** A personalized user dashboard featuring a daily skin health tip.

## 🛠️ Technology Stack

**Machine Learning & AI**
* **TensorFlow / Keras:** For building, training, and running the neural network.
* **Transfer Learning:** Utilizes the **MobileNetV2** base architecture.
* **Algorithm Improvement:** Implements class weights during training to combat dataset imbalance and ensure accurate predictions across all rare and common classes.

**Backend**
* **Python / Flask:** Core server logic and routing.
* **Flask-SQLAlchemy:** Database ORM for managing user accounts via SQLite.
* **Flask-Login:** Session management and route protection.
* **FPDF:** Dynamic PDF report generation.

**Frontend**
* **HTML5, CSS3, JavaScript (ES6)**
* **Bootstrap 5:** For a responsive, modern, and clean user interface.

## 📂 Dataset Information

The AI model was trained using the **HAM10000 (Human Against Machine with 10000 training images)** dataset. This is a large collection of multi-source dermatoscopic images of common pigmented skin lesions, encompassing the following categories:
1. Actinic keratoses and intraepithelial carcinoma (akiec)
2. Basal cell carcinoma (bcc)
3. Benign keratosis-like lesions (bkl)
4. Dermatofibroma (df)
5. Melanoma (mel)
6. Melanocytic nevi (nv)
7. Vascular lesions (vasc)

## 🚀 How to Run Locally

*Note: The trained model (`.h5` file) and raw dataset are excluded from this repository due to size limits. You must train the model locally using `train_model.py` before running the web app.*

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/dermascan-ai.git](https://github.com/YourUsername/dermascan-ai.git)
   cd dermascan-ai
Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
(Ensure your requirements.txt includes Flask, tensorflow, Pillow, numpy, Flask-SQLAlchemy, Flask-Login, Werkzeug, fpdf, scikit-learn, pandas, matplotlib)

Train the model (if you haven't already):

Bash
python train_model.py
Start the Flask server:

Bash
python app.py
