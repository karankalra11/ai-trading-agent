import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useLocalSearchParams, useNavigation } from "expo-router";
import { api } from "@/lib/api";
import { colors, radius, spacing } from "@/lib/theme";
import type { Signal } from "@/lib/types";
import { formatDistanceToNow } from "date-fns";

const SIG_CONFIG = {
  BUY:  { emoji: "🟢", color: colors.buy,  bg: colors.buyBg,  border: colors.buyBorder  },
  SELL: { emoji: "🔴", color: colors.sell, bg: colors.sellBg, border: colors.sellBorder },
  HOLD: { emoji: "⚪", color: colors.hold, bg: colors.holdBg, border: colors.holdBorder },
};

const TF_COLOR: Record<string, string> = {
  short: colors.yellow,
  mid: colors.blue,
  long: colors.purple,
};

export default function SignalDetailScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const navigation = useNavigation();
  const [signal, setSignal] = useState<Signal | null>(null);
  const [history, setHistory] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (ticker) navigation.setOptions({ title: ticker });
    async function load() {
      try {
        const [sig, hist] = await Promise.all([
          api.signals.latest(ticker!).catch(() => null),
          api.signals.history(ticker!, 10),
        ]);
        setSignal(sig);
        setHistory(hist);
      } finally {
        setLoading(false);
      }
    }
    if (ticker) load();
  }, [ticker, navigation]);

  const triggerRun = async () => {
    try {
      const market = signal?.asset_type === "crypto" ? "crypto"
        : ticker?.endsWith(".NS") || ticker?.endsWith(".BO") ? "india" : "us";
      await api.signals.trigger(ticker!, market);
      Alert.alert("✅ Triggered", `Refreshing signal for ${ticker}…`);
    } catch {
      Alert.alert("❌ Error", "Could not trigger signal run");
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.indigo} />
        <Text style={{ color: colors.textMuted, marginTop: spacing.md }}>
          Loading {ticker}…
        </Text>
      </View>
    );
  }

  const sig = signal?.signal ?? "HOLD";
  const cfg = SIG_CONFIG[sig] ?? SIG_CONFIG.HOLD;
  const conf = signal?.confidence ?? 0;

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>

      {/* Signal banner */}
      {signal ? (
        <View style={[styles.banner, { borderColor: cfg.border, backgroundColor: cfg.bg }]}>
          <View style={styles.bannerTop}>
            <View>
              <View style={styles.bannerTitleRow}>
                <Text style={styles.bannerTicker}>{ticker}</Text>
                <View style={[styles.sigBadge, { backgroundColor: cfg.bg, borderColor: cfg.border }]}>
                  <Text style={[styles.sigBadgeText, { color: cfg.color }]}>
                    {cfg.emoji} {sig}
                  </Text>
                </View>
              </View>
              <Text style={styles.bannerMeta}>
                {signal.exchange} · {signal.asset_type?.toUpperCase()} ·{" "}
                {signal.created_at
                  ? formatDistanceToNow(new Date(signal.created_at), { addSuffix: true })
                  : ""}
              </Text>
            </View>
            <View style={styles.confBlock}>
              <Text style={[styles.confNum, { color: conf >= 75 ? colors.green : conf >= 50 ? colors.yellow : colors.textMuted }]}>
                {conf}%
              </Text>
              <Text style={styles.confLabel}>confidence</Text>
            </View>
          </View>

          {/* Price levels */}
          {sig !== "HOLD" && (
            <View style={styles.priceRow}>
              {[
                { label: "Entry", value: signal.entry_price, color: colors.blue },
                { label: "Target", value: signal.target_price, color: colors.green },
                { label: "Stop Loss", value: signal.stop_loss, color: colors.red },
              ].map((p) => (
                <View key={p.label} style={styles.priceBox}>
                  <Text style={styles.priceLabel}>{p.label}</Text>
                  <Text style={[styles.priceVal, { color: p.color }]}>
                    {p.value?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
                  </Text>
                </View>
              ))}
            </View>
          )}

          {/* Meta */}
          <View style={styles.metaRow}>
            {signal.risk_reward_ratio && (
              <Text style={[styles.metaChip, { color: colors.blue }]}>⚖️ R:R {signal.risk_reward_ratio}x</Text>
            )}
            {signal.timeframe && (
              <Text style={[styles.metaChip, { color: TF_COLOR[signal.timeframe] ?? colors.textMuted }]}>
                ⏱ {signal.timeframe.toUpperCase()} TERM
              </Text>
            )}
            {(signal.data_sources ?? []).map((s) => (
              <View key={s} style={styles.sourceChip}>
                <Text style={styles.sourceChipText}>{s}</Text>
              </View>
            ))}
          </View>

          {/* Reasoning */}
          {signal.reasoning && (
            <View style={styles.reasoningBox}>
              <Text style={styles.reasoningText}>💬 {signal.reasoning}</Text>
            </View>
          )}

          {/* Key risks */}
          {(signal.key_risks ?? []).length > 0 && (
            <View style={styles.risksRow}>
              {(signal.key_risks ?? []).map((r, i) => (
                <View key={i} style={styles.riskTag}>
                  <Text style={styles.riskText}>⚠️ {r}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      ) : (
        <View style={[styles.banner, { borderColor: colors.border }]}>
          <Text style={styles.noSignalText}>No signals found for {ticker}</Text>
        </View>
      )}

      {/* Trigger button */}
      <TouchableOpacity style={styles.triggerBtn} onPress={triggerRun}>
        <Text style={styles.triggerBtnText}>▶ Refresh Signal Now</Text>
      </TouchableOpacity>

      {/* Signal history */}
      {history.length > 0 && (
        <View style={styles.historySection}>
          <Text style={styles.historyTitle}>Signal History</Text>
          {history.map((s) => {
            const hcfg = SIG_CONFIG[s.signal] ?? SIG_CONFIG.HOLD;
            return (
              <View key={s.id} style={styles.historyRow}>
                <View style={[styles.histBadge, { backgroundColor: hcfg.bg, borderColor: hcfg.border }]}>
                  <Text style={[styles.histBadgeText, { color: hcfg.color }]}>{s.signal}</Text>
                </View>
                <View style={styles.histInfo}>
                  <Text style={styles.histMeta}>
                    {s.created_at ? new Date(s.created_at).toLocaleString() : "—"}
                  </Text>
                  <Text style={styles.histPrices}>
                    Entry:{" "}
                    <Text style={{ color: colors.blue }}>
                      {s.entry_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
                    </Text>
                    {"  "}Target:{" "}
                    <Text style={{ color: colors.green }}>
                      {s.target_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
                    </Text>
                  </Text>
                </View>
                <Text style={[styles.histConf, { color: (s.confidence ?? 0) >= 75 ? colors.green : colors.yellow }]}>
                  {s.confidence}%
                </Text>
              </View>
            );
          })}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: colors.bg },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  centered: { flex: 1, alignItems: "center", justifyContent: "center", padding: spacing.xxl },

  banner: {
    borderRadius: radius.xl,
    borderWidth: 1.5,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  bannerTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", marginBottom: spacing.md },
  bannerTitleRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, flexWrap: "wrap" },
  bannerTicker: { fontSize: 28, fontWeight: "800", color: colors.text },
  sigBadge: { paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: radius.full, borderWidth: 1 },
  sigBadgeText: { fontSize: 13, fontWeight: "700" },
  bannerMeta: { color: colors.textMuted, fontSize: 12, marginTop: 4 },
  confBlock: { alignItems: "center" },
  confNum: { fontSize: 40, fontWeight: "800" },
  confLabel: { color: colors.textMuted, fontSize: 11 },

  priceRow: { flexDirection: "row", gap: spacing.sm, marginBottom: spacing.md },
  priceBox: { flex: 1, backgroundColor: "rgba(255,255,255,0.05)", borderRadius: radius.md, padding: spacing.md, alignItems: "center" },
  priceLabel: { color: colors.textMuted, fontSize: 11, marginBottom: 4 },
  priceVal: { fontSize: 14, fontFamily: "monospace", fontWeight: "700" },

  metaRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.md },
  metaChip: { fontSize: 13, fontWeight: "600" },
  sourceChip: { backgroundColor: "rgba(255,255,255,0.06)", borderRadius: radius.sm, paddingHorizontal: spacing.sm, paddingVertical: 2 },
  sourceChipText: { color: colors.textMuted, fontSize: 11 },

  reasoningBox: { backgroundColor: "rgba(255,255,255,0.05)", borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.sm },
  reasoningText: { color: colors.text, fontSize: 13, lineHeight: 20 },

  risksRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  riskTag: { backgroundColor: colors.warningBg, borderRadius: radius.sm, paddingHorizontal: spacing.sm, paddingVertical: 4 },
  riskText: { color: colors.warning, fontSize: 12 },

  noSignalText: { color: colors.textMuted, fontSize: 15, textAlign: "center" },

  triggerBtn: {
    backgroundColor: colors.indigo,
    borderRadius: radius.lg,
    paddingVertical: spacing.md,
    alignItems: "center",
    marginBottom: spacing.xl,
  },
  triggerBtnText: { color: "#fff", fontSize: 15, fontWeight: "700" },

  historySection: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  historyTitle: { color: colors.text, fontSize: 16, fontWeight: "700", marginBottom: spacing.md },
  historyRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    gap: spacing.sm,
  },
  histBadge: { paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: radius.sm, borderWidth: 1, minWidth: 50, alignItems: "center" },
  histBadgeText: { fontSize: 11, fontWeight: "700" },
  histInfo: { flex: 1 },
  histMeta: { color: colors.textMuted, fontSize: 11 },
  histPrices: { color: colors.textMuted, fontSize: 12, marginTop: 2 },
  histConf: { fontSize: 14, fontWeight: "700" },
});
