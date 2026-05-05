import { test, expect } from "@playwright/test";

test.describe("Active bake flow", () => {
  test("start bake shows kitchen mode", async ({ page }) => {
    // Go to cornbread recipe
    await page.goto("/recipes");
    await page.waitForSelector("a[href^='/recipes/']");
    await page.locator("text=Buttermilk Cornbread").click();
    await page.waitForSelector("h1");

    // Click start bake
    await page.locator("text=Start bake").click();

    // Should see the pre-bake modal
    await expect(page.locator("text=Quick context")).toBeVisible();

    // Skip the modal
    await page.getByRole("button", { name: "Skip" }).click();

    // Should be in kitchen mode (dark background)
    await page.waitForSelector("text=Buttermilk Cornbread");

    // Should show step progress and navigation
    await expect(page.locator("text=Next step")).toBeVisible();

    await page.screenshot({
      path: "../../test-results/screenshots/M2/active-bake.png",
      fullPage: true,
    });
  });
});

test.describe("Reflection screen", () => {
  test("shows measurement fields", async ({ page }) => {
    // Start a bake via API first
    const startRes = await page.request.post("http://localhost:8001/api/v1/bakes", {
      data: {
        recipeId: await getFirstRecipeId(page),
      },
    });
    const bake = await startRes.json();

    // Go to the reflection screen
    await page.goto(`/bakes/${bake.id}`);
    await page.waitForSelector("text=Bake reflection");

    // Should show measurement fields
    await expect(page.locator("text=Rise height")).toBeVisible();
    await expect(page.locator("text=Internal temp")).toBeVisible();
    await expect(page.locator("text=Weight before")).toBeVisible();
    await expect(page.locator("text=Weight after")).toBeVisible();

    // Should show rating stars
    await expect(page.getByText("Rating", { exact: true })).toBeVisible();

    // Should show outcome chips
    await expect(page.locator("text=Okay")).toBeVisible();

    await page.screenshot({
      path: "../../test-results/screenshots/M2/reflection.png",
      fullPage: true,
    });
  });
});

async function getFirstRecipeId(page: any): Promise<string> {
  const res = await page.request.get("http://localhost:8001/api/v1/recipes");
  const recipes = await res.json();
  return recipes[0].id;
}
