import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "@/lib/theme";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarStyle: {
          backgroundColor: colors.card,
          borderTopColor: colors.border,
          borderTopWidth: 1,
        },
        tabBarActiveTintColor: colors.indigo,
        tabBarInactiveTintColor: colors.textMuted,
        headerStyle: { backgroundColor: colors.bg },
        headerTintColor: colors.text,
        headerTitleStyle: { fontWeight: "800" },
        contentStyle: { backgroundColor: colors.bg },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Signals",
          headerTitle: "📈 AI Trading Agent",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="trending-up" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="alerts"
        options={{
          title: "Alerts",
          headerTitle: "🔔 High-Confidence Alerts",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="notifications" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: "Settings",
          headerTitle: "⚙️ Settings",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="settings-outline" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
