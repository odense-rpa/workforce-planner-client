import os

from workforce_planner_client.selectors import WorkforcePlannerSelectors
from playwright.sync_api import (
    sync_playwright,
    Playwright,
    Page,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)


def _env_to_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class WorkforcePlannerClient:
    def __init__(
        self, base_url: str, username: str, password: str, headless: bool | None = None
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headless = (
            _env_to_bool("PLAYWRIGHT_HEADLESS", False) if headless is None else headless
        )
        self._playwright: Playwright | None = None
        self._browser = None
        self._context = None
        self._page: Page | None = None
        self._login()

    def _ensure_browser(self) -> None:
        if self._page is not None:
            return

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
        )
        self._context = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            accept_downloads=False,
            ignore_https_errors=True,
            locale="da-DK",
            http_credentials={"username": self.username, "password": self.password},
        )
        self._page = self._context.new_page()

    def _login(self):
        self._ensure_browser()
        if self._page is None:
            return None

        try:
            self._page.goto(self.base_url, wait_until="domcontentloaded")
            self._page.locator(
                WorkforcePlannerSelectors.LOGIN_PANEL_FIRST_SUCCESS_BUTTON
            ).click()
            self._page.locator(WorkforcePlannerSelectors.ODENSE_IDP_BUTTON).click()
            self._page.wait_for_selector(WorkforcePlannerSelectors.MAIN_MENU_BRAND_LINK)
            return self._page
        except PlaywrightError:
            self.close()
            raise

    def close(self) -> None:
        if self._context is not None:
            self._context.close()
            self._context = None

        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

        self._page = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def handle_dialog(self, dialog, dialog_count):
        dialog_count += 1

        if dialog_count == 1:
            # first confirm: always accept
            print("First dialog accepted:", dialog.message)
            dialog.accept()

        elif dialog_count == 2:
            # second dialog: accept but fail test
            dialog.accept()
            raise ValueError("Online ressourcer er tilknyttet. Kan ikke slette.")

        else:
            # anything beyond is also suspicious
            dialog.accept()
            raise ValueError(f"Ekstra uventet dialog #{dialog_count}: {dialog.message}")

    def slet_personressource(self, email: str) -> None:
        dialog_count = 0
        if self._page is None:
            raise ValueError("Side kunne ikke åbnes.")

        self._page.goto(
            f"{self.base_url}Planner/administration/personresources.aspx",
            wait_until="domcontentloaded",
        )
        self._page.locator(WorkforcePlannerSelectors.SEARCH_DEPARTMENTS_BUTTON).fill(
            email
        )
        self._page.locator(WorkforcePlannerSelectors.SEARCH_BUTTON).click()
        self._page.wait_for_timeout(5000)

        if self._page.locator(
            WorkforcePlannerSelectors.EMPTY_GRIDVIEW_DIV
        ).is_visible():
            raise ValueError("Bruger ikke fundet under Person ressourcer")

        table = self._page.locator(
            WorkforcePlannerSelectors.PERSONRESOURCE_RESULTS_TABLE
        )
        if table.count() == 0:
            raise ValueError("Kunne ikke finde resultat tabel.")

        result_rows = table.locator("tbody tr")
        row_count = result_rows.count()

        if row_count == 0:
            raise ValueError("Bruger ikke fundet under Person ressourcer")
        if row_count > 1:
            raise ValueError(
                f"Flere brugere fundet med email {email} under Person ressourcer"
            )
        self._page.on("dialog", lambda dialog: self.handle_dialog(dialog, dialog_count))
        self._page.locator(WorkforcePlannerSelectors.DELETE_BUTTON).click()
        

    def deaktiver_bruger(self, email: str) -> None:
        if self._page is None:
            return None

        self._page.goto(
            f"{self.base_url}Planner/app/administration/users",
            wait_until="domcontentloaded",
        )
        self._page.locator(WorkforcePlannerSelectors.USERS_SEARCH_INPUT).fill(email)
        self._page.keyboard.press("Enter")

        try:
            self._page.locator(
                f"{WorkforcePlannerSelectors.USERS_RESULTS_TABLE} tbody tr"
            ).first.wait_for(state="visible", timeout=5000)
        except PlaywrightTimeoutError:
            raise LookupError("Bruger ikke fundet under Brugere")

        table = self._page.locator(WorkforcePlannerSelectors.USERS_RESULTS_TABLE)
        if table.count() == 0:
            raise LookupError("Bruger ikke fundet under Brugere")

        result_rows = table.locator("tbody tr")
        row_count = result_rows.count()

        if row_count == 0:
            raise LookupError("Bruger ikke fundet under Brugere")
        if row_count > 1:
            raise ValueError(f"Flere brugere fundet med email {email} under Brugere")

        result_rows.nth(0).locator(
            WorkforcePlannerSelectors.USERS_RESULT_ITEM_BUTTON
        ).click()
        self._page.get_by_role("checkbox", name="Aktiv", exact=True).uncheck()
        self._page.locator("button.button-success", has_text="Gem").click()
