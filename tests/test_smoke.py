from playwright.sync_api import Page, expect


def test_homepage_loads(page: Page, base_url):
    page.goto(base_url)
    expect(page.locator("body")).to_be_visible()


def test_admin_page_loads(page: Page, base_url):
    page.goto(f"{base_url}/admin")
    expect(page.locator("body")).to_be_visible()
