import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, radius, spacing } from "@/lib/theme";

interface Props {
  buy: number;
  sell: number;
  hold: number;
}

export default function StatBar({ buy, sell, hold }: Props) {
  return (
    <View style={styles.row}>
      {[
        { label: "BUY", count: buy, color: colors.buy, bg: colors.buyBg },
        { label: "SELL", count: sell, color: colors.sell, bg: colors.sellBg },
        { label: "HOLD", count: hold, color: colors.hold, bg: colors.holdBg },
      ].map((s) => (
        <View
          key={s.label}
          style={[styles.box, { backgroundColor: s.bg }]}
        >
          <Text style={[styles.count, { color: s.color }]}>{s.count}</Text>
          <Text style={styles.label}>{s.label}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  box: {
    flex: 1,
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: "center",
  },
  count: { fontSize: 28, fontWeight: "800" },
  label: { fontSize: 11, color: colors.textMuted, marginTop: 2 },
});
