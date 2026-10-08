declare namespace chrome {
  namespace runtime {
    interface Port {
      postMessage(message: unknown): void;
      onMessage: { addListener(listener: (message: unknown) => void): void };
      onDisconnect: { addListener(listener: () => void): void };
    }
    interface MessageSender { tab?: tabs.Tab }
    const lastError: { message?: string } | undefined;
    function connectNative(name: string): Port;
    function sendMessage(message: unknown): Promise<unknown>;
    const onInstalled: { addListener(listener: () => void): void };
    const onStartup: { addListener(listener: () => void): void };
    const onMessage: { addListener(listener: (message: any, sender: MessageSender, sendResponse: (response?: unknown) => void) => boolean | void): void };
  }
  namespace tabs {
    interface Tab { id?: number; url?: string; windowId?: number }
    function query(queryInfo: { active?: boolean; currentWindow?: boolean }): Promise<Tab[]>;
    function sendMessage(tabId: number, message: unknown): Promise<unknown>;
    const onActivated: { addListener(listener: (info: { tabId: number; windowId: number }) => void): void };
    const onUpdated: { addListener(listener: (tabId: number, changeInfo: { status?: string }, tab: Tab) => void): void };
    function get(tabId: number): Promise<Tab>;
  }
  namespace commands {
    const onCommand: { addListener(listener: (command: string) => void): void };
  }
  namespace action {
    function setBadgeText(details: { text: string }): Promise<void>;
  }
  namespace sidePanel {
    function setPanelBehavior(options: { openPanelOnActionClick: boolean }): Promise<void>;
  }
  namespace storage {
    namespace local {
      function get(keys?: string | string[] | object | null): Promise<Record<string, unknown>>;
      function set(items: Record<string, unknown>): Promise<void>;
    }
    const onChanged: { addListener(listener: (changes: Record<string, { oldValue?: unknown; newValue?: unknown }>, areaName: string) => void): void };
  }
}
