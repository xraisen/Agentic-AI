import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('agentic-ai'));
    });

    test('Should activate', async () => {
        const ext = vscode.extensions.getExtension('agentic-ai');
        await ext?.activate();
    });

    test('Should register all commands', async () => {
        const commands = await vscode.commands.getCommands();
        const agenticCommands = commands.filter(cmd => cmd.startsWith('agentic-ai.'));
        
        assert.strictEqual(agenticCommands.length, 3);
        assert.ok(agenticCommands.includes('agentic-ai.start'));
        assert.ok(agenticCommands.includes('agentic-ai.stop'));
        assert.ok(agenticCommands.includes('agentic-ai.clear'));
    });

    test('Should create config file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            assert.fail('No workspace folder found');
            return;
        }

        const configPath = path.join(workspaceFolders[0].uri.fsPath, 'config.json');
        
        // Clean up any existing config file
        if (fs.existsSync(configPath)) {
            fs.unlinkSync(configPath);
        }

        // Set test configuration
        await vscode.workspace.getConfiguration('agentic-ai').update('apiKey', 'test-api-key', true);
        await vscode.workspace.getConfiguration('agentic-ai').update('model', 'test-model', true);

        // Execute start command
        await vscode.commands.executeCommand('agentic-ai.start');

        // Verify config file was created
        assert.ok(fs.existsSync(configPath));

        // Verify config contents
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        assert.strictEqual(config.OPENROUTER_API_KEY, 'test-api-key');
        assert.strictEqual(config.MODEL, 'test-model');

        // Clean up
        fs.unlinkSync(configPath);
    });
}); 