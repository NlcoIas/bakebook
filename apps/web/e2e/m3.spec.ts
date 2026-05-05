import { test, expect } from "@playwright/test";

test.describe("M3 features", () => {
  test("ready-by panel shows on recipe detail", async ({ page }) => {
    await page.goto("/recipes");
    await page.waitForSelector("a[href^='/recipes/']");
    await page.locator("text=No-Knead Dutch Oven Loaf").click();
    await page.waitForSelector("h1");

    // Should have the ready-by panel
    await expect(page.locator("text=Ready by").first()).toBeVisible();
    // Wait for the API to respond with start time
    await expect(page.locator("text=Start at").first()).toBeVisible({ timeout: 10000 });

    await page.screenshot({
      path: "../../test-results/screenshots/M3/recipe-with-readyby.png",
      fullPage: true,
    });
  });

  test("allergen badges show on bread recipe", async ({ page }) => {
    await page.goto("/recipes");
    await page.waitForSelector("a[href^='/recipes/']");
    await page.locator("text=Swiss Butterzopf").click();
    await page.waitForSelector("h1");

    // Butterzopf should have gluten, dairy, egg allergens
    await expect(page.locator("text=gluten").first()).toBeVisible();

    await page.screenshot({
      path: "../../test-results/screenshots/M3/butterzopf-allergens.png",
      fullPage: false,
    });
  });
});
