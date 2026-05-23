import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Platform,
} from "react-native";
import { useRouter } from "expo-router";
import { formatDistanceToNow } from "date-fns";
import { colors, radius, spacing } from "@/lib/theme";
import type { Signal } from "@/lib/types";

const SIG_CONFIG = {
  BUY: {
    emoji: "🟢",
    color: colors.buy,
    bg: colors.buyBg,
    border: colors.buyBorder,
  },
  SELL: {
    emoji: "🔴",
    color: colors.sell,
    bg: colors.sellBg,
    border: colors.sellBorder,
  },
  HOLD: {
    emoji: "⚪",
    color: colors.hold,
    bg: colors.holdBg,
    border: colors.holdBorder,
  },
};

const TF_COLOR: Record<string, string> = {
  short: colors.yellow,
  mid: colors.blue,
  long: colors.purple,
};

interface Props {
  signal: Signal;
}

export default function SignalCard({ signal: s }: Props) {
  const router = useRouter();
  const cfg = SIG_CONFIG[s.signal] ?? SIG_CONFIG.HOLD;
  const conf = s.confidence ?? 0;
  const timeAgo = s.created_at
    ? formatDistanceToNow(new Date(s.created_at), { addSuffix: true })
    : "";

  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={() => router.push(`/signal/${s.ticker}`)}
      style={[styles.card, { borderColor: cfg.border, backgroundColor: colors.card }]}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <View style={styles.titleRow}>
            <Text style={styles.ticker}>{s.ticker}</Text>
            <View style={[styles.badge, { backgroundColor: cfg.bg, borderColor: cfg.border }]}>
              <Text style={[styles.badgeText, { color: cfg.color }]}>
                {cfg.emoji} {s.signal}
              </Text>
            </View>
          </View>
          <Text style={styles.exchange}>
            {s.exchange} · {s.asset_type?.toUpperCase()}
          </Text>
        </View>
        <View style={styles.confWrapper}>
          <Text
            style={[
              styles.confNumber,
              {
                color:
                  conf >= 75
                    ? colors.green
                    : conf >= 50
                    ? colors.yellow
                    : colors.textMuted,
              },
            ]}
          >
            {conf}%
          </Text>
          <Text style={styles.confLabel}>confidence</Text>
        </View>
      </View>

      {/* Price levels */}
      {s.signal !== "HOLD" && (
        <View style={styles.priceRow}>
          <View style={[styles.priceBox, { backgroundColor: "rgba(255,255,255,0.04)" }]}>
            <Text style={styles.priceLabel}>Entry</Text>
            <Text style={[styles.priceValue, { color: colors.text }]}>
              {s.entry_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
            </Text>
          </View>
          <View style={[styles.priceBox, { backgroundColor: "rgba(34,197,94,0.08)" }]}>
            <Text style={styles.priceLabel}>Target</Text>
            <Text style={[styles.priceValue, { color: colors.green }]}>
              {s.target_price?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
            </Text>
          </View>
          <View style={[styles.priceBox, { backgroundColor: "rgba(239,68,68,0.08)" }]}>
            <Text style={styles.priceLabel}>Stop</Text>
            <Text style={[styles.priceValue, { color: colors.red }]}>
              {s.stop_loss?.toLocaleString(undefined, { maximumFractionDigits: 4 }) ?? "—"}
            </Text>
          </View>
        </View>
      )}

      {/* Meta row */}
      <View style={styles.metaRow}>
        {s.risk_reward_ratio && (
          <Text style={[styles.metaChip, { color: colors.blue }]}>
            ⚖️ R:R {s.risk_reward_ratio}x
          </Text>
        )}
        {s.timeframe && (
          <Text style={[styles.metaChip, { color: TF_COLOR[s.timeframe] ?? colors.textMuted }]}>
            ⏱ {s.timeframe.toUpperCase()}
          </Text>
        )}
      </View>

      {/* Reasoning */}
      {s.reasoning && (
        <Text style={styles.reasoning} numberOfLines={2}>
          {s.reasoning}
        </Text>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <View style={styles.risks}>
          {(s.key_risks ?? []).slice(0, 1).map((r, i) => (
            <View key={i} style={styles.riskTag}>
              <Text style={styles.riskText} numberOfLines={1}>
                ⚠️ {r.length > 28 ? r.slice(0, 28) + "…" : r}
              </Text>
            </View>
          ))}
        </View>
        <Text style={styles.timeAgo}>{timeAgo}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: radius.lg,
    borderWidth: 1.5,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
      },
      android: { elevation: 4 },
    }),
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: spacing.md,
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    flexWrap: "wrap",
  },
  ticker: {
    fontSize: 20,
    fontWeight: "800",
    color: colors.text,
  },
  badge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.full,
    borderWidth: 1,
  },
  badgeText: { fontSize: 11, fontWeight: "700" },
  exchange: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 2,
  },
  confWrapper: { alignItems: "center" },
  confNumber: { fontSize: 24, fontWeight: "800" },
  confLabel: { fontSize: 10, color: colors.textMuted },

  priceRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  priceBox: {
    flex: 1,
    borderRadius: radius.md,
    padding: spacing.sm,
    alignItems: "center",
  },
  priceLabel: { fontSize: 10, color: colors.textMuted, marginBottom: 2 },
  priceValue: { fontSize: 12, fontFamily: Platform.OS === "ios" ? "Courier" : "monospace", fontWeight: "700" },

  metaRow: {
    flexDirection: "row",
    gap: spacing.md,
    marginBottom: spacing.sm,
  },
  metaChip: { fontSize: 12, fontWeight: "600" },

  reasoning: {
    fontSize: 12,
    color: colors.textMuted,
    lineHeight: 18,
    marginBottom: spacing.sm,
  },

  footer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  risks: { flexDirection: "row", gap: spacing.xs, flex: 1 },
  riskTag: {
    backgroundColor: colors.warningBg,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
  },
  riskText: { fontSize: 10, color: colors.warning },
  timeAgo: { fontSize: 10, color: colors.textFaint },
});
