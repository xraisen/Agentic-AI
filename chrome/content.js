// Create overlay for displaying results
const overlay = document.createElement('div');
overlay.id = 'agentic-ai-overlay';
overlay.style.display = 'none';
document.body.appendChild(overlay);

// Handle messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'analyze-page') {
        analyzePage();
    } else if (message.type === 'analyze-selection') {
        analyzeSelection();
    }
});

// Analyze entire page
async function analyzePage() {
    try {
        // Get page content
        const content = {
            title: document.title,
            url: window.location.href,
            content: document.body.innerText
        };
        
        // Send request to background script
        const response = await chrome.runtime.sendMessage({
            type: 'analyze',
            data: {
                model: 'google/gemini-pro',
                prompt: `Please analyze this webpage:\n\nTitle: ${content.title}\nURL: ${content.url}\n\nContent:\n${content.content}`,
                temperature: 0.7,
                maxTokens: 2048
            }
        });
        
        // Show result
        showResult(response.result);
        
    } catch (error) {
        console.error('Error analyzing page:', error);
        showError(error.message);
    }
}

// Analyze selected text
async function analyzeSelection() {
    try {
        const selection = window.getSelection();
        if (!selection.toString()) {
            showError('No text selected');
            return;
        }
        
        // Get selected text and context
        const range = selection.getRangeAt(0);
        const selectedText = range.toString();
        const context = getContext(range);
        
        // Send request to background script
        const response = await chrome.runtime.sendMessage({
            type: 'analyze',
            data: {
                model: 'google/gemini-pro',
                prompt: `Please analyze this text selection:\n\nContext:\n${context}\n\nSelected Text:\n${selectedText}`,
                temperature: 0.7,
                maxTokens: 2048
            }
        });
        
        // Show result
        showResult(response.result);
        
    } catch (error) {
        console.error('Error analyzing selection:', error);
        showError(error.message);
    }
}

// Get context around selection
function getContext(range) {
    const preCaretRange = range.cloneRange();
    const postCaretRange = range.cloneRange();
    
    // Get text before selection
    preCaretRange.selectNodeContents(range.startContainer.parentElement);
    preCaretRange.setEnd(range.startContainer, range.startOffset);
    const beforeText = preCaretRange.toString();
    
    // Get text after selection
    postCaretRange.selectNodeContents(range.endContainer.parentElement);
    postCaretRange.setStart(range.endContainer, range.endOffset);
    const afterText = postCaretRange.toString();
    
    return `${beforeText}\n${afterText}`;
}

// Show result in overlay
function showResult(result) {
    overlay.innerHTML = `
        <div class="agentic-ai-result">
            <div class="agentic-ai-header">
                <h3>Analysis Result</h3>
                <button class="agentic-ai-close">&times;</button>
            </div>
            <div class="agentic-ai-content">
                ${result.replace(/\n/g, '<br>')}
            </div>
        </div>
    `;
    
    overlay.style.display = 'block';
    
    // Add close button handler
    overlay.querySelector('.agentic-ai-close').addEventListener('click', () => {
        overlay.style.display = 'none';
    });
}

// Show error in overlay
function showError(message) {
    overlay.innerHTML = `
        <div class="agentic-ai-error">
            <div class="agentic-ai-header">
                <h3>Error</h3>
                <button class="agentic-ai-close">&times;</button>
            </div>
            <div class="agentic-ai-content">
                ${message}
            </div>
        </div>
    `;
    
    overlay.style.display = 'block';
    
    // Add close button handler
    overlay.querySelector('.agentic-ai-close').addEventListener('click', () => {
        overlay.style.display = 'none';
    });
} 