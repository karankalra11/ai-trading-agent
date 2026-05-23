import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { colors, radius, spacing } from "@/lib/theme";
import { API_BASE_URL } from "@/lib/config";

export default function SettingsScreen() {
  const [apiUrl, setApiUrl] = useState(API_BASE_URL);
  const [status, setStatus] = useState<"idle" | "checking" | "ok" | "error">("idle");
  const [statusMsg, setStatusMsg] = useState("");

  useEffect(() => {
    AsyncStorage.getItem("api_url").then((v) => {
      if (v) setApiUrl(v);
    });
  }, []);

  const saveUrl = async () => {
    await AsyncStorage.setItem("api_url", apiUrl);
    Alert.alert("✅ Saved", "Restart the app for URL changes to take effect.");
  };

  const checkHealth = async () => {
    setStatus("checking");
    try {
      const res = await fetch(`${apiUrl}/health`, { signal: AbortSignal.timeout(5000) });
      const data = await res.json();
      setStatus("ok");
      setStatusMsg(data.status === "ok" ? "Backend is online ✅" : "Unexpected response");
    } catch {
      setStatus("error");
      setStatusMsg("Cannot reach backend ❌");
    }
  };

  const triggerSignal = async (ticker: string, market: string) => {
    try {
      await fetch(`${apiUrl}/api/signals/trigger?ticker=${ticker}&market=${market}`, {
        method: "POST",
      });
      Alert.alert("✅ Triggered", `Signal run started for ${ticker}`);
    } catch {
      Alert.alert("❌ Error", "Could not trigger signal run");
    }
  };

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: colors.bg }}
      contentContainerStyle={styles.content}
    >
      {/* Backend URL */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Backend URL</Text>
        <Text style={styles.sectionSub}>
          Point to your Render URL or local server
        </Text>
        <TextInput
          style={styles.input}
          value={apiUrl}
          onChangeText={setApiUrl}
          placeholder="https://your-app.onrender.com"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
        />
        <View style={styles.buttonRow}>
          <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={saveUrl}>
            <Text style={styles.btnTextPrimary}>Save URL</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnSecondary]} onPress={checkHealth}>
            {status === "checking" ? (
              <ActivityIndicator size="small" color={colors.indigo} />
            ) : (
              <Text style={styles.btnTextSecondary}>Check Health</Text>
            )}
          </TouchableOpacity>
        </View>
        {statusMsg ? (
          <Text style={[styles.statusMsg, { color: status === "ok" ? colors.green : colors.red }]}>
            {statusMsg}
          </Text>
        ) : null}
      </View>

      {/* Manual triggers */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Manual Signal Triggers</Text>
        <Text style={styles.sectionSub}>Force a signal run without waiting for the scheduler</Text>
        {[
          { label: "🇺🇸 AAPL", ticker: "AAPL", market: "us" },
          { label: "🇺🇸 NVDA", ticker: "NVDA", market: "us" },
          { label: "₿ BTC", ticker: "BTC", market: "crypto" },
          { label: "₿ ETH", ticker: "ETH", market: "crypto" },
          { label: "🇮🇳 TCS", ticker: "TCS.NS", market: "india" },
          { label: "🇮🇳 RELIANCE", ticker: "RELIANCE.NS", market: "india" },
        ].map((item) => (
          <TouchableOpacity
            key={item.ticker}
            style={styles.triggerRow}
            onPress={() => triggerSignal(item.ticker, item.market)}
          >
            <Text style={styles.triggerLabel}>{item.label}</Text>
            <Text style={styles.triggerArrow}>▶ Run</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <Text style={styles.infoText}>
          AI Trading Agent v1.0{"\n"}
          Powered by Claude AI + FinBERT/VADER Sentiment{"\n"}
          Data: yfinance · CoinGecko · Google News RSS{"\n"}
          Signals auto-refresh every 60 seconds
        </Text>
        <Text style={[styles.infoText, { color: colors.red, marginTop: spacing.md }]}>
          ⚠️ Disclaimer: This app provides AI-generated signals for informational purposes only.
          Not financial advice. Always do your own research before investing.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  section: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sectionTitle: { color: colors.text, fontSize: 16, fontWeight: "700", marginBottom: 4 },
  sectionSub: { color: colors.textMuted, fontSize: 12, marginBottom: spacing.md },
  input: {
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.text,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm + 2,
    fontSize: 13,
    fontFamily: "monospace",
    marginBottom: spacing.md,
  },
  buttonRow: { flexDirection: "row", gap: spacing.sm },
  btn: {
    flex: 1,
    paddingVertical: spacing.sm + 2,
    borderRadius: radius.md,
    alignItems: "center",
  },
  btnPrimary: { backgroundColor: colors.indigo },
  btnSecondary: {
    backgroundColor: "rgba(255,255,255,0.06)",
    borderWidth: 1,
    borderColor: colors.border,
  },
  btnTextPrimary: { color: "#fff", fontWeight: "700", fontSize: 14 },
  btnTextSecondary: { color: colors.textMuted, fontWeight: "600", fontSize: 14 },
  statusMsg: { marginTop: spacing.sm, fontSize: 13, fontWeight: "600", textAlign: "center" },

  triggerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  triggerLabel: { color: colors.text, fontSize: 14, fontWeight: "600" },
  triggerArrow: { color: colors.indigo, fontSize: 13, fontWeight: "700" },

  infoText: { color: colors.textMuted, fontSize: 12, lineHeight: 20 },
});
