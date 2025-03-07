import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

let agenticProcess: any = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('Agentic AI extension is now active!');

    let startCommand = vscode.commands.registerCommand('agentic-ai.start', async () => {
        try {
            const config = vscode.workspace.getConfiguration('agentic-ai');
            const apiKey = config.get('apiKey');
            const model = config.get('model');

            if (!apiKey) {
                vscode.window.showErrorMessage('Please set your OpenRouter API key in settings');
                return;
            }

            // Create config file
            const configPath = path.join(context.extensionPath, 'config.json');
            fs.writeFileSync(configPath, JSON.stringify({
                OPENROUTER_API_KEY: apiKey,
                SITE_URL: "https://agentic-ai.vercel.app/",
                SITE_NAME: "Agentic AI VS Code Extension",
                MODEL: model
            }, null, 2));

            // Start the Python process
            const pythonPath = vscode.workspace.getConfiguration('python').get('pythonPath') || 'python';
            const scriptPath = path.join(context.extensionPath, 'src', 'main.py');

            agenticProcess = spawn(pythonPath, [scriptPath], {
                stdio: 'pipe',
                shell: true
            });

            agenticProcess.stdout.on('data', (data: Buffer) => {
                vscode.window.showInformationMessage(`Agentic AI: ${data.toString()}`);
            });

            agenticProcess.stderr.on('data', (data: Buffer) => {
                vscode.window.showErrorMessage(`Agentic AI Error: ${data.toString()}`);
            });

            vscode.window.showInformationMessage('Agentic AI started successfully!');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start Agentic AI: ${error}`);
        }
    });

    let stopCommand = vscode.commands.registerCommand('agentic-ai.stop', () => {
        if (agenticProcess) {
            agenticProcess.kill();
            agenticProcess = null;
            vscode.window.showInformationMessage('Agentic AI stopped');
        }
    });

    let clearCommand = vscode.commands.registerCommand('agentic-ai.clear', () => {
        // Implement clear functionality
        vscode.window.showInformationMessage('Chat history cleared');
    });

    context.subscriptions.push(startCommand, stopCommand, clearCommand);
}

export function deactivate() {
    if (agenticProcess) {
        agenticProcess.kill();
        agenticProcess = null;
    }
} 