// Strategy editor logic

// Dealer upcards (columns)
const DEALER_CARDS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A'];

// Player totals for each table type
const HARD_TOTALS = Array.from({length: 17}, (_, i) => (5 + i).toString()); // 5-21
const SOFT_TOTALS = Array.from({length: 9}, (_, i) => (13 + i).toString()); // 13-21
const PAIRS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A'];

// Available actions
const ACTIONS = {
    hard_totals: ['hit', 'stand', 'double_else_hit', 'double_else_stand', 'surrender_else_hit'],
    soft_totals: ['hit', 'stand', 'double_else_hit', 'double_else_stand'],
    pairs: ['hit', 'stand', 'split', 'double_else_hit', 'surrender_else_split']
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadAvailableStrategies();
    initializeTables();
    setupEventListeners();
    checkLocalStorage();
});

// Load available strategies from API
async function loadAvailableStrategies() {
    try {
        const response = await fetch('/api/strategies');
        const data = await response.json();

        const select = document.getElementById('existing-strategies');
        data.strategies.forEach(strat => {
            const option = document.createElement('option');
            option.value = strat.id;
            option.textContent = strat.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading strategies:', error);
    }
}

// Initialize strategy tables with default action 'hit'
function initializeTables() {
    buildTable('hard-totals-table', HARD_TOTALS, DEALER_CARDS, ACTIONS.hard_totals, 'hit');
    buildTable('soft-totals-table', SOFT_TOTALS, DEALER_CARDS, ACTIONS.soft_totals, 'hit');
    buildTable('pairs-table', PAIRS, DEALER_CARDS, ACTIONS.pairs, 'hit');
}

// Build a strategy table
function buildTable(tableId, rowHeaders, colHeaders, actions, defaultAction) {
    const table = document.getElementById(tableId);
    table.innerHTML = '';

    // Create header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    // Empty corner cell
    const cornerCell = document.createElement('th');
    cornerCell.textContent = 'Player';
    cornerCell.className = 'row-header';
    headerRow.appendChild(cornerCell);

    // Dealer upcard headers
    colHeaders.forEach(card => {
        const th = document.createElement('th');
        th.textContent = card;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create body rows
    const tbody = document.createElement('tbody');
    rowHeaders.forEach(rowHeader => {
        const row = document.createElement('tr');

        // Row header (player total or pair)
        const th = document.createElement('th');
        th.className = 'row-header';
        if (tableId === 'pairs-table') {
            th.textContent = `${rowHeader}-${rowHeader}`;
        } else {
            th.textContent = rowHeader;
        }
        row.appendChild(th);

        // Create select dropdowns for each dealer upcard
        colHeaders.forEach(dealerCard => {
            const td = document.createElement('td');
            const select = document.createElement('select');
            select.dataset.playerTotal = rowHeader;
            select.dataset.dealerCard = dealerCard;
            select.dataset.tableType = tableId;

            // Add action options
            actions.forEach(action => {
                const option = document.createElement('option');
                option.value = action;
                option.textContent = formatActionLabel(action);
                if (action === defaultAction) {
                    option.selected = true;
                }
                select.appendChild(option);
            });

            td.appendChild(select);
            row.appendChild(td);
        });

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
}

// Format action label for display
function formatActionLabel(action) {
    const labels = {
        'hit': 'Hit',
        'stand': 'Stand',
        'double_else_hit': 'Double/Hit',
        'double_else_stand': 'Double/Stand',
        'split': 'Split',
        'surrender_else_hit': 'Surrender/Hit',
        'surrender_else_split': 'Surrender/Split'
    };
    return labels[action] || action;
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('load-strategy-btn').addEventListener('click', loadStrategy);
    document.getElementById('reset-btn').addEventListener('click', resetTables);
    document.getElementById('save-json-btn').addEventListener('click', saveAsJSON);
    document.getElementById('use-in-sim-btn').addEventListener('click', useInSimulation);
    document.getElementById('quick-test-btn').addEventListener('click', quickTest);
}

// Check localStorage for existing custom strategy
function checkLocalStorage() {
    const savedStrategy = localStorage.getItem('customStrategy');
    if (savedStrategy) {
        try {
            const strategy = JSON.parse(savedStrategy);
            if (strategy.name) {
                document.getElementById('strategy-name').value = strategy.name;
            }
            if (strategy.description) {
                document.getElementById('strategy-description').value = strategy.description;
            }
            if (strategy.strategy) {
                populateTables(strategy.strategy);
            }
        } catch (error) {
            console.error('Error loading saved strategy:', error);
        }
    }
}

// Load strategy from API
async function loadStrategy() {
    const strategyId = document.getElementById('existing-strategies').value;
    if (!strategyId) {
        alert('Please select a strategy to load');
        return;
    }

    try {
        const response = await fetch(`/api/strategies/${strategyId}`);
        if (!response.ok) {
            throw new Error('Failed to load strategy');
        }

        const data = await response.json();

        // Populate metadata
        if (data.name) {
            document.getElementById('strategy-name').value = data.name;
        }
        if (data.description) {
            document.getElementById('strategy-description').value = data.description;
        }

        // Populate tables
        if (data.strategy) {
            populateTables(data.strategy);
        }

        alert(`Loaded strategy: ${data.name}`);
    } catch (error) {
        console.error('Error loading strategy:', error);
        alert('Failed to load strategy');
    }
}

// Populate tables with strategy data
function populateTables(strategyData) {
    // Hard totals
    if (strategyData.hard_totals) {
        populateTable('hard-totals-table', strategyData.hard_totals);
    }

    // Soft totals
    if (strategyData.soft_totals) {
        populateTable('soft-totals-table', strategyData.soft_totals);
    }

    // Pairs
    if (strategyData.pairs) {
        populateTable('pairs-table', strategyData.pairs);
    }
}

// Populate a single table with strategy data
function populateTable(tableId, strategyData) {
    const table = document.getElementById(tableId);
    const selects = table.querySelectorAll('select');

    selects.forEach(select => {
        const playerTotal = select.dataset.playerTotal;
        const dealerCard = select.dataset.dealerCard;

        if (strategyData[playerTotal] && strategyData[playerTotal][dealerCard]) {
            const action = strategyData[playerTotal][dealerCard];
            select.value = action;
        }
    });
}

// Reset tables to default (all 'hit')
function resetTables() {
    if (!confirm('Reset all tables to default (Hit)? This will clear your current strategy.')) {
        return;
    }

    document.getElementById('strategy-name').value = 'My Custom Strategy';
    document.getElementById('strategy-description').value = '';

    const allSelects = document.querySelectorAll('.strategy-table select');
    allSelects.forEach(select => {
        select.value = 'hit';
    });

    // Clear localStorage
    localStorage.removeItem('customStrategy');
}

// Extract strategy from tables
function extractStrategyFromTables() {
    const strategy = {
        hard_totals: {},
        soft_totals: {},
        pairs: {}
    };

    // Extract hard totals
    const hardTable = document.getElementById('hard-totals-table');
    extractTableData(hardTable, strategy.hard_totals);

    // Extract soft totals
    const softTable = document.getElementById('soft-totals-table');
    extractTableData(softTable, strategy.soft_totals);

    // Extract pairs
    const pairsTable = document.getElementById('pairs-table');
    extractTableData(pairsTable, strategy.pairs);

    return strategy;
}

// Extract data from a table
function extractTableData(table, targetObj) {
    const selects = table.querySelectorAll('select');

    selects.forEach(select => {
        const playerTotal = select.dataset.playerTotal;
        const dealerCard = select.dataset.dealerCard;
        const action = select.value;

        if (!targetObj[playerTotal]) {
            targetObj[playerTotal] = {};
        }

        targetObj[playerTotal][dealerCard] = action;
    });
}

// Save strategy as JSON file
function saveAsJSON() {
    const strategyName = document.getElementById('strategy-name').value || 'custom_strategy';
    const description = document.getElementById('strategy-description').value || '';

    const strategyData = extractStrategyFromTables();

    const strategyJSON = {
        name: strategyName,
        description: description,
        strategy: strategyData
    };

    // Create blob and download
    const dataStr = JSON.stringify(strategyJSON, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;

    // Generate filename with date
    const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const safeName = strategyName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    link.download = `${safeName}_${date}.json`;

    link.click();
    URL.revokeObjectURL(url);

    alert('Strategy saved as JSON file!');
}

// Use strategy in simulation (save to localStorage and redirect)
function useInSimulation() {
    const strategyName = document.getElementById('strategy-name').value || 'Custom Strategy';
    const description = document.getElementById('strategy-description').value || '';

    const strategyData = extractStrategyFromTables();

    const strategyJSON = {
        name: strategyName,
        description: description,
        strategy: strategyData
    };

    // Save to localStorage
    localStorage.setItem('customStrategy', JSON.stringify(strategyJSON));

    alert('Custom strategy saved! Redirecting to simulator...');

    // Redirect to main page with URL param to trigger custom strategy selection
    window.location.href = '/?strategy=custom';
}

// Quick test: run 10K hands and show EV
async function quickTest() {
    const btn = document.getElementById('quick-test-btn');
    const resultSpan = document.getElementById('quick-test-result');

    btn.disabled = true;
    resultSpan.textContent = 'Running...';
    resultSpan.style.color = '#7f8c8d';

    try {
        const strategyData = extractStrategyFromTables();
        const strategyName = document.getElementById('strategy-name').value || 'Custom Strategy';

        const payload = {
            game_rules: {
                dealer_hits_soft_17: true,
                surrender_allowed: true,
                double_after_split: true,
                blackjack_payout: 1.5
            },
            shoe: {
                num_decks: 6,
                penetration: 0.75,
                infinite_shoe: false
            },
            simulation: {
                total_hands: 10000,
                num_sessions: 1,
                strategy: 'custom',
                track_hands: false,
                debug_mode: false,
                custom_strategy: {
                    name: strategyName,
                    strategy: strategyData
                }
            }
        };

        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Simulation failed');
        }

        const results = await response.json();
        const ev = results.summary.ev_percent.toFixed(3);
        const color = results.summary.ev_per_hand >= 0 ? '#27ae60' : '#e74c3c';

        resultSpan.textContent = `EV: ${ev}% (10K hands, 6-deck, H17)`;
        resultSpan.style.color = color;
    } catch (error) {
        resultSpan.textContent = `Error: ${error.message}`;
        resultSpan.style.color = '#e74c3c';
    } finally {
        btn.disabled = false;
    }
}
