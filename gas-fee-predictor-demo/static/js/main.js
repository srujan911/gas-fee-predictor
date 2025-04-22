/*
   Ethereum Gas Fee Predictor - Main JavaScript
   Author: SRUJANJAINI
   Date: April 2025
*/

// Wait for the document to be fully loaded
$(document).ready(function() {
    // Initialize the application
    initApp();

    // Set up event listeners
    setupEventListeners();

    // Load initial data
    loadInitialData();
});

// Initialize the application
function initApp() {
    console.log('Ethereum Gas Fee Predictor - Frontend Initialized');

    // Smooth scrolling for navigation links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();

        // If this is a tab link in the app page
        if ($(this).attr('data-bs-toggle') === 'tab') {
            // Let Bootstrap handle the tab switching
            return;
        }

        $('html, body').animate({
            scrollTop: $($(this).attr('href')).offset().top - 70
        }, 500);

        // Update active nav link
        $('.nav-link').removeClass('active');
        $(this).addClass('active');
    });

    // Add animation to elements when they come into view
    if (typeof IntersectionObserver !== 'undefined') {
        const animateOnScroll = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated');
                    entry.target.classList.add(entry.target.dataset.animation || 'animate__fadeIn');
                    animateOnScroll.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('[data-animation]').forEach(element => {
            animateOnScroll.observe(element);
        });
    }

    // Handle tab switching with animations
    $('.nav-link[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const targetId = $(e.target).attr('href');
        $(targetId).find('[data-animation]').each(function() {
            const animationClass = $(this).data('animation');
            $(this).removeClass(animationClass).addClass('animate__animated').addClass(animationClass);
        });
    });
}

// Set up event listeners
function setupEventListeners() {
    // Prediction button
    $('#predict-btn').on('click', function() {
        makePrediction();
    });

    // Generate heatmap button
    $('#generate-heatmap-btn').on('click', function() {
        generateHeatmap();
    });

    // Run heatmap script button
    $('#run-heatmap-script-btn').on('click', function() {
        runHeatmapScript();
    });

    // Calculate transaction costs button
    $('#calculate-costs-btn').on('click', function() {
        calculateTransactionCosts();
    });

    // Pipeline form submission
    $('#pipeline-form').on('submit', function(e) {
        e.preventDefault();
        runPipeline();
    });
}

// Load initial data
function loadInitialData() {
    // Make initial prediction
    makePrediction();

    // Load historical data for charts
    loadHistoricalData();

    // Generate heatmap
    generateHeatmap();

    // Calculate transaction costs
    calculateTransactionCosts();
}

// Make gas fee prediction
function makePrediction() {
    // Show loading state
    $('#current-fee, #predicted-fee').text('...');
    $('#current-block, #current-time').text('Loading...');
    $('#change-value, #change-percent').text('');
    $('#gas-used, #gas-limit, #tx-count, #block-number').text('Loading...');
    $('#predict-btn').prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Predicting...');

    // Make AJAX request to prediction endpoint
    $.ajax({
        url: '/predict',
        type: 'POST',
        contentType: 'application/json',
        success: function(response) {
            if (response.success) {
                updatePredictionUI(response.prediction);
            } else {
                console.error('Prediction failed:', response.error);
                $('#predict-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Update Prediction');
                alert('Prediction failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', error);
            $('#predict-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Update Prediction');
            alert('Error making prediction. Please try again.');
        }
    });
}

// Update prediction UI with new data
function updatePredictionUI(prediction) {
    // Update current fee
    $('#current-fee').text(prediction.current_fee.toFixed(2));
    $('#current-block').text('Block: ' + prediction.block_number);
    $('#current-time').text('Time: ' + prediction.formatted_time);

    // Update predicted fee
    $('#predicted-fee').text(prediction.predicted_fee.toFixed(2));

    // Update change indicators
    const changeValue = prediction.difference.toFixed(2);
    const changePercent = prediction.percent_change.toFixed(2);

    if (prediction.difference > 0) {
        $('#change-value').html(`<i class="fas fa-arrow-up"></i> +${changeValue} GWEI`).addClass('increase').removeClass('decrease');
        $('#change-percent').html(`(+${changePercent}%)`).addClass('increase').removeClass('decrease');
        $('#current-trend').html('Gas fees are <strong>increasing</strong>. The predicted fee is higher than the current fee.');
        $('#transaction-recommendation').html('Consider executing urgent transactions now before fees increase further.');
    } else if (prediction.difference < 0) {
        $('#change-value').html(`<i class="fas fa-arrow-down"></i> ${changeValue} GWEI`).addClass('decrease').removeClass('increase');
        $('#change-percent').html(`(${changePercent}%)`).addClass('decrease').removeClass('increase');
        $('#current-trend').html('Gas fees are <strong>decreasing</strong>. The predicted fee is lower than the current fee.');
        $('#transaction-recommendation').html('Consider delaying non-urgent transactions to benefit from lower fees.');
    } else {
        $('#change-value').html(`<i class="fas fa-equals"></i> ${changeValue} GWEI`).removeClass('increase decrease');
        $('#change-percent').html(`(${changePercent}%)`).removeClass('increase decrease');
        $('#current-trend').html('Gas fees are <strong>stable</strong>. The predicted fee is equal to the current fee.');
        $('#transaction-recommendation').html('Current conditions are suitable for most transactions.');
    }

    // Update block stats
    $('#gas-used').text(prediction.gas_used.toLocaleString());
    $('#gas-limit').text(prediction.gas_limit.toLocaleString());
    $('#tx-count').text(prediction.tx_count);
    $('#block-number').text(prediction.block_number);

    // Update gas usage progress bar
    const gasUsagePercent = (prediction.gas_used / prediction.gas_limit) * 100;
    $('#gas-used-progress').css('width', gasUsagePercent + '%');

    if (gasUsagePercent > 80) {
        $('#gas-used-progress').removeClass('bg-info bg-warning').addClass('bg-danger');
    } else if (gasUsagePercent > 50) {
        $('#gas-used-progress').removeClass('bg-info bg-danger').addClass('bg-warning');
    } else {
        $('#gas-used-progress').removeClass('bg-warning bg-danger').addClass('bg-info');
    }

    // Re-enable prediction button
    $('#predict-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Update Prediction');
}

// Load historical data for charts
function loadHistoricalData() {
    $.ajax({
        url: '/historical-data',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                createGasFeeChart(response.chart_data);
                createHourlyPatternChart(response.hourly_data);
            } else {
                console.error('Failed to load historical data:', response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', error);
        }
    });
}

// Create gas fee chart
function createGasFeeChart(data) {
    const trace1 = {
        x: data.timestamps,
        y: data.base_fees,
        type: 'scatter',
        mode: 'lines',
        name: 'Actual Gas Fee',
        line: {
            color: 'rgb(49, 130, 189)',
            width: 2
        }
    };

    const traces = [trace1];

    // Add predictions if available
    if (data.predicted_fees) {
        const trace2 = {
            x: data.timestamps,
            y: data.predicted_fees,
            type: 'scatter',
            mode: 'lines',
            name: 'Predicted Gas Fee',
            line: {
                color: 'rgb(204, 0, 0)',
                width: 2,
                dash: 'dash'
            }
        };

        traces.push(trace2);
    }

    const layout = {
        title: 'Gas Fee History',
        xaxis: {
            title: 'Time',
            showgrid: false
        },
        yaxis: {
            title: 'Gas Fee (GWEI)',
            showgrid: true,
            gridcolor: 'rgba(0,0,0,0.1)'
        },
        margin: {
            l: 50,
            r: 20,
            t: 50,
            b: 80
        },
        legend: {
            orientation: 'h',
            y: -0.2
        },
        hovermode: 'closest',
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('gas-fee-chart', traces, layout, {responsive: true});

    // Create prediction accuracy chart if predictions are available
    if (data.predicted_fees) {
        createPredictionAccuracyChart(data);
    }
}

// Create hourly pattern chart
function createHourlyPatternChart(data) {
    const trace = {
        x: data.hours,
        y: data.avg_fees,
        type: 'bar',
        marker: {
            color: data.avg_fees.map(function(fee) {
                // Color gradient based on fee value
                const normalizedFee = (fee - Math.min(...data.avg_fees)) /
                                     (Math.max(...data.avg_fees) - Math.min(...data.avg_fees));
                return `rgba(${Math.round(255 * normalizedFee)}, ${Math.round(255 * (1 - normalizedFee))}, 0, 0.7)`;
            })
        }
    };

    const layout = {
        title: 'Average Gas Fee by Hour of Day (IST)',
        xaxis: {
            title: 'Hour (IST)',
            tickmode: 'linear',
            tick0: 0,
            dtick: 2
        },
        yaxis: {
            title: 'Average Gas Fee (GWEI)'
        },
        margin: {
            l: 50,
            r: 20,
            t: 50,
            b: 50
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('hourly-pattern-chart', [trace], layout, {responsive: true});

    // Find best and worst hours
    const bestHour = data.hours[data.avg_fees.indexOf(Math.min(...data.avg_fees))];
    const worstHour = data.hours[data.avg_fees.indexOf(Math.max(...data.avg_fees))];

    // Update optimal time recommendation
    $('#optimal-time').html(`Based on historical data, the best time to transact is around <strong>${bestHour}:00 IST</strong>, while the worst time is around <strong>${worstHour}:00 IST</strong>.`);
}

// Create prediction accuracy chart
function createPredictionAccuracyChart(data) {
    // Calculate prediction errors
    const errors = [];
    for (let i = 0; i < data.base_fees.length; i++) {
        if (data.predicted_fees[i]) {
            errors.push(data.predicted_fees[i] - data.base_fees[i]);
        }
    }

    const trace = {
        x: errors,
        type: 'histogram',
        marker: {
            color: 'rgba(100, 149, 237, 0.7)',
            line: {
                color: 'rgba(100, 149, 237, 1)',
                width: 1
            }
        },
        nbinsx: 20
    };

    const layout = {
        title: 'Prediction Error Distribution',
        xaxis: {
            title: 'Prediction Error (GWEI)'
        },
        yaxis: {
            title: 'Frequency'
        },
        margin: {
            l: 50,
            r: 20,
            t: 50,
            b: 50
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('prediction-accuracy-chart', [trace], layout, {responsive: true});
}

// Run heatmap script directly
function runHeatmapScript() {
    // Show loading state
    $('#heatmap-image').addClass('d-none');
    $('#heatmap-loading').removeClass('d-none');
    $('#run-heatmap-script-btn').prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running Script...');
    $('#best-time, #worst-time').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');
    $('#optimal-times').html('<li class="list-group-item"><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...</li>');

    // Make AJAX request to run the script
    $.ajax({
        url: '/run-heatmap-script',
        type: 'POST',
        success: function(response) {
            if (response.success) {
                alert('Heatmap script executed successfully! Refreshing data...');
                // Now get the updated heatmap data
                generateHeatmap();
            } else {
                console.error('Heatmap script execution failed:', response.error);
                $('#run-heatmap-script-btn').prop('disabled', false).html('<i class="fas fa-code me-2"></i> Run Heatmap Script');
                alert('Heatmap script execution failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', error);
            $('#run-heatmap-script-btn').prop('disabled', false).html('<i class="fas fa-code me-2"></i> Run Heatmap Script');
            alert('Error executing heatmap script. Please try again.');
        },
        complete: function() {
            $('#run-heatmap-script-btn').prop('disabled', false).html('<i class="fas fa-code me-2"></i> Run Heatmap Script');
        }
    });
}

// Generate gas fee heatmap
function generateHeatmap() {
    // Show loading state
    $('#heatmap-image').addClass('d-none');
    $('#heatmap-loading').removeClass('d-none');
    $('#generate-heatmap-btn').prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...');
    $('#best-time, #worst-time').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');
    $('#optimal-times').html('<li class="list-group-item"><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...</li>');

    // Make AJAX request to heatmap endpoint
    $.ajax({
        url: '/heatmap',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                updateHeatmapUI(response);
            } else {
                console.error('Heatmap generation failed:', response.error);
                $('#generate-heatmap-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Generate Heatmap');
                alert('Heatmap generation failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', error);
            $('#generate-heatmap-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Generate Heatmap');
            alert('Error generating heatmap. Please try again.');
        }
    });
}

// Update heatmap UI with new data
function updateHeatmapUI(data) {
    // Update heatmap image
    const imgPath = data.heatmap_path + '?t=' + new Date().getTime();
    console.log('Loading heatmap from:', imgPath);

    // Create a new Image object to check if the image loads correctly
    const img = new Image();
    img.onload = function() {
        console.log('Heatmap image loaded successfully');
        $('#heatmap-image').attr('src', imgPath).removeClass('d-none');
        $('#heatmap-loading').addClass('d-none');
    };
    img.onerror = function() {
        console.error('Failed to load heatmap image');
        $('#heatmap-loading').addClass('d-none');
        $('#heatmap-image').addClass('d-none');
        alert('Failed to generate heatmap. Please check if you have enough data collected.');
    };
    img.src = imgPath;

    // Update best time
    $('#best-time').html(`
        <strong>Day:</strong> ${data.best_time.day}<br>
        <strong>Hour:</strong> ${data.best_time.hour}:00 IST<br>
        <strong>Average Fee:</strong> ${data.best_time.average_fee.toFixed(2)} GWEI
    `);

    // Update worst time
    $('#worst-time').html(`
        <strong>Day:</strong> ${data.worst_time.day}<br>
        <strong>Hour:</strong> ${data.worst_time.hour}:00 IST<br>
        <strong>Average Fee:</strong> ${data.worst_time.average_fee.toFixed(2)} GWEI
    `);

    // Update optimal times
    let optimalTimesHtml = '';
    if (data.optimal_times && data.optimal_times.length > 0) {
        data.optimal_times.forEach(function(time, index) {
            optimalTimesHtml += `
                <li class="list-group-item">
                    <strong>${index + 1}.</strong> ${time.day_of_week} at ${time.hour}:00 IST
                    <span class="badge bg-success float-end">${time.mean.toFixed(2)} GWEI</span>
                </li>
            `;
        });
    } else {
        optimalTimesHtml = '<li class="list-group-item">No optimal times found</li>';
    }
    $('#optimal-times').html(optimalTimesHtml);

    // Re-enable heatmap button
    $('#generate-heatmap-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Generate Heatmap');
}

// Calculate transaction costs
function calculateTransactionCosts() {
    // Show loading state
    $('#calculate-costs-btn').prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calculating...');
    $('#cost-comparison-table').html('<tr><td colspan="7" class="text-center"><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading transaction cost data...</td></tr>');

    // Make AJAX request to transaction costs endpoint
    $.ajax({
        url: '/transaction-costs',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                updateTransactionCostsUI(response);
            } else {
                console.error('Transaction cost calculation failed:', response.error);
                $('#calculate-costs-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Update Transaction Costs');
                alert('Transaction cost calculation failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', error);
            $('#calculate-costs-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Update Transaction Costs');
            alert('Error calculating transaction costs. Please try again.');
        }
    });
}

// Update transaction costs UI with new data
function updateTransactionCostsUI(data) {
    // Create current costs chart
    createTransactionCostsChart('current-costs-chart', data.current_costs, data.current_fee, data.eth_price, 'Current');

    // Create predicted costs chart
    createTransactionCostsChart('predicted-costs-chart', data.predicted_costs, data.predicted_fee, data.eth_price, 'Predicted');

    // Update cost comparison table
    let tableHtml = '';
    data.current_costs.forEach(function(currentCost, index) {
        const predictedCost = data.predicted_costs[index];
        const savingsEth = currentCost.cost_in_eth - predictedCost.cost_in_eth;
        const savingsUsd = currentCost.cost_in_usd - predictedCost.cost_in_usd;
        const savingsPercent = (savingsEth / currentCost.cost_in_eth) * 100;

        let savingsClass = '';
        let savingsIcon = '';

        if (savingsEth > 0) {
            savingsClass = 'text-success';
            savingsIcon = '<i class="fas fa-arrow-down"></i>';
        } else if (savingsEth < 0) {
            savingsClass = 'text-danger';
            savingsIcon = '<i class="fas fa-arrow-up"></i>';
        }

        tableHtml += `
            <tr>
                <td>${currentCost.transaction_type}</td>
                <td>${currentCost.gas_used.toLocaleString()}</td>
                <td>${currentCost.cost_in_eth.toFixed(6)}</td>
                <td>$${currentCost.cost_in_usd.toFixed(2)}</td>
                <td>${predictedCost.cost_in_eth.toFixed(6)}</td>
                <td>$${predictedCost.cost_in_usd.toFixed(2)}</td>
                <td class="${savingsClass}">
                    ${savingsIcon} ${Math.abs(savingsEth).toFixed(6)} ETH
                    <small>(${Math.abs(savingsPercent).toFixed(2)}%)</small>
                </td>
            </tr>
        `;
    });

    $('#cost-comparison-table').html(tableHtml);

    // Re-enable calculate costs button
    $('#calculate-costs-btn').prop('disabled', false).html('<i class="fas fa-sync-alt me-2"></i> Update Transaction Costs');
}

// Create transaction costs chart
function createTransactionCostsChart(elementId, costsData, gasFee, ethPrice, title) {
    // Filter to top 5 transaction types for clarity
    const topCosts = costsData.slice(0, 5);

    const trace = {
        x: topCosts.map(cost => cost.transaction_type),
        y: topCosts.map(cost => cost.cost_in_usd),
        type: 'bar',
        marker: {
            color: 'rgba(50, 171, 96, 0.7)',
            line: {
                color: 'rgba(50, 171, 96, 1)',
                width: 1
            }
        },
        text: topCosts.map(cost => `${cost.cost_in_eth.toFixed(6)} ETH`),
        textposition: 'auto'
    };

    const layout = {
        title: `${title} Transaction Costs (Gas Fee: ${gasFee.toFixed(2)} GWEI, ETH: $${ethPrice.toFixed(2)})`,
        xaxis: {
            title: 'Transaction Type'
        },
        yaxis: {
            title: 'Cost (USD)'
        },
        margin: {
            l: 50,
            r: 20,
            t: 50,
            b: 100
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot(elementId, [trace], layout, {responsive: true});
}

// Run prediction pipeline
function runPipeline() {
    // Get form values
    const numBlocks = $('#num-blocks').val();
    const useImproved = $('#use-improved').is(':checked');
    const timezone = $('#timezone').val();

    // Show loading state
    $('#pipeline-form button[type="submit"]').prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...');
    $('#pipeline-status').removeClass('alert-info alert-success alert-danger').addClass('alert-warning').html('Pipeline running...');
    $('#pipeline-progress').css('width', '0%').text('0%');
    $('#pipeline-log').html('<p>Starting pipeline...</p>');

    // Make AJAX request to run pipeline
    $.ajax({
        url: '/run-pipeline',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            num_blocks: parseInt(numBlocks),
            use_improved: useImproved,
            timezone: timezone
        }),
        success: function(response) {
            if (response.success) {
                updatePipelineUI(true, response.message);

                // Reload data after pipeline completes
                loadInitialData();
            } else {
                updatePipelineUI(false, response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', error);
            updatePipelineUI(false, 'Error running pipeline. Please try again.');
        }
    });

    // Simulate pipeline progress (since we don't have real-time updates)
    simulatePipelineProgress();
}

// Update pipeline UI
function updatePipelineUI(success, message) {
    // Re-enable form button
    $('#pipeline-form button[type="submit"]').prop('disabled', false).html('<i class="fas fa-play me-2"></i> Run Full Pipeline');

    // Update status
    if (success) {
        $('#pipeline-status').removeClass('alert-info alert-warning alert-danger').addClass('alert-success').html(message);
        $('#pipeline-progress').css('width', '100%').text('100%');
        $('#pipeline-log').append('<p class="text-success">Pipeline completed successfully!</p>');
    } else {
        $('#pipeline-status').removeClass('alert-info alert-warning alert-success').addClass('alert-danger').html(message);
        $('#pipeline-log').append(`<p class="text-danger">Pipeline failed: ${message}</p>`);
    }
}

// Simulate pipeline progress
function simulatePipelineProgress() {
    const steps = [
        { percent: 10, message: 'Collecting gas fee data...' },
        { percent: 30, message: 'Cleaning data...' },
        { percent: 50, message: 'Training model...' },
        { percent: 70, message: 'Making predictions...' },
        { percent: 90, message: 'Generating visualizations...' }
    ];

    let currentStep = 0;

    const interval = setInterval(function() {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            $('#pipeline-progress').css('width', step.percent + '%').text(step.percent + '%');
            $('#pipeline-log').append(`<p>${step.message}</p>`);
            $('#pipeline-log').scrollTop($('#pipeline-log')[0].scrollHeight);
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 1500);
}
