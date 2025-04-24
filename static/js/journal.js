// the journal page functionality
document.addEventListener('DOMContentLoaded', () => {
    const moodSelect = document.getElementById('mood');
    const journalForm = document.querySelector('.journal-form');
    const entryTextarea = document.getElementById('entry');
    const flashMessages = document.querySelectorAll('.flash-message');
    
    // shows any flash messages
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.display = 'none';
        }, 4000);
    });
    
    // handle mood selection
    if (moodSelect) {
        moodSelect.addEventListener('change', () => {
            const mood = moodSelect.value;
            const greetings = {
                'Happy': "Great to hear you're feeling happy!",
                'Sad': "It's okay to feel sad. Let's write down something.",
                'Anxious': "Take a deep breath. You've got this.",
                'Stressed': "Try to relax and take a break!",
                'Calm': "Calm is the way to go!"
            };
            
            if (greetings[mood]) {
                showPopup(greetings[mood]);
            }
        });
    }
    
    //checks if you actually put something or not and makes sure its 10+ words long.
    if (journalForm) {
        journalForm.addEventListener('submit', (e) => {
            const mood = moodSelect.value;
            const entry = entryTextarea.value.trim();
            
            if (!mood) {
                e.preventDefault();
                showPopup("⚠️ Please select a mood before submitting.");
                return;
            }
            
            if (entry.length < 10) {
                e.preventDefault();
                showPopup("I notice your writing is short, did you want to write more?");
                return;
            }
        });
    }
    
    // custom popup/toast message functionality
    function showPopup(message) {
        // create the popup element
        const popup = document.createElement('div');
        popup.className = 'popup';
        
        const popupContent = document.createElement('div');
        popupContent.className = 'popup-content';
        
        const closeBtn = document.createElement('span');
        closeBtn.className = 'close-btn';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', () => {
            popup.remove();
        });
        
        const messageEl = document.createElement('p');
        messageEl.textContent = message;
        
        popupContent.appendChild(closeBtn);
        popupContent.appendChild(messageEl);
        popup.appendChild(popupContent);
        
        document.body.appendChild(popup);
        
        // auto-removes after 4 seconds
        setTimeout(() => {
            if (document.body.contains(popup)) {
                popup.remove();
            }
        }, 4000);
    }
    
    // load mood chart if on journal page with chart container
    const chartContainer = document.getElementById('moodChartContainer');
    if (chartContainer) {
        fetchMoodData();
    }
});

// grabs data from the chart
function fetchMoodData() {
    fetch('/api/journal_entries')
        .then(response => response.json())
        .then(data => {
            initMoodChart(data);
        })
        .catch(error => {
            console.error('Error fetching mood data:', error);
        });
}
