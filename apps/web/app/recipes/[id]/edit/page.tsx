"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { RecipeEditor } from "@/components/recipe/RecipeEditor";

export default function EditRecipePage() {
  const params = useParams();
  const id = params.id as string;

  const { data: recipe, isLoading } = useQuery({
    queryKey: ["recipe", id],
    queryFn: () => api.recipes.get(id),
  });

  if (isLoading || !recipe) {
    return (
      <div className="px-4 pt-12 text-center">
        <p className="font-mono text-[11px] tracking-[0.14em] uppercase text-ink-faint">Loading...</p>
      </div>
    );
  }

  return <RecipeEditor recipe={recipe} />;
}
