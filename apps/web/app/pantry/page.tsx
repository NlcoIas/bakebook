"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, type PantryItem } from "@/lib/api";
import { SectionLabel } from "@/components/shared/SectionLabel";

async function createPantryItem(data: Record<string, unknown>): Promise<PantryItem> {
  const res = await fetch("/api/v1/pantry", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

async function updatePantryItem(id: string, data: Record<string, unknown>): Promise<PantryItem> {
  const res = await fetch(`/api/v1/pantry/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export default function PantryPage() {
  const queryClient = useQueryClient();
  const { data: items, isLoading } = useQuery({
    queryKey: ["pantry"],
    queryFn: () => api.pantry.list(),
  });

  const [showAdd, setShowAdd] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [costPerKg, setCostPerKg] = useState("");
  const [nutritionRef, setNutritionRef] = useState("");
  const [defaultRole, setDefaultRole] = useState("");

  const resetForm = () => {
    setName("");
    setCostPerKg("");
    setNutritionRef("");
    setDefaultRole("");
    setShowAdd(false);
    setEditId(null);
  };

  const startEdit = (item: PantryItem) => {
    setEditId(item.id);
    setName(item.name);
    setCostPerKg(item.costPerKg != null ? String(item.costPerKg) : "");
    setNutritionRef(item.nutritionRef ?? "");
    setDefaultRole(item.defaultRole ?? "");
    setShowAdd(true);
  };

  const saveMutation = useMutation({
    mutationFn: () => {
      const data = {
        name,
        costPerKg: costPerKg ? Number(costPerKg) : null,
        nutritionRef: nutritionRef || null,
        defaultRole: defaultRole || null,
      };
      return editId ? updatePantryItem(editId, data) : createPantryItem(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
      resetForm();
    },
  });

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      <h1
        className="font-display font-[350] text-[28px] tracking-[-0.02em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        Pantry
      </h1>

      <SectionLabel>{items?.length ?? 0} items</SectionLabel>

      {isLoading ? (
        <p className="mt-6 text-center font-mono text-[11px] tracking-[0.14em] uppercase text-ink-faint">Loading...</p>
      ) : (
        <div className="mt-3 flex flex-col">
          {items?.map((item, i) => (
            <button
              type="button"
              key={item.id}
              onClick={() => startEdit(item)}
              className={`flex items-center justify-between py-2.5 text-left ${
                i < (items?.length ?? 0) - 1 ? "border-b border-dashed border-rule/50" : ""
              }`}
            >
              <span className="font-display text-[14.5px] text-ink" style={{ fontVariationSettings: '"opsz" 24' }}>
                {item.name}
              </span>
              <span className="font-mono text-[11px] text-ink-faint">
                {item.costPerKg != null ? `CHF ${item.costPerKg}/kg` : "—"}
              </span>
            </button>
          ))}
        </div>
      )}

      {!showAdd ? (
        <button
          type="button"
          onClick={() => { resetForm(); setShowAdd(true); }}
          className="mt-4 w-full py-3 font-mono text-[10px] tracking-[0.18em] uppercase border border-rule text-ink-faint rounded-pill hover:border-ink-faint"
        >
          + Add item
        </button>
      ) : (
        <div className="mt-4 border border-rule rounded-card p-4 bg-paper">
          <p className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint mb-2">
            {editId ? "Edit item" : "New item"}
          </p>
          <div className="flex flex-col gap-2">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Name"
              className="px-3 py-2 bg-cream-deep border border-rule rounded-lg font-display text-[14px] focus:outline-none focus:ring-1 focus:ring-amber"
              style={{ fontVariationSettings: '"opsz" 24' }}
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                value={costPerKg}
                onChange={(e) => setCostPerKg(e.target.value)}
                placeholder="Cost/kg (CHF)"
                type="number"
                inputMode="decimal"
                className="px-3 py-2 bg-cream-deep border border-rule rounded-lg font-mono text-[13px] focus:outline-none focus:ring-1 focus:ring-amber"
              />
              <input
                value={defaultRole}
                onChange={(e) => setDefaultRole(e.target.value)}
                placeholder="Default role"
                className="px-3 py-2 bg-cream-deep border border-rule rounded-lg font-mono text-[13px] focus:outline-none focus:ring-1 focus:ring-amber"
              />
            </div>
            <input
              value={nutritionRef}
              onChange={(e) => setNutritionRef(e.target.value)}
              placeholder="Nutrition ref (key in nutrition.json)"
              className="px-3 py-2 bg-cream-deep border border-rule rounded-lg font-mono text-[13px] focus:outline-none focus:ring-1 focus:ring-amber"
            />
          </div>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={resetForm}
              className="flex-1 py-2 font-mono text-[10px] tracking-[0.18em] uppercase border border-rule rounded-pill text-ink-faint"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => saveMutation.mutate()}
              disabled={!name || saveMutation.isPending}
              className="flex-1 py-2 font-mono text-[10px] tracking-[0.18em] uppercase bg-amber text-cream rounded-pill font-medium disabled:opacity-50"
            >
              {saveMutation.isPending ? "Saving..." : "Save"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
