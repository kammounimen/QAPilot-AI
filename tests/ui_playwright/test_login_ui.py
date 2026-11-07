import pytest
from playwright.sync_api import Page, expect


@pytest.mark.tc("TC-001-03")
def test_login_empty_fields_refused(page: Page, base_url):
    page.goto(f"{base_url}/admin")
    page.locator("#doLogin").click()
    # Connexion refusée : le formulaire reste affiché
    expect(page.locator("#doLogin")).to_be_visible()


@pytest.mark.tc("TC-001-01b")
def test_login_admin_success(page: Page, base_url):
    page.goto(f"{base_url}/admin")
    page.locator("#username").fill("admin")
    page.locator("#password").fill("password")
    page.locator("#doLogin").click()
    # Connexion réussie : le formulaire de login disparaît
    expect(page.locator("#doLogin")).to_be_hidden()


@pytest.mark.tc("TC-001-02b")
def test_login_wrong_password_refused(page: Page, base_url):
    page.goto(f"{base_url}/admin")
    page.locator("#username").fill("admin")
    page.locator("#password").fill("mauvais-mot-de-passe")
    page.locator("#doLogin").click()
    expect(page.locator("#doLogin")).to_be_visible()
