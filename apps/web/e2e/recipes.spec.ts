import { test, expect } from "@playwright/test";

test.describe("Recipe list", () => {
  test("shows all 8 recipes", async ({ page }) => {
    await page.goto("/recipes");
    await page.waitForSelector("a[href^='/recipes/']");
    const cards = page.locator("a[href^='/recipes/']");
    await expect(cards).toHaveCount(8);

    await page.screenshot({
      path: "../../test-results/screenshots/M1/recipe-list.png",
      fullPage: true,
    });
  });
});

test.describe("Cornbread recipe", () => {
  test("has nutrition and cost but no ratios", async ({ page }) => {
    // Navigate to recipes list first to get the cornbread ID
    await page.goto("/recipes");
    await page.waitForSelector("a[href^='/recipes/']");

    // Click on the cornbread card
    await page.locator("text=Buttermilk Cornbread").click();
    await page.waitForSelector("h1");

    // Should have nutrition panel with non-zero kcal
    const nutritionPanel = page.locator("text=Nutrition").first();
    await expect(nutritionPanel).toBeVisible();

    // Check for macro values - the 4 macro columns should be visible
    const macroLabels = page.locator("text=/^(carbs|fat|protein|fiber)$/i");
    await expect(macroLabels).toHaveCount(4);

    // Should have cost panel
    const costPanel = page.locator("text=Cost").first();
    await expect(costPanel).toBeVisible();

    // Cost should show CHF
    await expect(page.locator("text=CHF").first()).toBeVisible();

    // Should NOT have ratios panel
    const ratiosPanel = page.locator("text=Baker's ratios");
    await expect(ratiosPanel).toHaveCount(0);

    await page.screenshot({
      path: "../../test-results/screenshots/M1/cornbread-detail.png",
      fullPage: true,
    });
  });
});

test.describe("Bread recipe with ratios", () => {
  test("Butterzopf has ratios panel", async ({ page }) => {
    await page.goto("/recipes");
    await page.waitForSelector("a[href^='/recipes/']");
    await page.locator("text=Swiss Butterzopf").click();
    await page.waitForSelector("h1");

    // Should have ratios panel
    const ratiosPanel = page.locator("text=Baker's ratios");
    await expect(ratiosPanel).toBeVisible();

    // Should have hydration row
    await expect(page.locator("text=Hydration").first()).toBeVisible();

    await page.screenshot({
      path: "../../test-results/screenshots/M1/butterzopf-detail.png",
      fullPage: true,
    });
  });
});
