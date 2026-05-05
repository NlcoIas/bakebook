import { test, expect } from "@playwright/test";

test("home page renders with design tokens", async ({ page }) => {
  await page.goto("/");

  // Verify Bakebook title is present
  const title = page.locator("h1");
  await expect(title).toBeVisible();
  await expect(title).toContainText("Bakebook");

  // Take screenshot for design comparison
  await page.screenshot({
    path: "../../test-results/screenshots/M0/home.png",
    fullPage: true,
  });
});
