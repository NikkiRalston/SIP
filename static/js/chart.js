// scatter chart
function initMoodChart(data) {
    const ctx = document.getElementById('moodChart').getContext('2d');
    // remove padding
    Chart.defaults.layout.padding = 0;
    
    //colors for mood
    const moodColors = {
        'Happy': 'rgba(255, 206, 86, 1)',   // Yellow
        'Calm': 'rgba(75, 192, 192, 1)',    // Teal
        'Neutral': 'rgba(153, 102, 255, 1)', // Purple
        'Anxious': 'rgba(255, 159, 64, 1)',  // Orange
        'Stressed': 'rgba(255, 99, 132, 1)', // Red
        'Sad': 'rgba(54, 162, 235, 1)'       // Blue
    };
    
    // creating datasets for scatter plot
    const moodLabels = {
        0: 'Sad',
        1: 'Stressed',
        2: 'Anxious', 
        3: 'Neutral',
        4: 'Calm',
        5: 'Happy'
    };
    
    // configuring the point colors based on mood
    const pointColors = data.map(entry => moodColors[entry.mood] || 'rgba(153, 102, 255, 1)');
    
    // making sure all points are visible
    const pointBorderColors = data.map(entry => {
        const baseColor = moodColors[entry.mood] || 'rgba(153, 102, 255, 1)';
        return baseColor.replace('1)', '0.8)'); // transparent border
    });
    
    // creating the chart
    const moodChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Mood Over Time',
                data: data,
                backgroundColor: pointColors,
                borderColor: pointBorderColors,
                borderWidth: 2,
                pointRadius: 7,
                pointHoverRadius: 10,                
                pointStyle: 'circle'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: 0 // removes any default extra padding
            },
            scales: {
                x: {
                    type: 'time',
                    offset: false,
                    bounds: 'data',
                    time: {
                        unit: 'day', 
                        displayFormats: {
                            day: 'MMM dd' 
                        },
                        tooltipFormat: 'MMMM dd, yyyy' 
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)', // light grid lines
                        borderColor: 'rgba(0, 0, 0, 0.1)', // border line for the axis
                        drawBorder: true,
                        borderWidth: 2
                    },
                    ticks: {
                        source: 'data', // show ticks ONLY for actual journal entry dates
                        autoSkip: false, // don't skip any ticks so all entries are shown
                        maxRotation: 45, 
                        minRotation: 45,
                        font: {
                            weight: 'bold',
                            size: 11
                        },
                        color: '#333' 
                    },
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 10
                        },
                        color: '#2c3e50' 
                    }
                },
                y: {
                    min: -0.5,
                    max: 5.5,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        borderColor: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return moodLabels[value] || '';
                        },
                        font: {
                            weight: 'bold'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Mood',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#2c3e50'
                    }
                }
            },
            plugins: {
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleColor: '#2c3e50',
                    bodyColor: '#333',
                    titleFont: {
                        weight: 'bold',
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 6,
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    callbacks: {
                        title: function(context) {
                            // using a custom title showing the full date
                            return context[0].raw.date;
                        },
                        label: function(context) {
                            const point = context.raw;
                            return [
                                `Mood: ${point.mood}`,
                                `Entry: ${point.entry_preview}`
                            ];
                        }
                    }
                },
                legend: {
                    display: false
                }
            },
            // no extra padding
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
    
    // creating the legend for mood colors
    createCustomLegend(moodColors);
}

// creating custom legend for mood colors
function createCustomLegend(moodColors) {
    const legendContainer = document.getElementById('moodLegend');
    if (!legendContainer) return;
    
    // clearing any existing content
    legendContainer.innerHTML = '';
    
    const ul = document.createElement('ul');
    ul.className = 'mood-legend';
    
    // creating a more compact header for the legend
    const header = document.createElement('div');
    header.textContent = 'Mood Colors';
    header.className = 'mood-legend-header';
    
    legendContainer.appendChild(header);
    
    // sorting the moods in a logical flow from positive to negative
    const moodOrder = ['Happy', 'Calm', 'Neutral', 'Anxious', 'Stressed', 'Sad'];
    const sortedMoods = moodOrder.filter(mood => mood in moodColors);
    
    // creating a grid-like layout for the legend items, 3 columns for larger screens
    sortedMoods.forEach(mood => {
        const color = moodColors[mood];
        const li = document.createElement('li');
        
        const colorBox = document.createElement('span');
        colorBox.style.backgroundColor = color;
        colorBox.style.boxShadow = '0 1px 3px rgba(0,0,0,0.12)';
        
        const text = document.createElement('span');
        text.textContent = mood;
        
        li.appendChild(colorBox);
        li.appendChild(text);
        ul.appendChild(li);
    });
    
    legendContainer.appendChild(ul);
}
