/**
 * Dark Mode Toggle for Ethereum Gas Fee Predictor
 * Author: SRUJAN.J
 * Date: April 2025
 */

// Wait for the document to be fully loaded
$(document).ready(function() {
    // Check for saved theme preference (default to light mode)
    checkDarkModePreference();

    // Set up event listener for dark mode toggle
    $('#dark-mode-toggle').on('click', function() {
        if ($('body').hasClass('dark-mode')) {
            disableDarkMode();
        } else {
            enableDarkMode();
        }
    });
});

// Check for saved theme preference
function checkDarkModePreference() {
    // Check if dark mode is saved in localStorage
    const darkModeSaved = localStorage.getItem('darkMode');

    if (darkModeSaved === 'enabled') {
        enableDarkMode();
    } else {
        // Default to light mode
        disableDarkMode();
    }
}

// Enable dark mode
function enableDarkMode() {
    // Add dark mode class to body
    $('body').addClass('dark-mode');

    // Update toggle button icon
    $('#dark-mode-toggle i').removeClass('fa-moon').addClass('fa-sun');

    // Save preference to localStorage
    localStorage.setItem('darkMode', 'enabled');

    // Update charts for dark mode
    updateChartsForDarkMode();
}

// Disable dark mode
function disableDarkMode() {
    // Remove dark mode class from body
    $('body').removeClass('dark-mode');

    // Update toggle button icon
    $('#dark-mode-toggle i').removeClass('fa-sun').addClass('fa-moon');

    // Save preference to localStorage
    localStorage.setItem('darkMode', 'disabled');

    // Update charts for light mode
    updateChartsForLightMode();
}

// Note: We've removed the reloadGasFeeChart function to simplify the dark mode toggle
// and avoid issues with data loading. We're now using CSS to change chart colors instead.

// Update charts for dark mode
function updateChartsForDarkMode() {
    // Update Plotly charts if they exist
    if (typeof Plotly !== 'undefined') {
        const chartIds = [
            'gas-fee-chart',
            'hourly-pattern-chart',
            'prediction-accuracy-chart',
            'current-costs-chart',
            'predicted-costs-chart'
        ];

        chartIds.forEach(chartId => {
            const chart = document.getElementById(chartId);
            if (chart) {
                try {
                    // Common layout updates for dark mode
                    let darkModeLayout = {
                        paper_bgcolor: '#1e1e1e',
                        plot_bgcolor: '#1e1e1e',
                        font: { color: '#e0e0e0' },
                        'xaxis.gridcolor': '#333',
                        'yaxis.gridcolor': '#333',
                        'xaxis.linecolor': '#555',
                        'yaxis.linecolor': '#555',
                        'xaxis.title.font.color': '#e0e0e0',
                        'yaxis.title.font.color': '#e0e0e0',
                        'legend.font.color': '#e0e0e0',
                        'title.font.color': '#e0e0e0'
                    };

                    // Special handling for gas fee chart
                    if (chartId === 'gas-fee-chart') {
                        darkModeLayout = {
                            ...darkModeLayout,
                            paper_bgcolor: '#121212',
                            plot_bgcolor: '#121212',
                            font: { color: '#FFFFFF' },
                            'xaxis.gridcolor': '#333',
                            'yaxis.gridcolor': '#333',
                            'xaxis.linecolor': '#FFFFFF',
                            'yaxis.linecolor': '#FFFFFF',
                            'xaxis.title.font.color': '#FFFFFF',
                            'yaxis.title.font.color': '#FFFFFF',
                            'legend.font.color': '#FFFFFF',
                            'title.font.color': '#FFFFFF'
                        };
                    };

                    // Apply layout changes
                    Plotly.relayout(chartId, darkModeLayout);

                    // Get the current data traces
                    const plotData = Plotly.d3.select(`#${chartId}`).data()[0].data;

                    // Update trace colors for better visibility in dark mode
                    if (plotData) {
                        const updatedData = plotData.map((trace, i) => {
                            const update = {};

                            // For bar charts, increase brightness
                            if (trace.type === 'bar') {
                                // If the trace already has custom colors, adjust them
                                if (trace.marker && trace.marker.color) {
                                    if (Array.isArray(trace.marker.color)) {
                                        // For color arrays (like in hourly pattern chart)
                                        update.marker = {
                                            color: trace.marker.color.map(color => {
                                                // Make colors brighter for dark mode
                                                if (typeof color === 'string' && color.includes('rgba')) {
                                                    return color.replace('rgba(', 'rgba(').replace(')', ')').replace(/[\d.]+\)$/, '0.9)');
                                                }
                                                return color;
                                            }),
                                            line: { color: '#555', width: 1 }
                                        };
                                    } else {
                                        // For single colors
                                        update.marker = {
                                            color: trace.marker.color,
                                            opacity: 0.9,
                                            line: { color: '#555', width: 1 }
                                        };
                                    }
                                } else {
                                    // Default color enhancement for bars
                                    update.marker = {
                                        color: `rgba(${100 + i * 50}, ${150 + i * 20}, 255, 0.8)`,
                                        line: { color: '#555', width: 1 }
                                    };
                                }
                            }

                            // For line charts, make lines brighter
                            if (trace.type === 'scatter' && trace.mode && trace.mode.includes('lines')) {
                                // Special handling for gas fee history chart - make it white in dark mode
                                if (chartId === 'gas-fee-chart') {
                                    update.line = {
                                        color: '#FFFFFF', // Pure white color for dark mode
                                        width: 4
                                    };
                                    // Also make markers white with a contrasting border
                                    update.marker = {
                                        color: '#FFFFFF',
                                        size: 6,
                                        line: {
                                            color: '#333333',
                                            width: 1
                                        }
                                    };
                                } else {
                                    update.line = {
                                        color: trace.line ? trace.line.color || '#bb86fc' : '#bb86fc',
                                        width: trace.line ? trace.line.width || 3 : 3
                                    };
                                }
                            }

                            // For histogram, make it more visible
                            if (trace.type === 'histogram') {
                                update.marker = {
                                    color: 'rgba(187, 134, 252, 0.7)',
                                    line: { color: '#bb86fc', width: 1 }
                                };
                            }

                            // Update text color for all traces
                            if (trace.textfont) {
                                update.textfont = { color: '#e0e0e0' };
                            }

                            return update;
                        });

                        // Apply data updates
                        Plotly.restyle(chartId, updatedData);
                    }

                } catch (e) {
                    console.log('Error updating chart for dark mode:', chartId, e);
                }
            }
        });
    }

    // Update any other chart types or visualizations here

    // Force redraw of all charts
    window.dispatchEvent(new Event('resize'));
}

// Update charts for light mode
function updateChartsForLightMode() {
    // Update Plotly charts if they exist
    if (typeof Plotly !== 'undefined') {
        const chartIds = [
            'gas-fee-chart',
            'hourly-pattern-chart',
            'prediction-accuracy-chart',
            'current-costs-chart',
            'predicted-costs-chart'
        ];

        chartIds.forEach(chartId => {
            const chart = document.getElementById(chartId);
            if (chart) {
                try {
                    // Common layout updates for light mode
                    const lightModeLayout = {
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#333' },
                        'xaxis.gridcolor': 'rgba(0,0,0,0.1)',
                        'yaxis.gridcolor': 'rgba(0,0,0,0.1)',
                        'xaxis.linecolor': '#333',
                        'yaxis.linecolor': '#333',
                        'xaxis.title.font.color': '#333',
                        'yaxis.title.font.color': '#333',
                        'legend.font.color': '#333',
                        'title.font.color': '#333'
                    };

                    // Apply layout changes
                    Plotly.relayout(chartId, lightModeLayout);

                    // Get the current data traces
                    const plotData = Plotly.d3.select(`#${chartId}`).data()[0].data;

                    // Update trace colors for light mode
                    if (plotData) {
                        const updatedData = plotData.map((trace, i) => {
                            const update = {};

                            // For bar charts
                            if (trace.type === 'bar') {
                                // If the trace already has custom colors, adjust them
                                if (trace.marker && trace.marker.color) {
                                    if (Array.isArray(trace.marker.color)) {
                                        // Keep the original color array but ensure opacity is appropriate
                                        update.marker = {
                                            color: trace.marker.color.map(color => {
                                                if (typeof color === 'string' && color.includes('rgba')) {
                                                    return color.replace(/[\d.]+\)$/, '0.7)');
                                                }
                                                return color;
                                            }),
                                            line: { color: 'rgba(0,0,0,0.3)', width: 1 }
                                        };
                                    } else {
                                        // For single colors
                                        update.marker = {
                                            color: trace.marker.color,
                                            opacity: 0.7,
                                            line: { color: 'rgba(0,0,0,0.3)', width: 1 }
                                        };
                                    }
                                }
                            }

                            // For line charts
                            if (trace.type === 'scatter' && trace.mode && trace.mode.includes('lines')) {
                                update.line = {
                                    color: trace.line ? trace.line.color || 'rgba(0, 123, 255, 1)' : 'rgba(0, 123, 255, 1)',
                                    width: trace.line ? trace.line.width || 2 : 2
                                };
                            }

                            // For histogram
                            if (trace.type === 'histogram') {
                                update.marker = {
                                    color: 'rgba(100, 149, 237, 0.7)',
                                    line: { color: 'rgba(100, 149, 237, 1)', width: 1 }
                                };
                            }

                            // Update text color for all traces
                            if (trace.textfont) {
                                update.textfont = { color: '#333' };
                            }

                            return update;
                        });

                        // Apply data updates
                        Plotly.restyle(chartId, updatedData);
                    }

                } catch (e) {
                    console.log('Error updating chart for light mode:', chartId, e);
                }
            }
        });
    }

    // Update any other chart types or visualizations here

    // Force redraw of all charts
    window.dispatchEvent(new Event('resize'));
}
