// Get DOM elements
const modelSelect = document.getElementById('model');
const promptInput = document.getElementById('prompt');
const analyzeButton = document.getElementById('analyze');
const loadingDiv = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');

// Load settings
chrome.storage.sync.get(
    ['apiKey', 'model', 'temperature', 'maxTokens'],
    (items) => {
        if (items.model) {
            modelSelect.value = items.model;
        }
    }
);

// Handle analyze button click
analyzeButton.addEventListener('click', async () => {
    try {
        // Show loading
        loadingDiv.style.display = 'block';
        resultDiv.textContent = '';
        errorDiv.textContent = '';
        analyzeButton.disabled = true;
        
        // Get settings
        const settings = await chrome.storage.sync.get([
            'apiKey',
            'model',
            'temperature',
            'maxTokens'
        ]);
        
        // Validate API key
        if (!settings.apiKey) {
            throw new Error('API key not found. Please set it in settings.');
        }
        
        // Get active tab
        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });
        
        // Get page content
        const [{result}] = await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            function: () => {
                return {
                    title: document.title,
                    url: window.location.href,
                    content: document.body.innerText
                };
            }
        });
        
        // Prepare prompt
        const prompt = promptInput.value.trim();
        const context = `Title: ${result.title}\nURL: ${result.url}\n\nContent:\n${result.content}\n\nPrompt: ${prompt}`;
        
        // Send request to background script
        const response = await chrome.runtime.sendMessage({
            type: 'analyze',
            data: {
                model: modelSelect.value,
                prompt: context,
                temperature: settings.temperature || 0.7,
                maxTokens: settings.maxTokens || 2048
            }
        });
        
        // Handle response
        if (response.error) {
            throw new Error(response.error);
        }
        
        // Show result
        resultDiv.textContent = response.result;
        
    } catch (error) {
        errorDiv.textContent = error.message;
    } finally {
        loadingDiv.style.display = 'none';
        analyzeButton.disabled = false;
    }
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && event.ctrlKey) {
        analyzeButton.click();
    }
});

// Handle model change
modelSelect.addEventListener('change', () => {
    chrome.storage.sync.set({model: modelSelect.value});
}); 