import React from "react";
import { View, FlatList, Text, StyleSheet, RefreshControl, ActivityIndicator } from "react-native";
import { useSignals } from "@/hooks/useSignals";
import SignalCard from "@/components/SignalCard";
import { colors, spacing, radius } from "@/lib/theme";

export default function AlertsScreen() {
  const { signals, loading, refetch } = useSignals({ min_confidence: 75 });

  const high = signals.filter((s) => (s.confidence ?? 0) >= 75);
  const sorted = [...high].sort((a, b) => (b.confidence ?? 0) - (a.confidence ?? 0));

  if (loading && sorted.length === 0) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.indigo} />
        <Text style={styles.sub}>Loading high-confidence alerts…</Text>
      </View>
    );
  }

  return (
    <FlatList
      style={{ flex: 1, backgroundColor: colors.bg }}
      contentContainerStyle={styles.content}
      data={sorted}
      keyExtractor={(s) => String(s.id)}
      renderItem={({ item }) => <SignalCard signal={item} />}
      refreshControl={
        <RefreshControl refreshing={loading} onRefresh={refetch} tintColor={colors.indigo} />
      }
      ListHeaderComponent={
        <View style={styles.banner}>
          <Text style={styles.bannerTitle}>🔥 High-Confidence Signals</Text>
          <Text style={styles.bannerSub}>Only signals with ≥ 75% confidence shown</Text>
        </View>
      }
      ListEmptyComponent={
        <View style={styles.centered}>
          <Text style={{ fontSize: 40, marginBottom: spacing.md }}>🔔</Text>
          <Text style={styles.emptyTitle}>No high-confidence alerts</Text>
          <Text style={styles.sub}>
            Signals will appear here when the AI has ≥ 75% confidence
          </Text>
        </View>
      }
    />
  );
}

const styles = StyleSheet.create({
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  centered: { flex: 1, alignItems: "center", justifyContent: "center", padding: spacing.xxl, minHeight: 300 },
  banner: {
    backgroundColor: colors.indigoBg,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: "rgba(99,102,241,0.3)",
  },
  bannerTitle: { color: colors.text, fontSize: 16, fontWeight: "700" },
  bannerSub: { color: colors.textMuted, fontSize: 13, marginTop: 4 },
  emptyTitle: { color: colors.text, fontSize: 16, fontWeight: "600", textAlign: "center" },
  sub: { color: colors.textMuted, fontSize: 13, marginTop: spacing.sm, textAlign: "center", lineHeight: 20 },
});
