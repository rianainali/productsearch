import { test, expect } from "@playwright/test";

test.describe("ProductSearch E2E", () => {
  test("homepage loads with search tab", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toHaveText("ProductSearch");
    await expect(page.getByText("Search products")).toBeVisible();
  });

  test("admin tab shows catalog with seed products", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Admin" }).click();
    await expect(page.getByText("Catalog")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Add Product" })).toBeVisible();
    // Wait for products to load
    await expect(page.getByText(/\d+ products/)).toBeVisible();
  });

  test("add product via admin form", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Admin" }).click();

    // Fill form
    await page.getByPlaceholder("Product name").fill("E2E Test Speaker");
    await page
      .getByPlaceholder("Describe the product")
      .fill("A test speaker created by Playwright");
    await page
      .getByPlaceholder("bluetooth, wireless, waterproof")
      .fill("test, e2e, speaker");
    await page.getByPlaceholder("0.00").fill("42.99");

    // Submit
    await page.getByRole("button", { name: "Add Product" }).click();

    // Wait for success message
    await expect(page.getByText("Product added successfully!")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("search for a product and get results", async ({ page }) => {
    await page.goto("/");

    // Type search query
    await page
      .getByPlaceholder("Search for products...")
      .fill("wireless headphones");
    await page.getByRole("button", { name: "Send" }).click();

    // Wait for results to appear (product cards)
    await expect(page.getByText("Wireless Bluetooth Headphones")).toBeVisible({
      timeout: 30_000,
    });
  });
});
