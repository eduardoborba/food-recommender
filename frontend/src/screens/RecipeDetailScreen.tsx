import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { getRecipe } from '../api';
import type { RecipeDetail as RecipeDetailType } from '../types';

interface Props {
  recipeId: number;
  onBack: () => void;
}

const NUTRITION_LABELS: Record<string, string> = {
  calories: 'Calories',
  total_fat: 'Fat',
  sugar: 'Sugar',
  sodium: 'Sodium',
  protein: 'Protein',
  saturated_fat: 'Sat. fat',
  carbs: 'Carbs',
};

export default function RecipeDetailScreen({ recipeId, onBack }: Props) {
  const [recipe, setRecipe] = useState<RecipeDetailType | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getRecipe(recipeId)
      .then((r) => {
        if (!cancelled) setRecipe(r);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load');
      });
    return () => {
      cancelled = true;
    };
  }, [recipeId]);

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error}</Text>
        <Pressable onPress={onBack} style={styles.backButton}>
          <Text style={styles.backText}>Go back</Text>
        </Pressable>
      </View>
    );
  }

  if (!recipe) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Pressable onPress={onBack} hitSlop={12}>
        <Text style={styles.backText}>&larr; Back</Text>
      </Pressable>

      {recipe.image_url && (
        <Image source={{ uri: recipe.image_url }} style={styles.hero} />
      )}

      <Text style={styles.title}>{recipe.name}</Text>

      <View style={styles.metaRow}>
        {recipe.minutes != null && <Text>{recipe.minutes} min</Text>}
      </View>

      {recipe.tags && recipe.tags.length > 0 && (
        <View style={styles.tagWrap}>
          {recipe.tags.slice(0, 10).map((tag) => (
            <View key={tag} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
        </View>
      )}

      {recipe.description && (
        <Text style={styles.description}>{recipe.description}</Text>
      )}

      {recipe.nutrition && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Nutrition</Text>
          <View style={styles.nutritionGrid}>
            {Object.entries(NUTRITION_LABELS)
              .filter(([key]) => recipe.nutrition?.[key] != null)
              .map(([key, label]) => (
                <View key={key} style={styles.nutritionItem}>
                  <Text style={styles.nutritionValue}>{recipe.nutrition?.[key]}</Text>
                  <Text style={styles.nutritionLabel}>{label}</Text>
                </View>
              ))}
          </View>
        </View>
      )}

      {recipe.steps && recipe.steps.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Steps</Text>
          {recipe.steps.map((step, i) => (
            <Text key={i} style={styles.step}>
              {i + 1}. {step}
            </Text>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 16,
    paddingTop: 60,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
    backgroundColor: '#fff',
  },
  backText: {
    color: '#e8590c',
    fontWeight: '600',
    marginBottom: 12,
  },
  error: {
    color: '#c92a2a',
  },
  backButton: {
    padding: 8,
  },
  hero: {
    width: '100%',
    height: 220,
    borderRadius: 12,
    marginBottom: 16,
    backgroundColor: '#eee',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 8,
  },
  metaRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
    color: '#555',
  },
  tagWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 16,
  },
  tag: {
    backgroundColor: '#f1f3f5',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  tagText: {
    fontSize: 12,
    color: '#495057',
  },
  description: {
    color: '#444',
    lineHeight: 20,
    marginBottom: 16,
  },
  section: {
    marginTop: 8,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  nutritionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  nutritionItem: {
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    minWidth: 80,
  },
  nutritionValue: {
    fontWeight: '700',
  },
  nutritionLabel: {
    fontSize: 11,
    color: '#666',
  },
  step: {
    lineHeight: 22,
    marginBottom: 8,
    color: '#333',
  },
});
