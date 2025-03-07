"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.run = void 0;
const path = require("path");
const Mocha = require("mocha");
const glob_1 = require("glob");
function run() {
    // Create the mocha test
    const mocha = new Mocha({
        ui: 'tdd',
        color: true
    });
    const testsRoot = path.resolve(__dirname, '..');
    return new Promise((resolve, reject) => {
        (0, glob_1.glob)('**/**.test.js', { cwd: testsRoot }).then(files => {
            try {
                // Add files to the test suite
                files.forEach(f => mocha.addFile(path.resolve(testsRoot, f)));
                // Run the mocha test
                mocha.run(failures => {
                    if (failures > 0) {
                        reject(new Error(`${failures} tests failed.`));
                    }
                    else {
                        resolve();
                    }
                });
            }
            catch (err) {
                console.error(err);
                reject(err);
            }
        }).catch(reject);
    });
}
exports.run = run;
//# sourceMappingURL=index.js.map