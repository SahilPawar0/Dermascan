document.addEventListener('DOMContentLoaded', () => {
    const findDermatologistButton = document.getElementById('btn-find-dermatologist');
    const cityInput = document.getElementById('city-input');

    const searchDermatologists = () => {
        const city = cityInput.value.trim();
        if (!city) {
            alert('Please enter a city name.');
            return;
        }

        // Show loading state on button
        const originalButtonHtml = findDermatologistButton.innerHTML;
        findDermatologistButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Searching...`;
        findDermatologistButton.disabled = true;

        fetch('/find_dermatologists', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ city: city })
        })
        .then(response => response.json())
        .then(data => {
            if (data.search_url) {
                // Open the Google Maps search results in a new tab
                window.open(data.search_url, '_blank');
            } else {
                alert('Could not generate a search link. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error fetching dermatologists:', error);
            alert('An error occurred while fetching data.');
        })
        .finally(() => {
            // Restore button state
            findDermatologistButton.innerHTML = originalButtonHtml;
            findDermatologistButton.disabled = false;
        });
    };

    findDermatologistButton.addEventListener('click', searchDermatologists);
    
    cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchDermatologists();
        }
    });
});