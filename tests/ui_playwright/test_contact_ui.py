import pytest
from playwright.sync_api import Page, expect


def fill_contact(page: Page, base_url: str, name, email, phone, subject, message):
    page.goto(f"{base_url}/#contact")
    page.get_by_test_id("ContactName").fill(name)
    if email:
        page.get_by_test_id("ContactEmail").fill(email)
    page.get_by_test_id("ContactPhone").fill(phone)
    page.get_by_test_id("ContactSubject").fill(subject)
    page.get_by_test_id("ContactDescription").fill(message)
    page.get_by_role("button", name="Submit").click()


@pytest.mark.tc("TC-008-01")
def test_contact_valid_message_accepted(page: Page, base_url):
    fill_contact(
        page,
        base_url,
        "Jean Dupont",
        "jean.dupont@example.com",
        "01234567890",
        "Question sur une chambre",
        "Bonjour, je voudrais des informations sur les chambres disponibles.",
    )
    expect(page.get_by_text("Thanks for getting in touch Jean Dupont!")).to_be_visible(
        timeout=10000
    )
    expect(page.get_by_text("Question sur une chambre")).to_be_visible()


@pytest.mark.tc("TC-008-02")
def test_contact_empty_email_refused(page: Page, base_url):
    fill_contact(
        page,
        base_url,
        "Jean Dupont",
        "",
        "01234567890",
        "Question sur une chambre",
        "Bonjour, je voudrais des informations sur les chambres disponibles.",
    )
    expect(page.get_by_text("Email may not be blank")).to_be_visible(timeout=10000)
    expect(page.get_by_text("Thanks for getting in touch")).to_have_count(0)
