import os
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, send_from_directory
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
from datetime import datetime

# --- App Initialization, DB, Login Manager (Unchanged) ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key_change_this'; app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'; app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app); login_manager = LoginManager(app); login_manager.login_view = 'login'

# --- Database Model and User Loader (Unchanged) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True); username = db.Column(db.String(150), unique=True, nullable=False); password_hash = db.Column(db.String(150), nullable=False); name = db.Column(db.String(150)); gender = db.Column(db.String(50)); age = db.Column(db.Integer)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

# --- AI Model and Data ---
MODEL_PATH = 'skin_cancer_model_trained.h5'; model = load_model(MODEL_PATH)
CLASS_NAMES = ['Actinic Keratoses (akiec)', 'Basal Cell Carcinoma (bcc)', 'Benign Keratosis-like Lesions (bkl)', 'Dermatofibroma (df)', 'Melanoma (mel)', 'Melanocytic Nevi (nv)', 'Vascular Lesions (vasc)']

# --- MODIFIED: Expanded Disease Information ---
DISEASE_INFO = {
    'Melanoma (mel)': {
        "description": "The most serious type of skin cancer. Early detection is crucial.",
        "symptoms": ["Asymmetry (one half doesn't match the other)", "Border irregularities", "Color variations (multiple shades)", "Diameter larger than 6mm", "Evolving or changing over time"],
        "risk_factors": ["Excessive UV exposure", "Fair skin", "Family history of melanoma", "Multiple moles"],
        "treatment_overview": "Treatment typically involves surgical removal. Advanced cases may require immunotherapy, targeted therapy, or chemotherapy. Always consult a specialist."
    },
    'Basal Cell Carcinoma (bcc)': {
        "description": "The most common form of skin cancer. It's slow-growing and rarely spreads.",
        "symptoms": ["A flesh-colored, pearl-like bump", "A pinkish patch of skin", "A sore that heals and then returns"],
        "risk_factors": ["Chronic sun exposure", "Fair skin", "History of radiation therapy"],
        "treatment_overview": "Common treatments include excisional surgery, Mohs surgery, and topical creams, depending on the tumor's characteristics."
    },
    'Actinic Keratoses (akiec)': {
        "description": "Also known as solar keratoses, these are dry, scaly, precancerous patches of skin.",
        "symptoms": ["Rough, dry, or scaly patch, usually less than 1 inch in diameter", "May be flat or slightly raised", "Can be pink, red, or brown"],
        "risk_factors": ["Years of sun exposure", "Fair skin and light-colored eyes/hair", "Weakened immune system"],
        "treatment_overview": "Treatments include cryotherapy (freezing), topical creams, or photodynamic therapy to prevent progression to skin cancer."
    },
    # Simplified entries for benign conditions
    'Benign Keratosis-like Lesions (bkl)': { "description": "These are non-cancerous skin growths like age spots. They are very common and harmless.", "symptoms": ["Typically brown, black or light tan", "Waxy, scaly, slightly raised appearance"], "risk_factors": ["Age", "Sun exposure"], "treatment_overview": "Generally not required unless for cosmetic reasons. Consult a doctor to confirm the diagnosis." },
    'Dermatofibroma (df)': { "description": "A common, benign skin nodule. They are small, firm bumps that are usually brown or pink.", "symptoms": ["Small, firm bump on the skin", "May be itchy or tender", "Dimples inward when pinched"], "risk_factors": ["Minor skin injuries (e.g., insect bites)", "More common in adults"], "treatment_overview": "Treatment is typically not necessary. Removal can be done for cosmetic reasons or if it causes discomfort." },
    'Melanocytic Nevi (nv)': { "description": "Commonly known as moles, these are benign growths. It's important to monitor them for changes.", "symptoms": ["Typically a small, brown spot", "Can be flat or raised, round or oval"], "risk_factors": ["Genetics", "Sun exposure, especially in childhood"], "treatment_overview": "Most moles do not require treatment. Any mole that changes in size, shape, or color should be evaluated by a dermatologist." },
    'Vascular Lesions (vasc)': { "description": "These include a range of benign conditions related to blood vessels, such as angiomas or hemorrhage.", "symptoms": ["Red or purple bumps (cherry angiomas)", "Spider-like blood vessels (spider angiomas)"], "risk_factors": ["Age", "Genetics", "Pregnancy"], "treatment_overview": "Usually not required. Cosmetic treatments include laser therapy or electrocautery." }
}
RISK_LEVELS = { 'Melanoma (mel)': 'High', 'Basal Cell Carcinoma (bcc)': 'Medium', 'Actinic Keratoses (akiec)': 'Medium', 'Melanocytic Nevi (nv)': 'Low', 'Benign Keratosis-like Lesions (bkl)': 'Low', 'Dermatofibroma (df)': 'Low', 'Vascular Lesions (vasc)': 'Low' }
RECOMMENDATIONS = { 'High': { 'text': "This prediction indicates a HIGH-RISK condition...", 'style': 'danger' }, 'Medium': { 'text': "This prediction indicates a MEDIUM-RISK condition...", 'style': 'warning' }, 'Low': { 'text': "This prediction indicates a LOW-RISK or benign condition...", 'style': 'success' }, 'Unknown': { 'text': "Could not determine risk level...", 'style': 'secondary' } }

def model_predict(img_path, model): # ... (Unchanged)
    img = Image.open(img_path).convert('RGB').resize((224, 224)); x = np.array(img); x = x / 255.0; x = np.expand_dims(x, axis=0); preds = model.predict(x); return preds

# --- Web Routes (Unchanged) ---
@app.route('/')
def index(): return render_template('index.html')
@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html', name=current_user.name or current_user.username)
# ... (Login, Register, Logout, Profile, Find Doctor Page routes are all unchanged)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')): login_user(user); return redirect(url_for('dashboard'))
        else: flash('Invalid username or password.')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if User.query.filter_by(username=request.form.get('username')).first(): flash('Username already exists.')
        else:
            new_user = User(username=request.form.get('username'), name=request.form.get('name'), gender=request.form.get('gender'), age=request.form.get('age'))
            new_user.set_password(request.form.get('password')); db.session.add(new_user); db.session.commit()
            flash('Account created successfully! Please log in.'); return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('index'))
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if not current_user.check_password(request.form.get('current_password')): flash('Your current password is incorrect.', 'danger')
        elif request.form.get('new_password') != request.form.get('confirm_password'): flash('New passwords do not match.', 'danger')
        else:
            current_user.set_password(request.form.get('new_password')); db.session.commit()
            flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html')
@app.route('/find_doctor_page')
@login_required
def find_doctor_page():
    return render_template('find_doctor.html')

# --- API Routes ---
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if 'file' not in request.files: return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'})
    if file:
        basepath = os.path.dirname(__file__); uploads_dir = os.path.join(basepath, 'uploads');
        if not os.path.exists(uploads_dir): os.makedirs(uploads_dir)
        file_path = os.path.join(uploads_dir, file.filename); file.save(file_path)
        preds = model_predict(file_path, model)
        pred_class_index = np.argmax(preds); pred_class_name = CLASS_NAMES[pred_class_index]
        
        # --- MODIFIED: Get the full details object ---
        details = DISEASE_INFO.get(pred_class_name, {"description": "No details available."})
        risk_level = RISK_LEVELS.get(pred_class_name, 'Unknown'); 
        recommendation_info = RECOMMENDATIONS.get(risk_level)
        
        return jsonify({
            'prediction': pred_class_name, 
            'details': details, # Send the whole details object
            'username': current_user.name, 
            'recommendation': recommendation_info.get('text'), 
            'recommendation_style': recommendation_info.get('style'),
            'risk_level': risk_level, 
            'filename': file.filename
        })
    return jsonify({'error': 'Something went wrong'})
    
# ... (generate_report and find_dermatologists routes are unchanged) ...
@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    data = request.get_json()
    filename = data.get('filename')
    image_path = os.path.join('uploads', filename)
    pdf = FPDF()
    pdf.add_page(); pdf.set_font('Helvetica', 'B', 20); pdf.cell(0, 10, 'DermaScan Analysis Report', 0, 1, 'C'); pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 12); pdf.cell(0, 10, 'Patient Details', 0, 1); pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f"Name: {current_user.name or 'N/A'}", 0, 1); pdf.cell(0, 8, f"Age: {current_user.age or 'N/A'}", 0, 1); pdf.cell(0, 8, f"Gender: {current_user.gender or 'N/A'}", 0, 1); pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 12); pdf.cell(0, 10, 'Analysis Details', 0, 1); pdf.set_font('Helvetica', '', 11)
    # The 'description' key in the report now comes from inside the 'details' object
    analysis_text = (f"Prediction: {data.get('prediction')}\n" f"Risk Level: {data.get('risk_level')}\n\n" f"Description: {data.get('details', {}).get('description', '')}")
    pdf.multi_cell(0, 8, analysis_text); pdf.ln(10)
    if os.path.exists(image_path): pdf.image(image_path, w=80); pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 12); pdf.cell(0, 10, 'Recommendation', 0, 1); pdf.set_font('Helvetica', '', 11); pdf.multi_cell(0, 8, data.get('recommendation')); pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9); pdf.multi_cell(0, 5, "Disclaimer: This AI-generated report is for informational purposes only...")
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports');
    if not os.path.exists(reports_dir): os.makedirs(reports_dir)
    report_filename = f"report_{os.path.splitext(filename)[0]}.pdf"; pdf_output_path = os.path.join(reports_dir, report_filename); pdf.output(pdf_output_path)
    if os.path.exists(image_path): os.remove(image_path)
    return send_from_directory(directory=reports_dir, path=report_filename, as_attachment=True)
@app.route('/find_dermatologists', methods=['POST'])
@login_required
def find_dermatologists():
    data = request.get_json()
    city = data.get('city', 'Mumbai')
    try:
        query = f"dermatologists in {city}"; encoded_query = quote_plus(query); search_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}";
        return jsonify({'search_url': search_url})
    except Exception as e:
        print(f"Error in find_dermatologists: {e}")
        return jsonify({'error': 'An internal error occurred.'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)