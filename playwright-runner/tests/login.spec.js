const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');

test.describe('Practice Test Automation - Login Tests', () => {
    let loginPage;

    test.beforeEach(async ({ page }) => {
        loginPage = new LoginPage(page);
        await loginPage.navigate();
    });

    test('TC_001 | Verify successful login with valid credentials', async ({ page }) => {
        await loginPage.login('student', 'Password123');
        
        // Assert URL contains the expected success substring
        await expect(page).toHaveURL(/.*\/logged-in-successfully\//);
        
        // Assert successful login header or content is visible
        const successHeader = page.locator('h1.post-title');
        await expect(successHeader).toBeVisible();
        await expect(successHeader).toHaveText('Logged In Successfully');
    });

    test('TC_002 | Verify password characters are masked during input', async () => {
        await expect(loginPage.passwordInput).toHaveAttribute('type', 'password');
    });

    test('TC_003 | Verify keyboard navigation and submission on login form', async ({ page }) => {
    await loginPage.usernameInput.focus();
    await page.keyboard.type('student');
    await page.keyboard.press('Tab');
    await page.keyboard.type('Password123');

    await loginPage.submitButton.click();

    await expect(page).toHaveURL(/.*\/logged-in-successfully\//, { timeout: 10000 });
    const successHeader = page.locator('h1.post-title');
    await expect(successHeader).toBeVisible();
    await expect(successHeader).toHaveText('Logged In Successfully');
});

    test('TC_004 | Verify error message with invalid username and valid password', async () => {
        await loginPage.login('incorrectUser', 'Password123');
        
        // Assert standard username error validation message
        await expect(loginPage.errorMessage).toBeVisible();
        await expect(loginPage.errorMessage).toContainText('Your username is invalid!');
    });

    test('TC_005 | Verify error message with valid username and invalid password', async () => {
        await loginPage.login('student', 'incorrectPassword');
        
        // Assert standard password error validation message
        await expect(loginPage.errorMessage).toBeVisible();
        await expect(loginPage.errorMessage).toContainText('Your password is invalid!');
    });

    test('TC_006 | Verify validation error when submitting with empty fields', async () => {
        // Submit empty fields directly
        await loginPage.submitButton.click();
        
        // Assert error is displayed for empty submission
        await expect(loginPage.errorMessage).toBeVisible();
        await expect(loginPage.errorMessage).toContainText('Your username is invalid!');
    });

    test('TC_007 | Verify login fails when username case sensitivity is modified', async () => {
        await loginPage.login('STUDENT', 'Password123');
        
        // Assert login fails due to case-sensitivity violation
        await expect(loginPage.errorMessage).toBeVisible();
        await expect(loginPage.errorMessage).toContainText('Your username is invalid!');
    });

    test('TC_008 | Verify login input fields handle SQL injection attempts safely', async () => {
        await loginPage.login("admin' OR '1'='1", "password' OR '1'='1");
        
        // Assert system safely rejects injection payload with standard error validation
        await expect(loginPage.errorMessage).toBeVisible();
        await expect(loginPage.errorMessage).toContainText('Your username is invalid!');
    });
});