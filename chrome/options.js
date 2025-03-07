// Get DOM elements
const apiKeyInput = document.getElementById('apiKey');
const modelSelect = document.getElementById('model');
const temperatureInput = document.getElementById('temperature');
const maxTokensInput = document.getElementById('maxTokens');
const enablePageAnalysisCheckbox = document.getElementById('enablePageAnalysis');
const enableTextSelectionCheckbox = document.getElementById('enableTextSelection');
const enableScreenshotAnalysisCheckbox = document.getElementById('enableScreenshotAnalysis');
const logLevelSelect = document.getElementById('logLevel');
const saveButton = document.getElementById('save');
const resetButton = document.getElementById('reset');
const statusDiv = document.getElementById('status');

// Default settings
const defaultSettings = {
    apiKey: '',
    model: 'google/gemini-pro',
    temperature: 0.7,
    maxTokens: 2048,
    enablePageAnalysis: true,
    enableTextSelection: true,
    enableScreenshotAnalysis: true,
    logLevel: 'info'
};

// Load settings
chrome.storage.sync.get(defaultSettings, (items) => {
    apiKeyInput.value = items.apiKey;
    modelSelect.value = items.model;
    temperatureInput.value = items.temperature;
    maxTokensInput.value = items.maxTokens;
    enablePageAnalysisCheckbox.checked = items.enablePageAnalysis;
    enableTextSelectionCheckbox.checked = items.enableTextSelection;
    enableScreenshotAnalysisCheckbox.checked = items.enableScreenshotAnalysis;
    logLevelSelect.value = items.logLevel;
});

// Save settings
saveButton.addEventListener('click', async () => {
    try {
        // Validate temperature
        const temperature = parseFloat(temperatureInput.value);
        if (isNaN(temperature) || temperature < 0 || temperature > 1) {
            throw new Error('Temperature must be between 0 and 1');
        }
        
        // Validate max tokens
        const maxTokens = parseInt(maxTokensInput.value);
        if (isNaN(maxTokens) || maxTokens < 1 || maxTokens > 4096) {
            throw new Error('Max tokens must be between 1 and 4096');
        }
        
        // Save settings
        await chrome.storage.sync.set({
            apiKey: apiKeyInput.value,
            model: modelSelect.value,
            temperature: temperature,
            maxTokens: maxTokens,
            enablePageAnalysis: enablePageAnalysisCheckbox.checked,
            enableTextSelection: enableTextSelectionCheckbox.checked,
            enableScreenshotAnalysis: enableScreenshotAnalysisCheckbox.checked,
            logLevel: logLevelSelect.value
        });
        
        // Show success message
        showStatus('Settings saved successfully', 'success');
        
    } catch (error) {
        showStatus(error.message, 'error');
    }
});

// Reset settings
resetButton.addEventListener('click', async () => {
    try {
        // Reset to defaults
        await chrome.storage.sync.set(defaultSettings);
        
        // Reset form
        apiKeyInput.value = defaultSettings.apiKey;
        modelSelect.value = defaultSettings.model;
        temperatureInput.value = defaultSettings.temperature;
        maxTokensInput.value = defaultSettings.maxTokens;
        enablePageAnalysisCheckbox.checked = defaultSettings.enablePageAnalysis;
        enableTextSelectionCheckbox.checked = defaultSettings.enableTextSelection;
        enableScreenshotAnalysisCheckbox.checked = defaultSettings.enableScreenshotAnalysis;
        logLevelSelect.value = defaultSettings.logLevel;
        
        // Show success message
        showStatus('Settings reset to defaults', 'success');
        
    } catch (error) {
        showStatus(error.message, 'error');
    }
});

// Show status message
function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
    
    // Hide message after 3 seconds
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

// Validate inputs
function validateInputs() {
    const temperature = parseFloat(temperatureInput.value);
    const maxTokens = parseInt(maxTokensInput.value);
    
    if (isNaN(temperature) || temperature < 0 || temperature > 1) {
        temperatureInput.value = defaultSettings.temperature;
    }
    
    if (isNaN(maxTokens) || maxTokens < 1 || maxTokens > 4096) {
        maxTokensInput.value = defaultSettings.maxTokens;
    }
}

// Add input validation
temperatureInput.addEventListener('change', validateInputs);
maxTokensInput.addEventListener('change', validateInputs); 