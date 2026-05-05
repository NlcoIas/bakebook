const API_BASE = "/api/v1";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// --- Recipe types ---

export interface RecipeListItem {
  id: string;
  title: string;
  slug: string;
  category: string;
  summary: string | null;
  yields: string | null;
  servings: number;
  totalTimeMin: number | null;
  activeTimeMin: number | null;
  difficulty: number | null;
  equipment: string[];
  heroPhotoKey: string | null;
  versionNumber: number;
  createdAt: string;
  updatedAt: string;
}

export interface Ingredient {
  id: string;
  pantryItemId: string | null;
  ord: number;
  groupLabel: string | null;
  name: string;
  grams: number | null;
  unitDisplay: string | null;
  unitDisplayQty: number | null;
  role: string | null;
  leavenFlourPct: number;
  costOverridePerKg: number | null;
  nutritionOverride: Record<string, number> | null;
  notes: string | null;
  optional: boolean;
}

export interface Step {
  id: string;
  ord: number;
  title: string;
  body: string;
  timerSeconds: number | null;
  minSeconds: number | null;
  maxSeconds: number | null;
  targetTempC: number | null;
  tempKind: string | null;
}

export interface Macros {
  kcal: number;
  protein: number;
  fat: number;
  carbs: number;
  sugar: number;
  fiber: number;
  salt: number;
}

export interface RecipeNutrition {
  perRecipe: Macros;
  perServing: Macros;
  per100g: Macros | null;
  dailyValuePct: { kcal: number; protein: number; fat: number; carbs: number } | null;
  warnings: string[];
}

export interface RecipeCost {
  totalCost: number;
  perServingCost: number;
  currency: string;
  topContributors: { name: string; cost: number }[];
  warnings: string[];
}

export interface RecipeRatios {
  flourTotalG: number;
  hydration: number;
  hydrationWithDairy: number;
  salt: number;
  sugar: number;
  fat: number;
  prefermentedFlour: number;
  inoculationRate: number;
}

export interface Recipe extends RecipeListItem {
  versionOfId: string | null;
  parentRecipeId: string | null;
  servingG: number | null;
  notes: string | null;
  source: string | null;
  targetDoughG: number | null;
  ingredients: Ingredient[];
  steps: Step[];
  nutrition: RecipeNutrition | null;
  cost: RecipeCost | null;
  ratios: RecipeRatios | null;
}

// --- API functions ---

export const api = {
  recipes: {
    list: (params?: { category?: string; q?: string }) => {
      const search = new URLSearchParams();
      if (params?.category) search.set("category", params.category);
      if (params?.q) search.set("q", params.q);
      const qs = search.toString();
      return fetchJson<RecipeListItem[]>(`/recipes${qs ? `?${qs}` : ""}`);
    },
    get: (id: string) => fetchJson<Recipe>(`/recipes/${id}`),
    getBySlug: (slug: string) => fetchJson<Recipe>(`/recipes/by-slug/${slug}`),
  },
  bakes: {
    list: () => fetchJson<BakeListItem[]>("/bakes"),
    get: (id: string) => fetchJson<BakeDetail>(`/bakes/${id}`),
    start: (data: {
      recipeId: string;
      scaleMultiplier?: number;
      kitchenTempC?: number;
      kitchenHumidity?: number;
      flourBrand?: string;
    }) => fetchJson<BakeDetail>("/bakes", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: Record<string, unknown>) =>
      fetchJson<BakeDetail>(`/bakes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    addTweak: (bakeId: string, data: { change: string; reason?: string; applyNextTime?: boolean }) =>
      fetchJson<BakeTweak>(`/bakes/${bakeId}/tweaks`, { method: "POST", body: JSON.stringify(data) }),
    requestPhotoUpload: (bakeId: string) =>
      fetchJson<{ r2Key: string; presignedUrl: string; expiresIn: number }>(`/bakes/${bakeId}/photos?filename=photo.jpg`, { method: "POST" }),
    confirmPhoto: (bakeId: string, r2Key: string, kind?: string, stepOrd?: number) => {
      const params = new URLSearchParams();
      if (kind) params.set("kind", kind);
      if (stepOrd != null) params.set("step_ord", String(stepOrd));
      const qs = params.toString();
      return fetchJson<BakePhoto>(`/bakes/${bakeId}/photos/${r2Key}/confirm${qs ? `?${qs}` : ""}`, { method: "POST" });
    },
  },
  pantry: {
    list: () => fetchJson<PantryItem[]>("/pantry"),
    nutritionTable: () => fetchJson<Record<string, Record<string, number>>>("/pantry/nutrition-table"),
  },
};

// --- Bake types ---

export interface BakeListItem {
  id: string;
  recipeId: string;
  recipeTitle: string | null;
  recipeCategory: string | null;
  startedAt: string;
  finishedAt: string | null;
  status: string;
  rating: number | null;
  outcome: string | null;
}

export interface BakePhoto {
  id: string;
  bakeId: string;
  r2Key: string;
  url: string | null;
  caption: string | null;
  kind: string | null;
  stepOrd: number | null;
  takenAt: string;
}

export interface BakeTweak {
  id: string;
  bakeId: string;
  change: string;
  reason: string | null;
  ingredientId: string | null;
  stepId: string | null;
  applyNextTime: boolean;
  resolvedInRecipeId: string | null;
}

export interface BakeDetail {
  id: string;
  recipeId: string;
  startedAt: string;
  finishedAt: string | null;
  status: string;
  currentStep: number;
  scaleMultiplier: number;
  kitchenTempC: number | null;
  kitchenHumidity: number | null;
  flourBrand: string | null;
  rating: number | null;
  outcome: string | null;
  startWeightG: number | null;
  finalWeightG: number | null;
  riseHeightCm: number | null;
  internalTempC: number | null;
  crumbScore: number | null;
  crustScore: number | null;
  notes: string | null;
  waterLossPct: number | null;
  photos: BakePhoto[];
  tweaks: BakeTweak[];
  recipeTitle: string | null;
  recipeCategory: string | null;
}

export interface PantryItem {
  id: string;
  name: string;
  costPerKg: number | null;
  costCurrency: string;
  nutritionRef: string | null;
  defaultRole: string | null;
  createdAt: string;
  updatedAt: string;
}
