# Web Export Guide

Godot 4.6 Web (HTML5) 匯出完整指南。

## 前置條件

- Godot 4.6.1（已確認使用 `gl_compatibility` 渲染器，Web 唯一支援）
- `export_presets.cfg` 已建立於專案根目錄

## 1. 安裝 Export Templates

### 方法 A：透過 Editor UI

1. 開啟 Godot Editor
2. 選單 → **Editor → Manage Export Templates**
3. 點擊 **Download and Install**
4. 等待下載完成（約 500MB）

安裝位置：`~/Library/Application Support/Godot/export_templates/4.6.1.stable/`

### 方法 B：手動下載

1. 從 [Godot 官方下載頁](https://godotengine.org/download) 下載對應版本的 Export Templates（`.tpz` 檔案）
2. 將 `.tpz` 重新命名為 `.zip` 並解壓
3. 將 `templates/` 內容複製到：
   ```
   ~/Library/Application Support/Godot/export_templates/4.6.1.stable/
   ```
4. 確認 `web_release.zip` 和 `web_debug.zip` 存在於該目錄

## 2. export_presets.cfg 配置

專案根目錄已包含 `export_presets.cfg`，主要設定：

| 參數 | 值 | 說明 |
|------|-----|------|
| `name` | `"Web"` | Preset 名稱，命令列匯出時使用 |
| `platform` | `"Web"` | 匯出平台 |
| `export_path` | `"./export/index.html"` | 匯出檔案路徑 |
| `vram_texture_compression/for_desktop` | `true` | 桌面端紋理壓縮 |
| `html/canvas_resize_policy` | `2` | Canvas 自適應大小 |
| `html/focus_canvas_on_start` | `true` | 載入後自動聚焦 |

如需修改，建議在 Godot Editor 中操作：**Project → Export → Web**。

## 3. 命令列匯出

```bash
# Release 版本
/Applications/Godot.app/Contents/MacOS/Godot --headless --export-release "Web" ./export/index.html

# Debug 版本
/Applications/Godot.app/Contents/MacOS/Godot --headless --export-debug "Web" ./export/index.html
```

匯出產物會出現在 `export/` 目錄，包含：
- `index.html` — 入口頁面
- `index.js` — Godot 引擎載入器
- `index.wasm` — WebAssembly 二進位
- `index.pck` — 遊戲資源封包
- `index.icon.png` — favicon

## 4. 本地測試

Web 匯出必須透過 HTTP Server 提供服務（不能直接開啟 HTML）。SharedArrayBuffer 需要 COOP/COEP headers。

### 使用 Python

```bash
cd export/
python3 -c "
from http.server import HTTPServer, SimpleHTTPRequestHandler
class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        super().end_headers()
HTTPServer(('localhost', 8060), Handler).serve_forever()
"
```

開啟瀏覽器訪問 `http://localhost:8060`。

### 使用 npx

```bash
npx serve export/ --cors -l 8060
```

> 注意：`npx serve` 不會自動加上 COOP/COEP headers。如果遊戲使用 SharedArrayBuffer（多執行緒），必須用 Python 方案或自行配置 headers。

## 5. 部署到 itch.io

### 步驟

1. 在 [itch.io](https://itch.io) 建立新專案，類型選 **HTML**
2. 將 `export/` 目錄內所有檔案打包成 `.zip`：
   ```bash
   cd export/ && zip -r ../candy-crush-web.zip . && cd ..
   ```
3. 上傳 `candy-crush-web.zip` 到 itch.io
4. 勾選 **This file will be played in the browser**
5. 設定嵌入尺寸為 **1280 x 720**（與 viewport 一致）
6. 勾選 **SharedArrayBuffer support**（itch.io 會自動處理 COOP/COEP headers）

### 使用 butler（CLI 工具）

```bash
# 安裝 butler
# https://itch.io/docs/butler/

# 推送到 itch.io
butler push export/ your-username/candy-crush:html5
```

## 常見問題

### 匯出失敗：找不到 Export Template
確認 `~/Library/Application Support/Godot/export_templates/4.6.1.stable/` 目錄存在且包含 `web_release.zip`。

### 畫面空白或黑屏
- 確認渲染器為 `gl_compatibility`（`project.godot` 中 `renderer/rendering_method`）
- 檢查瀏覽器 Console 是否有 WebGL 錯誤
- 確認 COOP/COEP headers 正確設定

### 載入卡在 logo 畫面
通常是 `.pck` 檔案未正確載入。確認所有匯出檔案在同一目錄，且 HTTP Server 能正確提供這些檔案。
