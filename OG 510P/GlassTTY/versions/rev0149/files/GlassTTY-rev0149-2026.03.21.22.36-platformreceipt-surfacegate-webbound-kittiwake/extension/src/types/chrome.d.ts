declare namespace chrome {
  namespace runtime {
    interface Port {
      postMessage(message: unknown): void;
      onMessage: { addListener(listener: (message: unknown) => void): void };
      onDisconnect: { addListener(listener: () => void): void };
    }
    interface MessageSender {
      tab?: tabs.Tab;
      documentId?: string;
      documentLifecycle?: string;
      frameId?: number;
      id?: string;
      nativeApplication?: string;
      origin?: string;
      url?: string;
      documentUrl?: string;
    }
    interface ExtensionContext {
      contextId?: string;
      contextType: string;
      documentId?: string;
      documentUrl?: string;
      documentOrigin?: string;
      tabId?: number;
      windowId?: number;
      frameId?: number;
      incognito?: boolean;
    }
    const lastError: { message?: string } | undefined;
    const id: string;
    function getManifest(): { version: string; minimum_chrome_version?: string; permissions?: string[]; host_permissions?: string[] };
    function getContexts(filter?: object): Promise<ExtensionContext[]>;
    function getURL(path: string): string;
    function connectNative(name: string): Port;
    function sendNativeMessage(application: string, message: unknown): Promise<unknown>;
    function sendMessage(message: unknown): Promise<unknown>;
    const onInstalled: { addListener(listener: () => void): void };
    const onStartup: { addListener(listener: () => void): void };
    const onSuspend: { addListener(listener: () => void): void };
    const onMessage: { addListener(listener: (message: any, sender: MessageSender, sendResponse: (response?: unknown) => void) => boolean | void): void };
  }
  namespace tabs {
    interface Tab {
      id?: number;
      url?: string;
      windowId?: number;
      active?: boolean;
      title?: string;
      discarded?: boolean;
      frozen?: boolean;
      status?: string;
      pendingUrl?: string;
    }
    interface SendMessageOptions {
      documentId?: string;
      frameId?: number;
    }
    function query(queryInfo: { active?: boolean; currentWindow?: boolean; lastFocusedWindow?: boolean; discarded?: boolean; frozen?: boolean }): Promise<Tab[]>;
    function sendMessage(tabId: number, message: unknown, options?: SendMessageOptions): Promise<unknown>;
    const onActivated: { addListener(listener: (info: { tabId: number; windowId: number }) => void): void };
    const onUpdated: { addListener(listener: (tabId: number, changeInfo: { status?: string; discarded?: boolean; frozen?: boolean; url?: string }, tab: Tab) => void): void };
    const onRemoved: { addListener(listener: (tabId: number) => void): void };
    function get(tabId: number): Promise<Tab>;
    function create(createProperties: { url?: string; active?: boolean; windowId?: number }): Promise<Tab>;
  }
  namespace commands {
    const onCommand: { addListener(listener: (command: string) => void): void };
  }
  namespace action {
    function setBadgeText(details: { text: string; tabId?: number }): Promise<void>;
    function setBadgeBackgroundColor(details: { color: string; tabId?: number }): Promise<void>;
    function setTitle(details: { title: string; tabId?: number }): Promise<void>;
  }
  namespace contextMenus {
    type ContextType = 'action' | 'page' | 'selection';
    interface OnClickData {
      menuItemId: string | number;
      selectionText?: string;
      pageUrl?: string;
    }
    function create(properties: {
      id?: string;
      title: string;
      contexts?: ContextType[];
      documentUrlPatterns?: string[];
    }): void;
    function removeAll(callback?: () => void): void;
    const onClicked: { addListener(listener: (info: OnClickData, tab?: tabs.Tab) => void): void };
  }
  namespace sidePanel {
    function setPanelBehavior(options: { openPanelOnActionClick: boolean }): Promise<void>;
    function setOptions(options: { tabId?: number; path?: string; enabled?: boolean }): Promise<void>;
    function open(options: { tabId?: number; windowId?: number }): Promise<void>;
  }

  namespace webNavigation {
    interface FrameDetails {
      documentId?: string;
      documentLifecycle?: string;
      frameId: number;
      frameType?: string;
      parentDocumentId?: string;
      parentFrameId?: number;
      tabId: number;
      url?: string;
    }
    type GetAllFramesResultDetails = FrameDetails;
    function getAllFrames(details: { tabId: number }): Promise<GetAllFramesResultDetails[] | undefined>;
    const onCommitted: { addListener(listener: (details: FrameDetails) => void): void };
    const onHistoryStateUpdated: { addListener(listener: (details: FrameDetails) => void): void };
    const onReferenceFragmentUpdated: { addListener(listener: (details: FrameDetails) => void): void };
  }
  namespace scripting {
    interface InjectionTarget {
      tabId: number;
      frameIds?: number[];
      documentIds?: string[];
      allFrames?: boolean;
    }
    function executeScript(options: { target: InjectionTarget; files?: string[] }): Promise<Array<{ frameId: number; result?: unknown }>>;
  }
namespace offscreen {
  type Reason = 'TESTING' | 'AUDIO_PLAYBACK' | 'IFRAME_SCRIPTING' | 'DOM_SCRAPING' | 'BLOBS' | 'DOM_PARSER' | 'USER_MEDIA' | 'DISPLAY_MEDIA' | 'WEB_RTC' | 'CLIPBOARD' | 'LOCAL_STORAGE' | 'WORKERS' | 'BATTERY_STATUS' | 'MATCH_MEDIA' | 'GEOLOCATION';
  function createDocument(options: { url: string; reasons: Reason[]; justification: string }): Promise<void>;
  function closeDocument(): Promise<void>;
}
namespace alarms {
    interface Alarm {
      name: string;
      scheduledTime: number;
      periodInMinutes?: number;
    }
    function create(name: string, alarmInfo: { delayInMinutes?: number; periodInMinutes?: number }): Promise<void>;
    function clear(name: string): Promise<boolean>;
    function get(name: string): Promise<Alarm | undefined>;
    const onAlarm: { addListener(listener: (alarm: Alarm) => void): void };
  }
  namespace storage {
    type AccessLevel = 'TRUSTED_CONTEXTS' | 'TRUSTED_AND_UNTRUSTED_CONTEXTS';
    namespace local {
      function get(keys?: string | string[] | object | null): Promise<Record<string, unknown>>;
      function set(items: Record<string, unknown>): Promise<void>;
      function setAccessLevel(options: { accessLevel: AccessLevel }): Promise<void>;
    }
    namespace session {
      function get(keys?: string | string[] | object | null): Promise<Record<string, unknown>>;
      function set(items: Record<string, unknown>): Promise<void>;
      function remove(keys: string | string[]): Promise<void>;
      function setAccessLevel(options: { accessLevel: AccessLevel }): Promise<void>;
    }
    const onChanged: { addListener(listener: (changes: Record<string, { oldValue?: unknown; newValue?: unknown }>, areaName: string) => void): void };
  }
}
