import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Agentic AI extension is now active');

    const disposable = vscode.commands.registerCommand('agentic-ai.start', () => {
        // Create and show a new webview
        const panel = vscode.window.createWebviewPanel(
            'agenticAI', // Identifies the type of the webview
            'Agentic AI', // Title of the panel displayed to the user
            vscode.ViewColumn.One, // Editor column to show the new webview panel in
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        // Set initial HTML content
        panel.webview.html = getWebviewContent();
    });

    context.subscriptions.push(disposable);
}

function getWebviewContent() {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agentic AI</title>
    </head>
    <body>
        <h1>Agentic AI</h1>
        <p>Welcome to Agentic AI - Your AI-powered development assistant</p>
    </body>
    </html>`;
}

export function deactivate() {} 