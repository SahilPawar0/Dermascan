document.addEventListener('DOMContentLoaded', () => {
    // --- Variable Declarations ---
    const predictButton = document.getElementById('btn-predict');
    const resultContainer = document.getElementById('result-container');
    const resultHeader = document.getElementById('result-header');
    const resultText = document.getElementById('result');
    const recommendationAlert = document.getElementById('recommendation-alert');
    const recommendationText = document.getElementById('recommendation-text');
    const downloadButton = document.getElementById('btn-download');
    let reportData = {};

    // --- NEW: Accordion body elements ---
    const descriptionBody = document.getElementById('description-body');
    const symptomsBody = document.getElementById('symptoms-body');
    const riskFactorsBody = document.getElementById('risk-factors-body');
    const treatmentBody = document.getElementById('treatment-body');
    
    // ... (rest of variable declarations and drag-and-drop logic is unchanged) ...
    const imageUpload = document.getElementById('imageUpload'); const imagePreview = document.getElementById('imagePreview'); const previewImage = imagePreview.querySelector('.image-preview__image'); const previewDefaultText = imagePreview.querySelector('.image-preview__default-text'); const spinner = document.getElementById('spinner'); const predictText = document.getElementById('predict-text'); const findDermatologistButton = document.getElementById('find_doctor_page'); // Corrected ID if needed
    imagePreview.addEventListener('click', () => imageUpload.click());
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => imagePreview.addEventListener(e, preventDefaults, false)); function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
    ['dragenter', 'dragover'].forEach(e => imagePreview.addEventListener(e, () => imagePreview.classList.add('drag-over'), false));
    ['dragleave', 'drop'].forEach(e => imagePreview.addEventListener(e, () => imagePreview.classList.remove('drag-over'), false));
    imagePreview.addEventListener('drop', e => handleFiles(e.dataTransfer.files), false);
    imageUpload.addEventListener('change', function() { handleFiles(this.files); });
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            previewDefaultText.style.display = 'none'; previewImage.style.display = 'block';
            const reader = new FileReader(); reader.onload = (e) => { previewImage.setAttribute('src', e.target.result); }; reader.readAsDataURL(file);
            resultContainer.classList.add('hidden');
        }
    }

    // --- Predict Button Logic ---
    predictButton.addEventListener('click', () => {
        const file = imageUpload.files[0];
        if (!file) { alert('Please upload an image first.'); return; }
        const formData = new FormData(); formData.append('file', file);
        
        predictText.textContent = 'Analyzing...'; spinner.classList.remove('hidden'); predictButton.disabled = true; resultContainer.classList.add('hidden');

        fetch('/predict', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                resultContainer.classList.remove('hidden');
                if (data.error) {
                    resultHeader.textContent = 'Prediction Result'; resultText.textContent = `Error: ${data.error}`;
                    recommendationAlert.classList.add('hidden'); downloadButton.classList.add('hidden');
                } else {
                    reportData = data; // Store all data for the report
                    resultHeader.textContent = `Analysis for: ${data.username}`;
                    resultText.textContent = data.prediction;
                    
                    const prediction = data.prediction.toLowerCase();
                    resultText.className = (prediction.includes('melanoma') || prediction.includes('carcinoma')) ? 'result-badge is-melanoma' : 'result-badge is-benign';
                    
                    if (data.recommendation) {
                        recommendationText.textContent = data.recommendation;
                        recommendationAlert.className = `alert mt-4 alert-${data.recommendation_style}`;
                        recommendationAlert.classList.remove('hidden');
                    }
                    
                    // --- NEW: Populate Accordion ---
                    const details = data.details;
                    descriptionBody.innerHTML = `<p>${details.description || ''}</p>`;
                    symptomsBody.innerHTML = createList(details.symptoms) || '<p>No specific symptoms listed.</p>';
                    riskFactorsBody.innerHTML = createList(details.risk_factors) || '<p>No specific risk factors listed.</p>';
                    treatmentBody.innerHTML = `<p>${details.treatment_overview || 'No specific treatment overview listed.'}</p>`;
                    
                    downloadButton.classList.remove('hidden');
                }
            })
            .catch(error => { console.error('Error:', error); resultContainer.classList.remove('hidden'); resultText.textContent = 'An error occurred.'; })
            .finally(() => { predictText.textContent = 'Classify'; spinner.classList.add('hidden'); predictButton.disabled = false; });
    });

    // --- NEW: Helper function to create lists ---
    function createList(items) {
        if (!items || items.length === 0) return null;
        let listHtml = '<ul class="list-group list-group-flush">';
        items.forEach(item => {
            listHtml += `<li class="list-group-item">${item}</li>`;
        });
        listHtml += '</ul>';
        return listHtml;
    }

    // --- Download and Dermatologist Logic (Unchanged) ---
    downloadButton.addEventListener('click', () => { /* ... (This code is unchanged) ... */
        downloadButton.disabled = true; downloadButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating...';
        fetch('/generate_report', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(reportData) })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob); const a = document.createElement('a'); a.style.display = 'none'; a.href = url;
            a.download = `DermaScan_Report_${reportData.filename.split('.')[0]}.pdf`; document.body.appendChild(a); a.click();
            window.URL.revokeObjectURL(url); a.remove();
        })
        .catch(error => console.error('Error generating report:', error))
        .finally(() => { downloadButton.disabled = false; downloadButton.innerHTML = '<i class="bi bi-download"></i> Download Report'; });
    });
    const findDoctorBtn = document.querySelector('a[href*="find_doctor_page"]'); // This assumes the button is now a link
    // The logic is now just a simple link, no JS needed for the find doctor button on the dashboard itself.
});