import { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

import RecipeDetailScreen from './src/screens/RecipeDetailScreen';
import SearchScreen from './src/screens/SearchScreen';
import type { RecipeSummary } from './src/types';

export default function App() {
  const [selected, setSelected] = useState<RecipeSummary | null>(null);

  return (
    <View style={styles.container}>
      {selected ? (
        <RecipeDetailScreen
          recipeId={selected.id}
          onBack={() => setSelected(null)}
        />
      ) : (
        <SearchScreen onSelectRecipe={setSelected} />
      )}
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});
