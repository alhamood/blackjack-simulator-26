// Global variables
let currentResults = null;
let handOutcomeChart = null;
let sessionOutcomeChart = null;

// Initialize page on load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDefaults();
    setupEventListeners();
    checkForCustomStrategy();
    fetchTimeEstimate();
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

    // Total hands calculation (hands per session × sessions) and time estimate
    document.getElementById('total_hands').addEventListener('input', updateTotalHandsDisplay);
    document.getElementById('num_sessions').addEventListener('input', updateTotalHandsDisplay);
    document.getElementById('strategy').addEventListener('change', updateTotalHandsDisplay);
    document.getElementById('num_decks').addEventListener('input', updateTotalHandsDisplay);
    document.getElementById('penetration').addEventListener('input', updateTotalHandsDisplay);
    document.getElementById('infinite_shoe').addEventListener('change', updateTotalHandsDisplay);

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

// Update total hands display (hands per session × sessions) and time estimate
let estimateTimer = null;

function updateTotalHandsDisplay() {
    const handsPerSession = parseInt(document.getElementById('total_hands').value) || 0;
    const numSessions = parseInt(document.getElementById('num_sessions').value) || 0;
    const totalHands = handsPerSession * numSessions;

    document.getElementById('total-hands-display').textContent = formatNumber(totalHands);

    // Debounce the estimate call
    if (estimateTimer) clearTimeout(estimateTimer);
    estimateTimer = setTimeout(fetchTimeEstimate, 500);
}

async function fetchTimeEstimate() {
    const estimateSpan = document.getElementById('time-estimate');

    try {
        const payload = buildRequestPayload();
        if (!validatePayloadSilent(payload)) {
            estimateSpan.textContent = '';
            return;
        }

        estimateSpan.textContent = '(estimating...)';

        const response = await fetch('/api/estimate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            estimateSpan.textContent = '';
            return;
        }

        const data = await response.json();
        const secs = data.estimated_seconds;

        if (secs >= 60) {
            estimateSpan.textContent = `(~${(secs / 60).toFixed(1)} min)`;
        } else {
            estimateSpan.textContent = `(~${secs.toFixed(1)}s)`;
        }
    } catch {
        estimateSpan.textContent = '';
    }
}

// Silent validation (no error display) for estimate calls
function validatePayloadSilent(payload) {
    const handsPerSession = payload.simulation.total_hands;
    const numSessions = payload.simulation.num_sessions;
    const actualTotalHands = handsPerSession * numSessions;

    if (handsPerSession < 100 || handsPerSession > 10000000) return false;
    if (numSessions < 1 || numSessions > 100000) return false;
    if (actualTotalHands > 100000000) return false;
    return true;
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

        // Validate payload (error message already shown by validatePayload)
        if (!validatePayload(payload)) {
            return; // Don't throw - error already displayed
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
            track_hands: false,
            debug_mode: document.getElementById('debug_mode').checked
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
    const handsPerSession = payload.simulation.total_hands;
    const numSessions = payload.simulation.num_sessions;
    const actualTotalHands = handsPerSession * numSessions;

    if (handsPerSession < 100 || handsPerSession > 10000000) {
        showError('Hands per session must be between 100 and 10,000,000');
        return false;
    }
    if (numSessions < 1 || numSessions > 100000) {
        showError('Number of sessions must be between 1 and 100,000');
        return false;
    }

    // Reasonable limit on total computation (100 million total hands)
    if (actualTotalHands > 100000000) {
        showError(`Total hands (${formatNumber(actualTotalHands)}) exceeds limit of 100,000,000. Reduce hands per session or number of sessions.`);
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

    // Display elapsed time
    if (summary.elapsed_seconds !== undefined) {
        if (summary.elapsed_seconds >= 60) {
            document.getElementById('elapsed-time').textContent = `${(summary.elapsed_seconds / 60).toFixed(1)}m`;
        } else {
            document.getElementById('elapsed-time').textContent = `${summary.elapsed_seconds.toFixed(2)}s`;
        }
    }

    // Color-code EV card
    const evCard = document.getElementById('ev-value').closest('.stat-card');
    evCard.classList.remove('positive', 'negative');
    if (summary.ev_per_hand > 0) {
        evCard.classList.add('positive');
    } else if (summary.ev_per_hand < 0) {
        evCard.classList.add('negative');
    }

    // Create charts
    createSessionOutcomeChart(results);
    createHandOutcomeChart(results);

    // Update stats tables
    updateSessionStatsTable(results);
    updateStatsTable(summary);

    // Display debug information if available
    if (results.debug) {
        displayDebugInfo(results.debug);
    } else {
        document.getElementById('debug-section').classList.add('hidden');
    }

    // Show results section
    showResults();
}

// Create hand-level outcome chart
function createHandOutcomeChart(results) {
    const ctx = document.getElementById('handOutcomeChart');

    // Destroy existing chart if any
    if (handOutcomeChart) {
        handOutcomeChart.destroy();
    }

    // Analyze hand results to categorize outcomes
    const categories = analyzeHandOutcomes(results);

    // Sort data descending by count
    const combined = categories.labels.map((label, i) => ({
        label: label,
        data: categories.data[i],
        color: categories.colors[i],
        payout: categories.payouts[i]
    }));
    combined.sort((a, b) => b.data - a.data);

    const sortedLabels = combined.map(item => item.label);
    const sortedData = combined.map(item => item.data);
    const sortedColors = combined.map(item => item.color);
    const sortedPayouts = combined.map(item => item.payout);

    handOutcomeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedLabels,
            datasets: [{
                label: 'Hand Count',
                data: sortedData,
                backgroundColor: sortedColors,
                borderWidth: 1,
                borderColor: '#2c3e50'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed.y / total) * 100).toFixed(2);
                            const payout = sortedPayouts[context.dataIndex];
                            return [
                                `${context.parsed.y.toLocaleString()} hands (${percentage}%)`,
                                `Est. payout: ${formatAbbreviated(payout)} units`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Hands'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Outcome Type'
                    }
                }
            },
            animation: {
                onComplete: function() {
                    const chart = this;
                    const ctx = chart.ctx;
                    ctx.save();
                    ctx.font = '11px sans-serif';
                    ctx.textAlign = 'center';

                    chart.data.datasets[0].data.forEach((value, index) => {
                        if (value === 0) return;
                        const meta = chart.getDatasetMeta(0);
                        const bar = meta.data[index];
                        const payout = sortedPayouts[index];
                        const label = formatAbbreviated(payout);

                        ctx.fillStyle = payout >= 0 ? '#1a7a3a' : '#a82020';
                        ctx.fillText(label, bar.x, bar.y - 4);
                    });
                    ctx.restore();
                }
            }
        }
    });
}

// Create session-level outcome chart (histogram)
function createSessionOutcomeChart(results) {
    const ctx = document.getElementById('sessionOutcomeChart');

    // Destroy existing chart if any
    if (sessionOutcomeChart) {
        sessionOutcomeChart.destroy();
    }

    // Create histogram data from session payouts
    const histogramData = createSessionHistogram(results);

    // Store binPayouts for the datalabels plugin
    const binPayouts = histogramData.binPayouts;

    sessionOutcomeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: histogramData.labels,
            datasets: [{
                label: 'Session Count',
                data: histogramData.data,
                backgroundColor: histogramData.colors,
                borderWidth: 1,
                borderColor: '#2c3e50'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const sessions = context.parsed.y;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((sessions / total) * 100).toFixed(1);
                            const payout = binPayouts[context.dataIndex];
                            return [
                                `${sessions} sessions (${percentage}%)`,
                                `Total payout: ${formatAbbreviated(payout)} units`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Sessions'
                    },
                    ticks: {
                        precision: 0
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Session Payout (units)'
                    }
                }
            },
            animation: {
                onComplete: function() {
                    const chart = this;
                    const ctx = chart.ctx;
                    ctx.save();
                    ctx.font = '11px sans-serif';
                    ctx.textAlign = 'center';

                    chart.data.datasets[0].data.forEach((value, index) => {
                        if (value === 0) return;
                        const meta = chart.getDatasetMeta(0);
                        const bar = meta.data[index];
                        const payout = binPayouts[index];
                        const label = formatAbbreviated(payout);

                        ctx.fillStyle = payout >= 0 ? '#1a7a3a' : '#a82020';
                        ctx.fillText(label, bar.x, bar.y - 4);
                    });
                    ctx.restore();
                }
            }
        }
    });
}

// Analyze hand outcomes from results (uses summary stats from ALL sessions)
function analyzeHandOutcomes(results) {
    const summary = results.summary;
    const bjPayout = parseFloat(document.getElementById('blackjack_payout').value) || 1.5;

    // Estimate breakdown from summary statistics
    // Note: Doubles overlap with wins/losses, so we estimate the split
    const estimatedDoubleWins = Math.round(summary.double_count * summary.win_rate);
    const estimatedDoubleLosses = summary.double_count - estimatedDoubleWins;

    const regularWins = summary.win_count - summary.blackjack_count - estimatedDoubleWins;
    const regularLosses = summary.loss_count - summary.surrender_count - estimatedDoubleLosses;

    return {
        labels: ['Blackjacks', 'Double Wins', 'Double Losses', 'Regular Wins', 'Regular Losses', 'Surrenders', 'Pushes'],
        data: [
            summary.blackjack_count,
            estimatedDoubleWins,
            estimatedDoubleLosses,
            Math.max(0, regularWins),
            Math.max(0, regularLosses),
            summary.surrender_count,
            summary.push_count
        ],
        payouts: [
            summary.blackjack_count * bjPayout,
            estimatedDoubleWins * 2,
            -estimatedDoubleLosses * 2,
            Math.max(0, regularWins),
            -Math.max(0, regularLosses),
            -summary.surrender_count * 0.5,
            0
        ],
        colors: [
            '#f39c12',  // Orange for blackjacks
            '#27ae60',  // Green for double wins
            '#c0392b',  // Dark red for double losses
            '#2ecc71',  // Light green for regular wins
            '#e74c3c',  // Red for regular losses
            '#95a5a6',  // Gray for surrenders
            '#7f8c8d'   // Dark gray for pushes
        ]
    };
}

// Analyze session outcomes
function analyzeSessionOutcomes(results) {
    if (!results.sessions || results.sessions.length === 0) {
        return { labels: [], data: [] };
    }

    let winners = 0;
    let losers = 0;
    let breakeven = 0;

    results.sessions.forEach(session => {
        if (session.total_payout > 0) {
            winners++;
        } else if (session.total_payout < 0) {
            losers++;
        } else {
            breakeven++;
        }
    });

    const labels = [];
    const data = [];

    if (winners > 0) {
        labels.push(`Winning (${winners})`);
        data.push(winners);
    }
    if (losers > 0) {
        labels.push(`Losing (${losers})`);
        data.push(losers);
    }
    if (breakeven > 0) {
        labels.push(`Break-even (${breakeven})`);
        data.push(breakeven);
    }

    return { labels, data };
}

// Format a number in abbreviated form (e.g. +1.2k, -340)
function formatAbbreviated(value) {
    const abs = Math.abs(value);
    const sign = value < 0 ? '-' : '+';
    if (abs >= 1000000) {
        return `${sign}${(abs / 1000000).toFixed(1)}M`;
    } else if (abs >= 1000) {
        return `${sign}${(abs / 1000).toFixed(1)}k`;
    } else {
        return `${sign}${abs.toFixed(0)}`;
    }
}

// Create histogram data from session payouts
function createSessionHistogram(results) {
    if (!results.sessions || results.sessions.length === 0) {
        return { labels: [], data: [], colors: [], binPayouts: [] };
    }

    const payouts = results.sessions.map(s => s.total_payout);
    const min = Math.min(...payouts);
    const max = Math.max(...payouts);
    const n = payouts.length;
    const targetBins = Math.min(30, Math.max(10, Math.ceil(Math.log2(n) + 1)));

    // Build bin edges with 0 as a mandatory boundary
    let edges;
    if (min >= 0) {
        // All non-negative
        const binSize = (max - min) / targetBins || 1;
        edges = [];
        for (let i = 0; i <= targetBins; i++) edges.push(min + i * binSize);
    } else if (max <= 0) {
        // All non-positive
        const binSize = (max - min) / targetBins || 1;
        edges = [];
        for (let i = 0; i <= targetBins; i++) edges.push(min + i * binSize);
    } else {
        // Mixed: split bins proportionally on each side of 0
        const negRange = -min;
        const posRange = max;
        const totalRange = negRange + posRange;
        const negBins = Math.max(1, Math.round(targetBins * (negRange / totalRange)));
        const posBins = Math.max(1, targetBins - negBins);
        const negBinSize = negRange / negBins;
        const posBinSize = posRange / posBins;

        edges = [];
        for (let i = 0; i <= negBins; i++) edges.push(min + i * negBinSize);
        for (let i = 1; i <= posBins; i++) edges.push(i * posBinSize);
    }

    const numBins = edges.length - 1;
    const bins = new Array(numBins).fill(0);
    const binPayouts = new Array(numBins).fill(0);
    const binLabels = [];
    const binColors = [];

    for (let i = 0; i < numBins; i++) {
        const binStart = edges[i];
        const binEnd = edges[i + 1];
        const binMid = (binStart + binEnd) / 2;

        binLabels.push(binMid.toFixed(1));

        if (binStart >= 0) {
            binColors.push('#27ae60');  // Green for winning
        } else if (binEnd <= 0) {
            binColors.push('#e74c3c');  // Red for losing
        } else {
            binColors.push('#3498db');  // Blue for exact zero boundary
        }
    }

    // Count sessions and sum payouts per bin
    payouts.forEach(payout => {
        let idx = numBins - 1;
        for (let i = 0; i < numBins; i++) {
            if (payout < edges[i + 1] || i === numBins - 1) {
                idx = i;
                break;
            }
        }
        bins[idx]++;
        binPayouts[idx] += payout;
    });

    return {
        labels: binLabels,
        data: bins,
        colors: binColors,
        binPayouts: binPayouts
    };
}

// Update detailed stats table
function updateStatsTable(summary) {
    const tbody = document.getElementById('stats-tbody');
    tbody.innerHTML = '';

    const totalHands = summary.total_hands;

    // Estimate double breakdown based on win/loss rates among decided hands
    const decidedHands = summary.win_count + summary.loss_count;
    const winRateDecided = decidedHands > 0 ? summary.win_count / decidedHands : 0;
    const lossRateDecided = decidedHands > 0 ? summary.loss_count / decidedHands : 0;

    const estimatedDoubleWins = Math.round(summary.double_count * winRateDecided);
    const estimatedDoubleLosses = Math.round(summary.double_count * lossRateDecided);
    const estimatedDoublePushes = summary.double_count - estimatedDoubleWins - estimatedDoubleLosses;

    // Calculate regular (non-special) outcomes
    const regularWins = summary.win_count - summary.blackjack_count - estimatedDoubleWins;
    const regularLosses = summary.loss_count - summary.bust_count - summary.surrender_count - estimatedDoubleLosses;
    const regularPushes = summary.push_count - estimatedDoublePushes;

    // Build hierarchical stats with payout calculations
    const stats = [
        { label: 'Wins', count: summary.win_count, payout: summary.blackjack_count * 1.5 + estimatedDoubleWins * 2 + regularWins * 1, indent: false },
        { label: 'Blackjacks', count: summary.blackjack_count, payout: summary.blackjack_count * 1.5, indent: true },
        { label: 'Double Wins', count: estimatedDoubleWins, payout: estimatedDoubleWins * 2, indent: true },
        { label: 'Regular Wins', count: Math.max(0, regularWins), payout: Math.max(0, regularWins) * 1, indent: true },

        { label: 'Losses', count: summary.loss_count, payout: -(summary.bust_count + regularLosses + estimatedDoubleLosses * 2 + summary.surrender_count * 0.5), indent: false },
        { label: 'Busts', count: summary.bust_count, payout: -summary.bust_count, indent: true },
        { label: 'Surrenders', count: summary.surrender_count, payout: -summary.surrender_count * 0.5, indent: true },
        { label: 'Double Losses', count: estimatedDoubleLosses, payout: -estimatedDoubleLosses * 2, indent: true },
        { label: 'Regular Losses', count: Math.max(0, regularLosses), payout: -Math.max(0, regularLosses), indent: true },

        { label: 'Pushes', count: summary.push_count, payout: 0, indent: false },
        { label: 'Double Pushes', count: Math.max(0, estimatedDoublePushes), payout: 0, indent: true },
        { label: 'Regular Pushes', count: Math.max(0, regularPushes), payout: 0, indent: true },

        { label: '---', count: 0, payout: 0, indent: false, separator: true },
        { label: 'Splits', count: summary.split_count || 0, payout: 0, indent: false }
    ];

    stats.forEach(stat => {
        const row = document.createElement('tr');

        // Handle separator rows
        if (stat.separator) {
            row.innerHTML = `<td colspan="4" style="border-top: 1px solid #ddd;"></td>`;
        } else {
            const percentage = ((stat.count / totalHands) * 100).toFixed(2);
            const indentClass = stat.indent ? 'class="indent"' : '';

            row.innerHTML = `
                <td ${indentClass}>${stat.label}</td>
                <td>${stat.count.toLocaleString()}</td>
                <td>${percentage}%</td>
                <td>${stat.payout >= 0 ? '+' : ''}${stat.payout.toFixed(2)}</td>
            `;
        }

        tbody.appendChild(row);
    });
}

// Update session statistics table
function updateSessionStatsTable(results) {
    if (!results.sessions || results.sessions.length === 0) {
        document.getElementById('session-stats-section').classList.add('hidden');
        return;
    }

    document.getElementById('session-stats-section').classList.remove('hidden');

    // Extract session payouts
    const payouts = results.sessions.map(s => s.total_payout).sort((a, b) => a - b);
    const n = payouts.length;

    // Calculate percentiles
    const percentile = (p) => {
        const index = (p / 100) * (n - 1);
        const lower = Math.floor(index);
        const upper = Math.ceil(index);
        const weight = index - lower;
        return payouts[lower] * (1 - weight) + payouts[upper] * weight;
    };

    // Calculate statistics
    const mean = payouts.reduce((a, b) => a + b, 0) / n;
    const variance = payouts.reduce((sum, x) => sum + Math.pow(x - mean, 2), 0) / n;
    const stdDev = Math.sqrt(variance);

    const p10 = percentile(10);
    const p25 = percentile(25);
    const p50 = percentile(50);  // Median
    const p75 = percentile(75);
    const p90 = percentile(90);
    const best = payouts[n - 1];
    const worst = payouts[0];

    // Update table
    const tbody = document.getElementById('session-stats-tbody');
    tbody.innerHTML = `
        <tr>
            <td>Best Session</td>
            <td>${best >= 0 ? '+' : ''}${best.toFixed(3)} units</td>
            <td>Highest session payout</td>
        </tr>
        <tr>
            <td>Worst Session</td>
            <td>${worst >= 0 ? '+' : ''}${worst.toFixed(3)} units</td>
            <td>Lowest session payout</td>
        </tr>
        <tr>
            <td>Mean Payout</td>
            <td>${mean >= 0 ? '+' : ''}${mean.toFixed(3)} units</td>
            <td>Average session result</td>
        </tr>
        <tr>
            <td>Median (P50)</td>
            <td>${p50 >= 0 ? '+' : ''}${p50.toFixed(3)} units</td>
            <td>50th percentile</td>
        </tr>
        <tr>
            <td>Standard Deviation</td>
            <td>${stdDev.toFixed(3)} units</td>
            <td>Measure of variability</td>
        </tr>
        <tr>
            <td>P10</td>
            <td>${p10 >= 0 ? '+' : ''}${p10.toFixed(3)} units</td>
            <td>10% of sessions worse than this</td>
        </tr>
        <tr>
            <td>P25</td>
            <td>${p25 >= 0 ? '+' : ''}${p25.toFixed(3)} units</td>
            <td>25% of sessions worse than this</td>
        </tr>
        <tr>
            <td>P75</td>
            <td>${p75 >= 0 ? '+' : ''}${p75.toFixed(3)} units</td>
            <td>75% of sessions worse than this</td>
        </tr>
        <tr>
            <td>P90</td>
            <td>${p90 >= 0 ? '+' : ''}${p90.toFixed(3)} units</td>
            <td>90% of sessions worse than this</td>
        </tr>
    `;
}

// Display debug information
function displayDebugInfo(debug) {
    document.getElementById('debug-section').classList.remove('hidden');
    document.getElementById('debug-tracked-count').textContent = debug.total_tracked_hands.toLocaleString();

    const examplesDiv = document.getElementById('debug-examples');
    examplesDiv.innerHTML = '';

    const strategyExamples = debug.strategy_examples;
    const keys = Object.keys(strategyExamples).sort();

    if (keys.length === 0) {
        examplesDiv.innerHTML = '<p>No hand examples captured.</p>';
        return;
    }

    // Create table for strategy examples
    const table = document.createElement('table');
    table.className = 'debug-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Situation</th>
                <th>Count</th>
                <th>Examples</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

    const tbody = table.querySelector('tbody');

    keys.forEach(key => {
        const examples = strategyExamples[key];
        const row = document.createElement('tr');

        // Format examples with action history and split info
        const examplesList = examples.map(ex => {
            const initialCards = ex.initial_cards.join(' ');
            const soft = ex.initial_soft ? 's' : '';
            const pair = ex.initial_pair ? 'P' : '';

            let result = `<strong>${initialCards}</strong> (${ex.initial_value}${soft}${pair}) vs ${ex.dealer_upcard}<br>`;

            // Display split hands separately
            if (ex.split_hands_count && ex.split_hands_count > 1 && ex.split_hands_final && ex.split_hands_final.length > 0) {
                // Show each split hand on its own line
                ex.split_hands_final.forEach((hand, idx) => {
                    const handCards = hand.cards.join(' ');
                    const handValue = hand.value;
                    const handSoft = hand.soft ? 's' : '';
                    const handBust = hand.bust ? ' BUST' : '';
                    const handActions = hand.actions && hand.actions.length > 0 ? hand.actions.join(' → ') : 'stand';
                    const bet = ex.split_bets[idx];
                    const payout = ex.split_payouts[idx];

                    result += `  <span style="color: #2196f3;">Hand ${idx}:</span> ${handActions} → ${handCards} (${handValue}${handSoft}${handBust}) | Bet: ${bet} | Payout: ${payout >= 0 ? '+' : ''}${payout}<br>`;
                });

                // Add dealer final value
                result += `  <strong>Dealer:</strong> ${ex.dealer_value}<br>`;
                result += `  <strong>Total:</strong> Bet: ${ex.bet} | Payout: ${ex.payout >= 0 ? '+' : ''}${ex.payout} | Outcome: ${ex.outcome}`;
            } else {
                // Non-split hand - original format
                const actions = ex.actions && ex.actions.length > 0 ? ex.actions.join(' → ') : 'stand';
                const finalCards = ex.final_cards.join(' ');
                result += `  Actions: <em>${actions}</em><br>` +
                         `  Final: ${finalCards} (${ex.final_value}) | Dealer: ${ex.dealer_value}<br>` +
                         `  Outcome: ${ex.outcome} (${ex.payout >= 0 ? '+' : ''}${ex.payout})`;
            }

            return result;
        }).join('<br><br>');

        row.innerHTML = `
            <td><code>${key}</code></td>
            <td>${examples.length}</td>
            <td class="example-cell">${examplesList}</td>
        `;

        tbody.appendChild(row);
    });

    examplesDiv.appendChild(table);
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

function formatNumber(num) {
    return num.toLocaleString();
}
