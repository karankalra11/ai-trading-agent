import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { View } from "react-native";
import { colors } from "@/lib/theme";

export default function RootLayout() {
  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar style="light" backgroundColor={colors.bg} />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: colors.card },
          headerTintColor: colors.text,
          headerTitleStyle: { fontWeight: "700", color: colors.text },
          contentStyle: { backgroundColor: colors.bg },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen
          name="signal/[ticker]"
          options={{ title: "Signal Detail", headerBackTitle: "Back" }}
        />
      </Stack>
    </View>
  );
}
