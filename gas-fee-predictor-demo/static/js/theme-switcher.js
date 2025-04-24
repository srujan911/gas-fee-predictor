// Theme Switcher and Enhanced Visualizations for Ethereum Gas Fee Predictor

// Theme management
class ThemeManager {
    constructor() {
        this.currentTheme = 'default';
        this.themes = ['default', 'ethereum', 'crypto', 'dark', 'neon'];
        this.init();
    }

    init() {
        // Create theme switcher UI
        this.createThemeSwitcher();
        
        // Check for saved theme
        const savedTheme = localStorage.getItem('gasFeePredictor.theme');
        if (savedTheme && this.themes.includes(savedTheme)) {
            this.setTheme(savedTheme);
        }
        
        // Add event listeners
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', () => {
                const theme = option.getAttribute('data-theme');
                this.setTheme(theme);
            });
        });
    }

    createThemeSwitcher() {
        const themeSwitcher = document.createElement('div');
        themeSwitcher.className = 'theme-switcher';
        
        this.themes.forEach(theme => {
            const themeOption = document.createElement('div');
            themeOption.className = `theme-option theme-option-${theme}`;
            themeOption.setAttribute('data-theme', theme);
            themeOption.title = `${theme.charAt(0).toUpperCase() + theme.slice(1)} Theme`;
            
            if (theme === this.currentTheme) {
                themeOption.classList.add('active');
            }
            
            themeSwitcher.appendChild(themeOption);
        });
        
        document.body.appendChild(themeSwitcher);
    }

    setTheme(theme) {
        // Remove all theme classes
        document.body.classList.remove(...this.themes.map(t => `theme-${t}`));
        
        // Add new theme class if not default
        if (theme !== 'default') {
            document.body.classList.add(`theme-${theme}`);
        }
        
        // Update active state in switcher
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.getAttribute('data-theme') === theme) {
                option.classList.add('active');
            }
        });
        
        // Save theme preference
        localStorage.setItem('gasFeePredictor.theme', theme);
        this.currentTheme = theme;
        
        // Update chart colors
        this.updateChartColors();
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
    }
    
    updateChartColors() {
        // Get theme colors
        const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
        const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue('--secondary-color').trim();
        const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
        const infoColor = getComputedStyle(document.documentElement).getPropertyValue('--info-color').trim();
        
        // Update all Chart.js instances
        Chart.instances.forEach(chart => {
            // Update dataset colors
            if (chart.config.type === 'line') {
                if (chart.data.datasets.length > 0) {
                    chart.data.datasets[0].borderColor = primaryColor;
                    chart.data.datasets[0].pointBackgroundColor = primaryColor;
                }
                if (chart.data.datasets.length > 1) {
                    chart.data.datasets[1].borderColor = secondaryColor;
                    chart.data.datasets[1].pointBackgroundColor = secondaryColor;
                }
            } else if (chart.config.type === 'bar') {
                chart.data.datasets.forEach((dataset, i) => {
                    const colors = [primaryColor, secondaryColor, accentColor, infoColor];
                    dataset.backgroundColor = colors[i % colors.length];
                });
            } else if (chart.config.type === 'doughnut' || chart.config.type === 'pie') {
                // Create a gradient of colors based on theme
                const colors = [primaryColor, secondaryColor, accentColor, infoColor];
                chart.data.datasets[0].backgroundColor = colors;
            }
            
            // Update and render
            chart.update();
        });
    }
}

// Enhanced visualizations
class VisualizationEnhancer {
    constructor() {
        this.init();
    }
    
    init() {
        // Add Ethereum logo to header
        this.addEthereumLogo();
        
        // Add refresh button
        this.addRefreshButton();
        
        // Add horizontal scroll to charts
        this.wrapChartsForScroll();
        
        // Add tooltips
        this.addTooltips();
        
        // Add trend indicators
        this.addTrendIndicators();
        
        // Add gradient cards
        this.enhanceCards();
        
        // Add value displays
        this.enhanceValueDisplays();
    }
    
    addEthereumLogo() {
        const heading = document.querySelector('h1');
        if (heading) {
            const logo = document.createElement('img');
            logo.src = 'https://ethereum.org/static/a110735dade3f354a46fc2446cd52476/f3a29/eth-home-icon.webp';
            logo.alt = 'Ethereum Logo';
            logo.className = 'eth-logo';
            heading.prepend(logo);
        }
    }
    
    addRefreshButton() {
        const container = document.querySelector('.container');
        if (container) {
            const refreshBtn = document.createElement('button');
            refreshBtn.className = 'btn btn-sm btn-light position-absolute top-0 end-0 mt-3 me-3';
            refreshBtn.innerHTML = '<i class="refresh-icon">↻</i> Refresh';
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
            container.style.position = 'relative';
            container.appendChild(refreshBtn);
        }
    }
    
    refreshData() {
        // Add refreshing class to icon
        const refreshIcon = document.querySelector('.refresh-icon');
        if (refreshIcon) {
            refreshIcon.classList.add('refreshing');
        }
        
        // Reload all data
        Promise.all([
            fetch('/predict').then(res => res.json()),
            fetch('/gas-fee-history').then(res => res.json()),
            fetch('/heatmap').then(res => res.json()),
            fetch('/transaction-costs').then(res => res.json())
        ]).then(([predictData, historyData, heatmapData, costsData]) => {
            // Update UI with new data
            if (predictData.success) {
                document.getElementById('currentGasFee').textContent = 
                    predictData.prediction.current_fee.toFixed(2) + ' GWEI';
                document.getElementById('predictedGasFee').textContent = 
                    predictData.prediction.predicted_fee.toFixed(2) + ' GWEI';
            }
            
            // Update other data as needed
            
            // Remove refreshing class
            if (refreshIcon) {
                refreshIcon.classList.remove('refreshing');
            }
            
            // Show success message
            this.showToast('Data refreshed successfully!');
        }).catch(error => {
            console.error('Error refreshing data:', error);
            // Remove refreshing class
            if (refreshIcon) {
                refreshIcon.classList.remove('refreshing');
            }
            
            // Show error message
            this.showToast('Error refreshing data. Please try again.', 'error');
        });
    }
    
    wrapChartsForScroll() {
        const chartCanvases = document.querySelectorAll('canvas');
        chartCanvases.forEach(canvas => {
            const parent = canvas.parentElement;
            if (!parent.classList.contains('chart-scroll-container')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'chart-scroll-container';
                parent.insertBefore(wrapper, canvas);
                wrapper.appendChild(canvas);
            }
        });
    }
    
    addTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            const tooltipText = element.getAttribute('data-tooltip');
            element.classList.add('custom-tooltip');
            
            const tooltip = document.createElement('span');
            tooltip.className = 'tooltip-text';
            tooltip.textContent = tooltipText;
            
            element.appendChild(tooltip);
        });
    }
    
    addTrendIndicators() {
        // Add trend indicators to predicted gas fee
        const predictedFee = document.getElementById('predictedGasFee');
        const currentFee = document.getElementById('currentGasFee');
        
        if (predictedFee && currentFee) {
            const predictedValue = parseFloat(predictedFee.textContent);
            const currentValue = parseFloat(currentFee.textContent);
            
            if (predictedValue > currentValue) {
                predictedFee.classList.add('trend-up');
            } else if (predictedValue < currentValue) {
                predictedFee.classList.add('trend-down');
            }
        }
    }
    
    enhanceCards() {
        // Add gradient backgrounds to some cards
        const cards = document.querySelectorAll('.card');
        if (cards.length >= 2) {
            cards[0].classList.add('card-gradient-primary', 'text-white');
            cards[1].classList.add('card-gradient-secondary', 'text-white');
        }
        
        // Add glow effect to important cards
        document.querySelectorAll('.card-body h5').forEach(title => {
            if (title.textContent.includes('Current Gas Fee') || 
                title.textContent.includes('Predicted Gas Fee')) {
                title.closest('.card').classList.add('glow-primary');
            }
        });
    }
    
    enhanceValueDisplays() {
        // Convert simple text values to enhanced displays
        const feeElements = document.querySelectorAll('#currentGasFee, #predictedGasFee');
        feeElements.forEach(element => {
            const value = element.textContent;
            if (value && !element.classList.contains('value-display')) {
                element.innerHTML = '';
                
                const valueDisplay = document.createElement('div');
                valueDisplay.className = 'value-display';
                
                // Extract numeric value and unit
                const match = value.match(/^([\d.]+)\s*(.*)$/);
                if (match) {
                    const numericValue = match[1];
                    const unit = match[2];
                    
                    valueDisplay.innerHTML = `${numericValue}<span class="value-unit">${unit}</span>`;
                    element.appendChild(valueDisplay);
                } else {
                    valueDisplay.textContent = value;
                    element.appendChild(valueDisplay);
                }
            }
        });
    }
    
    showToast(message, type = 'success') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast ${type === 'error' ? 'bg-danger' : 'bg-success'} text-white`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="toast-header ${type === 'error' ? 'bg-danger' : 'bg-success'} text-white">
                <strong class="me-auto">${type === 'error' ? 'Error' : 'Success'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme manager
    window.themeManager = new ThemeManager();
    
    // Initialize visualization enhancer
    window.visualEnhancer = new VisualizationEnhancer();
    
    // Add event listener for tab changes to update charts
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', event => {
            // Trigger resize event to fix chart rendering issues
            window.dispatchEvent(new Event('resize'));
            
            // Update any visible charts
            Chart.instances.forEach(chart => {
                chart.update();
            });
        });
    });
});
