const { expect } = require('@playwright/test');

class LoginPage {
    /**
     * @param {import('@playwright/test').Page} page
     */
    constructor(page) {
        this.page = page;
        this.usernameInput = page.locator('#username');
        this.passwordInput = page.locator('#password');
        this.submitButton = page.locator('#submit');
        this.errorMessage = page.locator('#error');
    }

    async navigate() {
        await this.page.goto('https://practicetestautomation.com/practice-test-login/');
    }

    async login(username, password) {
        if (username !== null) {
            await this.usernameInput.fill(username);
        }
        if (password !== null) {
            await this.passwordInput.fill(password);
        }
        await this.submitButton.click();
    }
}

module.exports = { LoginPage };