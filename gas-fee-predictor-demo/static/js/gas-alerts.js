/**
 * Gas Fee Alerts Functionality
 * For Ethereum Gas Fee Predictor
 */

$(document).ready(function() {
    // Initialize alerts system
    initializeAlerts();

    // Set up event listeners
    setupEventListeners();

    // Load current gas fee data for alerts tab
    loadGasDataForAlerts();
});

// Initialize alerts system
function initializeAlerts() {
    // Load saved alerts from localStorage
    loadSavedAlerts();

    // Check if we need to show the phone number field
    $('#alert-sms').change(function() {
        if ($(this).is(':checked')) {
            $('#phone-container').slideDown();
        } else {
            $('#phone-container').slideUp();
        }
    });
}

// Set up event listeners
function setupEventListeners() {
    // Handle alert form submission
    $('#gas-alert-form').submit(function(e) {
        e.preventDefault();
        saveNewAlert();
    });

    // Handle alert deletion
    $(document).on('click', '.delete-alert', function() {
        const alertId = $(this).data('alert-id');
        deleteAlert(alertId);
    });
}

// Load current gas fee data for alerts tab
function loadGasDataForAlerts() {
    // Fetch current gas fee data
    $.ajax({
        url: '/predict',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.success) {
                // Update current fee display with 4 decimal places
                $('#alert-current-fee').text(data.prediction.current_fee.toFixed(4) + ' GWEI');

                // Update predicted fee display with 4 decimal places
                $('#alert-predicted-fee').text(data.prediction.predicted_fee.toFixed(4) + ' GWEI');

                // Update recommendation
                updateAlertRecommendation(data.prediction);

                // Check active alerts against current gas fee
                checkActiveAlerts(data.prediction.current_fee);
            }
        },
        error: function() {
            $('#alert-recommendation').removeClass('alert-success').addClass('alert-danger')
                .html('<i class="fas fa-exclamation-circle me-2"></i> Failed to load gas fee data. Please try again later.');
        }
    });
}

// Update alert recommendation based on gas fee data
function updateAlertRecommendation(prediction) {
    const currentFee = prediction.current_fee;
    const predictedFee = prediction.predicted_fee;

    let recommendation = '';
    let alertClass = 'alert-info';

    if (predictedFee < currentFee) {
        // Gas fee is predicted to decrease
        const percentDecrease = ((currentFee - predictedFee) / currentFee * 100).toFixed(2);
        recommendation = `
            <i class="fas fa-arrow-down me-2"></i>
            Gas fees are predicted to decrease by ${percentDecrease}% in the next hour.
            Consider waiting before making transactions.
        `;
        alertClass = 'alert-success';
    } else if (predictedFee > currentFee) {
        // Gas fee is predicted to increase
        const percentIncrease = ((predictedFee - currentFee) / currentFee * 100).toFixed(2);
        recommendation = `
            <i class="fas fa-arrow-up me-2"></i>
            Gas fees are predicted to increase by ${percentIncrease}% in the next hour.
            Consider making transactions now.
        `;
        alertClass = 'alert-warning';
    } else {
        // Gas fee is predicted to stay the same
        recommendation = `
            <i class="fas fa-equals me-2"></i>
            Gas fees are predicted to remain stable in the next hour.
        `;
        alertClass = 'alert-info';
    }

    // Update recommendation display
    $('#alert-recommendation').removeClass('alert-success alert-warning alert-info alert-danger')
        .addClass(alertClass)
        .html(recommendation);
}

// Load saved alerts from localStorage
function loadSavedAlerts() {
    // Get saved alerts from localStorage
    const savedAlerts = JSON.parse(localStorage.getItem('gasFeeAlerts')) || [];

    // Update UI based on saved alerts
    if (savedAlerts.length > 0) {
        $('#no-alerts').hide();
        $('#alerts-list').show();

        // Clear existing alerts
        $('#alerts-list .list-group').empty();

        // Add each alert to the list
        savedAlerts.forEach(function(alert) {
            addAlertToList(alert);
        });
    } else {
        $('#no-alerts').show();
        $('#alerts-list').hide();
    }
}

// Save a new alert
function saveNewAlert() {
    // Get form values
    const threshold = parseFloat($('#alert-threshold').val());
    const alertCondition = $('input[name="alert-condition"]:checked').val();
    const email = $('#alert-email').val();
    const smsEnabled = $('#alert-sms').is(':checked');
    const phone = smsEnabled ? $('#alert-phone').val() : '';
    const duration = parseInt($('#alert-duration').val());

    // Validate input
    if (isNaN(threshold) || threshold <= 0) {
        showAlertError('Please enter a valid threshold value greater than 0.');
        return;
    }

    if (!email || !validateEmail(email)) {
        showAlertError('Please enter a valid email address.');
        return;
    }

    if (smsEnabled && !phone) {
        showAlertError('Please enter a phone number for SMS alerts.');
        return;
    }

    // Create alert object
    const alertId = 'alert_' + Date.now();
    const createdAt = new Date();
    const expiresAt = new Date(createdAt.getTime() + duration * 60 * 60 * 1000);

    const newAlert = {
        id: alertId,
        threshold: threshold,
        alertCondition: alertCondition, // 'below' or 'above'
        email: email,
        smsEnabled: smsEnabled,
        phone: phone,
        duration: duration,
        createdAt: createdAt.toISOString(),
        expiresAt: expiresAt.toISOString(),
        triggered: false
    };

    // Get existing alerts
    const savedAlerts = JSON.parse(localStorage.getItem('gasFeeAlerts')) || [];

    // Add new alert
    savedAlerts.push(newAlert);

    // Save to localStorage
    localStorage.setItem('gasFeeAlerts', JSON.stringify(savedAlerts));

    // Update UI
    $('#no-alerts').hide();
    $('#alerts-list').show();
    addAlertToList(newAlert);

    // Reset form
    $('#gas-alert-form')[0].reset();
    $('#phone-container').hide();

    // Show success message
    showAlertSuccess('Alert has been set successfully!');

    // Check if the alert should be triggered immediately
    $.ajax({
        url: '/predict',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.success) {
                checkActiveAlerts(data.prediction.current_fee);
            }
        }
    });
}

// Add an alert to the list in the UI
function addAlertToList(alert) {
    const expiresDate = new Date(alert.expiresAt);
    const now = new Date();

    // Check if alert has expired
    if (expiresDate < now) {
        // Remove expired alert
        deleteAlert(alert.id);
        return;
    }

    // Format expiration time
    const expiresFormatted = formatDateTime(expiresDate);

    // Create alert item
    const alertItem = $(`
        <div class="list-group-item list-group-item-action ${alert.triggered ? 'list-group-item-success' : ''}" id="${alert.id}">
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">
                    ${alert.alertCondition === 'below' ? 'Below' : 'Above'}
                    ${alert.threshold.toFixed(4)} GWEI
                </h5>
                <small class="text-muted">Expires: ${expiresFormatted}</small>
            </div>
            <p class="mb-1">
                <i class="fas fa-envelope me-1"></i> ${alert.email}
                ${alert.smsEnabled ? `<br><i class="fas fa-phone me-1"></i> ${alert.phone}` : ''}
            </p>
            <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">
                    ${alert.triggered ? '<span class="text-success"><i class="fas fa-check-circle me-1"></i> Triggered</span>' : 'Not triggered yet'}
                </small>
                <button class="btn btn-sm btn-danger delete-alert" data-alert-id="${alert.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `);

    // Add to list
    $('#alerts-list .list-group').append(alertItem);
}

// Delete an alert
function deleteAlert(alertId) {
    // Get saved alerts
    let savedAlerts = JSON.parse(localStorage.getItem('gasFeeAlerts')) || [];

    // Filter out the alert to delete
    savedAlerts = savedAlerts.filter(alert => alert.id !== alertId);

    // Save updated alerts
    localStorage.setItem('gasFeeAlerts', JSON.stringify(savedAlerts));

    // Remove from UI
    $(`#${alertId}`).remove();

    // Update UI if no alerts left
    if (savedAlerts.length === 0) {
        $('#no-alerts').show();
        $('#alerts-list').hide();
    }
}

// Check active alerts against current gas fee
function checkActiveAlerts(currentFee) {
    // Get saved alerts
    let savedAlerts = JSON.parse(localStorage.getItem('gasFeeAlerts')) || [];
    let alertsUpdated = false;

    // Check each alert
    savedAlerts.forEach(alert => {
        // Check if alert should be triggered based on condition
        let shouldTrigger = false;

        if (alert.alertCondition === 'below') {
            // Trigger if fee falls below threshold
            shouldTrigger = !alert.triggered && currentFee <= alert.threshold;
        } else {
            // Trigger if fee rises above threshold
            shouldTrigger = !alert.triggered && currentFee >= alert.threshold;
        }

        if (shouldTrigger) {
            // Mark as triggered
            alert.triggered = true;
            alertsUpdated = true;

            // Update UI
            $(`#${alert.id}`).addClass('list-group-item-success');
            $(`#${alert.id} small:first-of-type`).html('<span class="text-success"><i class="fas fa-check-circle me-1"></i> Triggered</span>');

            // Show notification
            showAlertNotification(alert, currentFee);
        }
    });

    // Save updated alerts if any were triggered
    if (alertsUpdated) {
        localStorage.setItem('gasFeeAlerts', JSON.stringify(savedAlerts));
    }
}

// Show alert notification
function showAlertNotification(alert, currentFee) {
    // Create notification
    const notification = $(`
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="10000">
            <div class="toast-header bg-success text-white">
                <i class="fas fa-bell me-2"></i>
                <strong class="me-auto">Gas Fee Alert Triggered!</strong>
                <small>Just now</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                Current gas fee (${currentFee.toFixed(4)} GWEI) is
                ${alert.alertCondition === 'below' ? 'below' : 'above'}
                your threshold of ${alert.threshold.toFixed(4)} GWEI.
                <br>
                <small class="text-muted">Alert sent to: ${alert.email}</small>
            </div>
        </div>
    `);

    // Add to container (create if doesn't exist)
    if ($('.toast-container').length === 0) {
        $('body').append('<div class="toast-container position-fixed bottom-0 end-0 p-3"></div>');
    }

    $('.toast-container').append(notification);

    // Show notification
    const toast = new bootstrap.Toast(notification[0]);
    toast.show();

    // Play notification sound
    playNotificationSound();
}

// Play notification sound
function playNotificationSound() {
    // Create audio element
    const audio = new Audio('https://assets.mixkit.co/sfx/preview/mixkit-software-interface-alert-notification-256.mp3');
    audio.volume = 0.5;
    audio.play();
}

// Show alert error message
function showAlertError(message) {
    // Create alert
    const errorAlert = $(`
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);

    // Add to form
    $('#gas-alert-form').prepend(errorAlert);

    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        errorAlert.alert('close');
    }, 5000);
}

// Show alert success message
function showAlertSuccess(message) {
    // Create alert
    const successAlert = $(`
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);

    // Add to form
    $('#gas-alert-form').prepend(successAlert);

    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        successAlert.alert('close');
    }, 5000);
}

// Validate email format
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Format date and time
function formatDateTime(date) {
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
