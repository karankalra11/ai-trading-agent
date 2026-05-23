import React, { useState } from "react";
import {
  View,
  FlatList,
  Text,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { useSignals } from "@/hooks/useSignals";
import SignalCard from "@/components/SignalCard";
import StatBar from "@/components/StatBar";
import { MarketFilter, SignalFilter, MARKET_TABS } from "@/components/FilterTabs";
import { colors, spacing } from "@/lib/theme";
import type { Signal } from "@/lib/types";

export default function SignalsScreen() {
  const [marketTab, setMarketTab] = useState("");
  const [signalFilter, setSignalFilter] = useState("");

  const marketCfg = MARKET_TABS.find((t) => t.key === marketTab);

  const { signals, loading, error, lastUpdated, refetch } = useSignals({
    // @ts-expect-error dynamic
    asset_type: marketCfg?.assetType,
    signal_type: signalFilter || undefined,
  });

  const buy = signals.filter((s) => s.signal === "BUY").length;
  const sell = signals.filter((s) => s.signal === "SELL").length;
  const hold = signals.filter((s) => s.signal === "HOLD").length;

  if (loading && signals.length === 0) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.indigo} />
        <Text style={styles.loadingText}>Loading signals…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorEmoji}>⚠️</Text>
        <Text style={styles.errorText}>{error}</Text>
        <Text style={styles.errorHint}>
          Make sure the backend is running and EXPO_PUBLIC_API_URL is set
        </Text>
      </View>
    );
  }

  return (
    <FlatList
      style={styles.list}
      contentContainerStyle={styles.content}
      data={signals}
      keyExtractor={(s: Signal) => String(s.id)}
      renderItem={({ item }) => <SignalCard signal={item} />}
      refreshControl={
        <RefreshControl
          refreshing={loading}
          onRefresh={refetch}
          tintColor={colors.indigo}
          colors={[colors.indigo]}
        />
      }
      ListHeaderComponent={
        <View>
          <StatBar buy={buy} sell={sell} hold={hold} />
          <MarketFilter active={marketTab} onChange={setMarketTab} />
          <SignalFilter active={signalFilter} onChange={setSignalFilter} />
          {lastUpdated && (
            <Text style={styles.updated}>
              Updated {lastUpdated.toLocaleTimeString()}
            </Text>
          )}
        </View>
      }
      ListEmptyComponent={
        <View style={styles.centered}>
          <Text style={styles.errorEmoji}>🔍</Text>
          <Text style={styles.errorText}>No signals yet</Text>
          <Text style={styles.errorHint}>
            Pull to refresh or run{"\n"}
            <Text style={styles.code}>python run_signal.py AAPL</Text>
            {"\n"}in the backend
          </Text>
        </View>
      }
    />
  );
}

const styles = StyleSheet.create({
  list: { flex: 1, backgroundColor: colors.bg },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  centered: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: spacing.xxl,
    minHeight: 300,
  },
  loadingText: { color: colors.textMuted, marginTop: spacing.md, fontSize: 14 },
  errorEmoji: { fontSize: 40, marginBottom: spacing.md },
  errorText: { color: colors.text, fontSize: 16, fontWeight: "600", textAlign: "center" },
  errorHint: {
    color: colors.textMuted,
    fontSize: 13,
    marginTop: spacing.sm,
    textAlign: "center",
    lineHeight: 20,
  },
  code: {
    fontFamily: "monospace",
    backgroundColor: "rgba(255,255,255,0.1)",
    color: colors.indigo,
  },
  updated: {
    color: colors.textMuted,
    fontSize: 11,
    marginBottom: spacing.md,
    textAlign: "right",
  },
});
