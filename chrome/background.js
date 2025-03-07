// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'analyze') {
        handleAnalysis(message.data)
            .then(sendResponse)
            .catch(error => sendResponse({error: error.message}));
        return true; // Keep message channel open for async response
    }
});

// Handle keyboard commands
chrome.commands.onCommand.addListener(async (command) => {
    try {
        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });
        
        if (command === 'analyze-page') {
            // Send message to content script to analyze page
            chrome.tabs.sendMessage(tab.id, {
                type: 'analyze-page'
            });
        } else if (command === 'analyze-selection') {
            // Send message to content script to analyze selection
            chrome.tabs.sendMessage(tab.id, {
                type: 'analyze-selection'
            });
        }
    } catch (error) {
        console.error('Error handling command:', error);
    }
});

// Handle analysis request
async function handleAnalysis(data) {
    try {
        // Get API key from storage
        const {apiKey} = await chrome.storage.sync.get('apiKey');
        if (!apiKey) {
            throw new Error('API key not found');
        }
        
        // Prepare request
        const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/xraisen/agentic-ai'
            },
            body: JSON.stringify({
                model: data.model,
                messages: [
                    {
                        role: 'user',
                        content: data.prompt
                    }
                ],
                temperature: data.temperature,
                max_tokens: data.maxTokens
            })
        });
        
        // Handle response
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'API request failed');
        }
        
        const result = await response.json();
        return {
            result: result.choices[0].message.content
        };
        
    } catch (error) {
        console.error('Error in handleAnalysis:', error);
        throw error;
    }
}

// Handle installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        // Set default settings
        chrome.storage.sync.set({
            model: 'google/gemini-pro',
            temperature: 0.7,
            maxTokens: 2048
        });
        
        // Open options page
        chrome.runtime.openOptionsPage();
    }
}); 