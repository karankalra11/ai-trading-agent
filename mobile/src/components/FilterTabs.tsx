import React from "react";
import {
  ScrollView,
  TouchableOpacity,
  Text,
  StyleSheet,
  View,
} from "react-native";
import { colors, radius, spacing } from "@/lib/theme";

export const MARKET_TABS = [
  { key: "", label: "🌍 All" },
  { key: "stock", label: "📈 Stocks", assetType: "stock" },
  { key: "crypto", label: "₿ Crypto", assetType: "crypto" },
  { key: "etf", label: "📦 ETFs", assetType: "etf" },
];

export const SIGNAL_TABS = ["ALL", "BUY", "SELL", "HOLD"];

interface MarketFilterProps {
  active: string;
  onChange: (key: string) => void;
}

export function MarketFilter({ active, onChange }: MarketFilterProps) {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      style={{ marginBottom: spacing.md }}
      contentContainerStyle={{ gap: spacing.sm }}
    >
      {MARKET_TABS.map((tab) => (
        <TouchableOpacity
          key={tab.key}
          onPress={() => onChange(tab.key)}
          style={[
            styles.tab,
            active === tab.key ? styles.tabActive : styles.tabInactive,
          ]}
        >
          <Text
            style={[
              styles.tabText,
              { color: active === tab.key ? "#fff" : colors.textMuted },
            ]}
          >
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

interface SignalFilterProps {
  active: string;
  onChange: (sig: string) => void;
}

export function SignalFilter({ active, onChange }: SignalFilterProps) {
  return (
    <View style={styles.sigRow}>
      {SIGNAL_TABS.map((sig) => (
        <TouchableOpacity
          key={sig}
          onPress={() => onChange(sig === "ALL" ? "" : sig)}
          style={[
            styles.sigTab,
            (sig === "ALL" ? active === "" : active === sig)
              ? styles.sigTabActive
              : styles.sigTabInactive,
          ]}
        >
          <Text
            style={[
              styles.sigText,
              {
                color:
                  (sig === "ALL" ? active === "" : active === sig)
                    ? "#fff"
                    : colors.textMuted,
              },
            ]}
          >
            {sig}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  tab: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: radius.full,
  },
  tabActive: {
    backgroundColor: colors.indigo,
  },
  tabInactive: {
    backgroundColor: "rgba(255,255,255,0.06)",
  },
  tabText: { fontSize: 13, fontWeight: "600" },

  sigRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  sigTab: {
    flex: 1,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    alignItems: "center",
  },
  sigTabActive: { backgroundColor: colors.indigo },
  sigTabInactive: { backgroundColor: "rgba(255,255,255,0.06)" },
  sigText: { fontSize: 12, fontWeight: "700" },
});
