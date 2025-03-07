"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const assert = require("assert");
const vscode = require("vscode");
suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('agentic-ai'));
    });
    test('Should activate', async () => {
        const ext = vscode.extensions.getExtension('agentic-ai');
        await ext?.activate();
        assert.ok(true);
    });
});
//# sourceMappingURL=extension.test.js.map