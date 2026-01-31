// Global variables
let currentResults = null;
let outcomeChart = null;

// Initialize page on load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDefaults();
    setupEventListeners();
    checkForCustomStrategy();
});

// Load default parameters from API
async function loadDefaults() {
    try {
        const response = await fetch('/api/defaults');
        const defaults = await response.json();

        // Populate form with defaults
        document.getElementById('dealer_hits_soft_17').checked = defaults.game_rules.dealer_hits_soft_17;
        document.getElementById('surrender_allowed').checked = defaults.game_rules.surrender_allowed;
        document.getElementById('double_after_split').checked = defaults.game_rules.double_after_split;
        document.getElementById('blackjack_payout').value = defaults.game_rules.blackjack_payout;
        updatePayoutLabel(defaults.game_rules.blackjack_payout);

        document.getElementById('num_decks').value = defaults.shoe.num_decks;
        document.getElementById('num-decks-value').textContent = defaults.shoe.num_decks;
        document.getElementById('penetration').value = defaults.shoe.penetration;
        document.getElementById('penetration-value').textContent = `${Math.round(defaults.shoe.penetration * 100)}%`;
        document.getElementById('infinite_shoe').checked = defaults.shoe.infinite_shoe;

        document.getElementById('total_hands').value = defaults.simulation.total_hands;
        document.getElementById('num_sessions').value = defaults.simulation.num_sessions;

        // Populate strategy dropdown
        const strategySelect = document.getElementById('strategy');
        strategySelect.innerHTML = '';

        defaults.available_strategies.forEach(strat => {
            const option = document.createElement('option');
            option.value = strat.id;
            option.textContent = strat.name;
            strategySelect.appendChild(option);
        });

        // Add custom strategy option if available
        if (localStorage.getItem('customStrategy')) {
            const option = document.createElement('option');
            option.value = 'custom';
            option.textContent = 'Custom Strategy (User-Defined)';
            strategySelect.appendChild(option);
        }

    } catch (error) {
        console.error('Error loading defaults:', error);
        showError('Failed to load default parameters');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('simulation-form').addEventListener('submit', handleSubmit);

    // Slider updates
    document.getElementById('num_decks').addEventListener('input', (e) => {
        document.getElementById('num-decks-value').textContent = e.target.value;
    });

    document.getElementById('penetration').addEventListener('input', (e) => {
        document.getElementById('penetration-value').textContent = `${Math.round(e.target.value * 100)}%`;
    });

    // Payout label update
    document.getElementById('blackjack_payout').addEventListener('input', (e) => {
        updatePayoutLabel(parseFloat(e.target.value));
    });

    // Infinite shoe checkbox
    document.getElementById('infinite_shoe').addEventListener('change', (e) => {
        const penetrationInput = document.getElementById('penetration');
        penetrationInput.disabled = e.target.checked;
        if (e.target.checked) {
            penetrationInput.style.opacity = '0.5';
        } else {
            penetrationInput.style.opacity = '1';
        }
    });

    // Download buttons
    document.getElementById('download-json').addEventListener('click', downloadJSON);
    document.getElementById('download-csv').addEventListener('click', downloadCSV);
}

// Update payout label (1.5 → 3:2, 1.2 → 6:5)
function updatePayoutLabel(value) {
    const label = document.getElementById('payout-label');
    if (value === 1.5) {
        label.textContent = '3:2';
    } else if (value === 1.2) {
        label.textContent = '6:5';
    } else {
        label.textContent = `${value}:1`;
    }
}

// Check for custom strategy in localStorage
function checkForCustomStrategy() {
    const customStrategy = localStorage.getItem('customStrategy');
    if (customStrategy) {
        console.log('Custom strategy found in localStorage');
    }
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();

    // Hide previous results/errors
    hideResults();
    hideError();

    // Show loading spinner
    showLoading();

    // Disable form
    setFormDisabled(true);

    try {
        // Build request payload
        const payload = buildRequestPayload();

        // Validate payload
        if (!validatePayload(payload)) {
            throw new Error('Invalid configuration');
        }

        // Send request to API
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Simulation failed');
        }

        // Get results
        const results = await response.json();
        currentResults = results;

        // Display results
        displayResults(results);

    } catch (error) {
        console.error('Simulation error:', error);
        showError(error.message);
    } finally {
        hideLoading();
        setFormDisabled(false);
    }
}

// Build request payload from form
function buildRequestPayload() {
    const payload = {
        game_rules: {
            dealer_hits_soft_17: document.getElementById('dealer_hits_soft_17').checked,
            surrender_allowed: document.getElementById('surrender_allowed').checked,
            double_after_split: document.getElementById('double_after_split').checked,
            blackjack_payout: parseFloat(document.getElementById('blackjack_payout').value)
        },
        shoe: {
            num_decks: parseInt(document.getElementById('num_decks').value),
            penetration: parseFloat(document.getElementById('penetration').value),
            infinite_shoe: document.getElementById('infinite_shoe').checked
        },
        simulation: {
            total_hands: parseInt(document.getElementById('total_hands').value),
            num_sessions: parseInt(document.getElementById('num_sessions').value),
            strategy: document.getElementById('strategy').value,
            track_hands: false
        }
    };

    // Add custom strategy if selected
    if (payload.simulation.strategy === 'custom') {
        const customStrategyJSON = localStorage.getItem('customStrategy');
        if (customStrategyJSON) {
            const customStrategy = JSON.parse(customStrategyJSON);
            payload.simulation.custom_strategy = customStrategy;
        } else {
            throw new Error('Custom strategy not found');
        }
    }

    return payload;
}

// Validate payload
function validatePayload(payload) {
    if (payload.simulation.total_hands < 100 || payload.simulation.total_hands > 1000000) {
        showError('Total hands must be between 100 and 1,000,000');
        return false;
    }
    if (payload.simulation.num_sessions < 1 || payload.simulation.num_sessions > 1000) {
        showError('Number of sessions must be between 1 and 1,000');
        return false;
    }
    return true;
}

// Display results
function displayResults(results) {
    const summary = results.summary;

    // Update summary stats
    document.getElementById('ev-value').textContent = `${(summary.ev_percent).toFixed(4)}%`;
    document.getElementById('win-rate').textContent = `${(summary.win_rate * 100).toFixed(2)}%`;
    document.getElementById('total-payout').textContent = summary.total_payout.toFixed(2);
    document.getElementById('total-hands').textContent = summary.total_hands.toLocaleString();

    // Color-code EV card
    const evCard = document.getElementById('ev-value').closest('.stat-card');
    evCard.classList.remove('positive', 'negative');
    if (summary.ev_per_hand > 0) {
        evCard.classList.add('positive');
    } else if (summary.ev_per_hand < 0) {
        evCard.classList.add('negative');
    }

    // Create chart
    createOutcomeChart(summary);

    // Update detailed stats table
    updateStatsTable(summary);

    // Show results section
    showResults();
}

// Create pie chart for outcomes
function createOutcomeChart(summary) {
    const ctx = document.getElementById('outcomeChart');

    // Destroy existing chart if any
    if (outcomeChart) {
        outcomeChart.destroy();
    }

    outcomeChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Wins', 'Losses', 'Pushes'],
            datasets: [{
                data: [summary.win_count, summary.loss_count, summary.push_count],
                backgroundColor: [
                    '#27ae60',  // Green for wins
                    '#e74c3c',  // Red for losses
                    '#95a5a6'   // Gray for pushes
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Outcome Distribution',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Update detailed stats table
function updateStatsTable(summary) {
    const tbody = document.getElementById('stats-tbody');
    tbody.innerHTML = '';

    const totalHands = summary.total_hands;

    const stats = [
        { label: 'Wins', count: summary.win_count },
        { label: 'Losses', count: summary.loss_count },
        { label: 'Pushes', count: summary.push_count },
        { label: 'Blackjacks', count: summary.blackjack_count },
        { label: 'Busts', count: summary.bust_count },
        { label: 'Surrenders', count: summary.surrender_count },
        { label: 'Doubles', count: summary.double_count }
    ];

    stats.forEach(stat => {
        const row = document.createElement('tr');
        const percentage = ((stat.count / totalHands) * 100).toFixed(2);

        row.innerHTML = `
            <td>${stat.label}</td>
            <td>${stat.count.toLocaleString()}</td>
            <td>${percentage}%</td>
        `;

        tbody.appendChild(row);
    });
}

// Download results as JSON
function downloadJSON() {
    if (!currentResults) return;

    const dataStr = JSON.stringify(currentResults, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `simulation_results_${Date.now()}.json`;
    link.click();

    URL.revokeObjectURL(url);
}

// Download results as CSV
function downloadCSV() {
    if (!currentResults) return;

    const summary = currentResults.summary;

    // Build CSV content
    let csv = 'Metric,Value\n';
    csv += `Total Hands,${summary.total_hands}\n`;
    csv += `Total Payout,${summary.total_payout}\n`;
    csv += `EV Per Hand,${summary.ev_per_hand}\n`;
    csv += `EV Percent,${summary.ev_percent}\n`;
    csv += `Win Count,${summary.win_count}\n`;
    csv += `Loss Count,${summary.loss_count}\n`;
    csv += `Push Count,${summary.push_count}\n`;
    csv += `Win Rate,${summary.win_rate}\n`;
    csv += `Blackjack Count,${summary.blackjack_count}\n`;
    csv += `Bust Count,${summary.bust_count}\n`;
    csv += `Surrender Count,${summary.surrender_count}\n`;
    csv += `Double Count,${summary.double_count}\n`;

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `simulation_results_${Date.now()}.csv`;
    link.click();

    URL.revokeObjectURL(url);
}

// UI Helper Functions
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showResults() {
    document.getElementById('results').classList.remove('hidden');
}

function hideResults() {
    document.getElementById('results').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    document.getElementById('error').classList.add('hidden');
}

function setFormDisabled(disabled) {
    const button = document.getElementById('run-button');
    button.disabled = disabled;

    const inputs = document.querySelectorAll('input, select, button');
    inputs.forEach(input => {
        if (input.id !== 'run-button') {
            input.disabled = disabled;
        }
    });
}
